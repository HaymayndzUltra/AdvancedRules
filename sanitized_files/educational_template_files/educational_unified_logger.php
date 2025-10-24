<?php
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);
ini_set('error_log', 'educational_php_errors.log');

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Method not allowed']);
    exit();
}

$input = file_get_contents('php://input');
$fingerprint_data = json_decode($input, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    error_log("educational_unified_logger.php: JSON Decode Error: " . json_last_error_msg());
    echo json_encode(['status' => 'error', 'message' => 'Invalid JSON data']);
    exit();
}

if (empty($fingerprint_data) || !isset($fingerprint_data['sessionId'])) {
    error_log("educational_unified_logger.php: Missing fingerprint data or sessionId.");
    echo json_encode(['status' => 'error', 'message' => 'Missing fingerprint data or sessionId']);
    exit();
}

$session_id = $fingerprint_data['sessionId'];
$sessions_dir = '../../educational_sessions';
$session_dir = $sessions_dir . '/' . $session_id;

// Ensure sessions directory exists
if (!is_dir($sessions_dir)) {
    if (!mkdir($sessions_dir, 0755, true)) {
        error_log("educational_unified_logger.php: Failed to create educational sessions directory");
        echo json_encode(['status' => 'error', 'message' => 'Failed to create educational sessions directory']);
        exit();
    }
}

// Ensure session-specific directory exists
if (!is_dir($session_dir)) {
    if (!mkdir($session_dir, 0755, true)) {
        error_log("educational_unified_logger.php: Failed to create educational session directory for ID: " . $session_id);
        echo json_encode(['status' => 'error', 'message' => 'Failed to create educational session directory']);
        exit();
    }
}

$fingerprint_file = $session_dir . '/educational_fingerprint.json';

// Store the full fingerprint data with additional metadata
$fingerprint_data['server_timestamp'] = date("Y-m-d H:i:s");
$fingerprint_data['server_ip'] = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$fingerprint_data['server_user_agent'] = $_SERVER['HTTP_USER_AGENT'] ?? 'unknown';

if (file_put_contents($fingerprint_file, json_encode($fingerprint_data, JSON_PRETTY_PRINT)) === false) {
    error_log("CRITICAL: Failed to write educational_fingerprint.json for session: " . $session_id);
    echo json_encode(['status' => 'error', 'message' => 'Failed to save educational fingerprint data']);
    exit();
}

// Update metadata to reflect fingerprint capture status
$metadata_file = $session_dir . '/educational_metadata.json';
$metadata_data = [];
if (file_exists($metadata_file)) {
    $existing_metadata = file_get_contents($metadata_file);
    if ($existing_metadata !== false) {
        $metadata_data = json_decode($existing_metadata, true) ?: [];
    }
}

$metadata_data['educational_fingerprint_captured'] = true;
$metadata_data['educational_fingerprint_capture_time'] = date("Y-m-d H:i:s");
$metadata_data['educational_fingerprint_categories'] = count($fingerprint_data);
$metadata_data['last_update'] = date("Y-m-d H:i:s");

if (file_put_contents($metadata_file, json_encode($metadata_data, JSON_PRETTY_PRINT)) === false) {
    error_log("WARNING: Failed to update educational_metadata.json for session: " . $session_id);
}

// Log successful capture
error_log("educational_unified_logger.php: Successfully saved educational fingerprint for session: " . $session_id . " with " . count($fingerprint_data) . " categories");

echo json_encode([
    'status' => 'success', 
    'message' => 'Educational fingerprint data saved', 
    'session_id' => $session_id,
    'categories_captured' => count($fingerprint_data),
    'timestamp' => date("Y-m-d H:i:s")
]);
?>
