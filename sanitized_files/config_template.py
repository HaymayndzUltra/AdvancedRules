# Educational Security Research Configuration
# Update these values with your actual credentials

# DataImpulse Mobile Proxy Credentials
DATAIMPULSE_USERNAME = "ae9bd5562646a8d33a7e"  # Replace with your username
DATAIMPULSE_PASSWORD = "5faeb42127544013"      # Replace with your password

# File Paths
SESSIONS_FILE = "/home/user/.site/sessions.json"
BROWSER_DATA_DIR = "/home/user/.browser_sessions"

# Browser Settings
HEADLESS_MODE = False  # Set True for background operation
VERIFY_FINGERPRINT = True  # Test at browserleaks.com
AUTO_LOGIN = True  # Automatically attempt login

# Monitoring Settings
CHECK_INTERVAL = 2  # Seconds between file checks
TRIGGER_ON_ATTEMPT = 3  # Which credential attempt triggers automation

# Advanced Settings
PROXY_TIMEOUT = 30  # Proxy connection timeout in seconds
LOGIN_TIMEOUT = 30  # Login attempt timeout in seconds
SCREENSHOT_ON_ERROR = True  # Take screenshots on errors
VERBOSE_LOGGING = False  # Enable debug logging

# Security Settings
MAX_RETRY_ATTEMPTS = 3  # Maximum retry attempts for failed operations
RETRY_DELAY = 5  # Delay between retry attempts in seconds
CLEANUP_ON_EXIT = True  # Clean up temporary files on exit

# Educational Research Settings
RESEARCH_MODE = True  # Enable educational research features
SAVE_SESSIONS = True  # Save browser sessions for analysis
ANALYTICS_ENABLED = False  # Enable usage analytics (disabled for privacy)
