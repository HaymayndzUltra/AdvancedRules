#!/usr/bin/env python3
"""
Educational Browser Automation System
Command-line interface for educational fingerprint analysis
"""

import argparse
import logging
import sys
import os
from typing import Optional

# Add educational module to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'educational'))

from educational.browser_automation import EducationalBrowser
from educational.config_manager import ConfigManager

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Educational Browser Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available test sessions
  python3 educational_browser.py --list-sessions

  # Analyze single session
  python3 educational_browser.py --session-id abc-123 --target facebook

  # Analyze all sessions with auto proxy
  python3 educational_browser.py --replay-all --country-auto

  # Analyze with specific country proxy
  python3 educational_browser.py --session-id abc-123 --country US --headless

  # Get session summary
  python3 educational_browser.py --session-id abc-123 --summary
        """
    )
    
    # Session management
    parser.add_argument("--session-id", help="Session ID to analyze")
    parser.add_argument("--list-sessions", action="store_true", help="List all available sessions")
    parser.add_argument("--replay-all", action="store_true", help="Analyze all available sessions")
    parser.add_argument("--summary", action="store_true", help="Show session summary")
    
    # Target configuration
    parser.add_argument("--target", default="facebook", 
                       choices=["facebook", "instagram", "twitter", "linkedin"],
                       help="Target platform [default: facebook]")
    parser.add_argument("--target-url", help="Custom target URL")
    
    # Proxy configuration
    parser.add_argument("--country", help="Country for proxy selection (US, UK, PH, etc.)")
    parser.add_argument("--country-auto", action="store_true", 
                       help="Auto-detect country from fingerprint")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy")
    
    # Browser configuration
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--concurrent", type=int, default=3, 
                       help="Maximum concurrent browser instances [default: 3]")
    
    # Configuration management
    parser.add_argument("--config-password", default="educational2024", 
                       help="Configuration encryption password [default: educational2024]")
    parser.add_argument("--init-config", action="store_true", 
                       help="Initialize configuration with defaults")
    
    # Output and logging
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level [default: INFO]")
    parser.add_argument("--log-file", help="Log file path")
    parser.add_argument("--stats", action="store_true", help="Show system statistics")
    parser.add_argument("--export", help="Export session data to directory")
    
    # System options
    parser.add_argument("--sessions-dir", default="sessions", 
                       help="Sessions directory [default: sessions]")
    parser.add_argument("--maxsites-dir", default=".local_maxsites/login_facebookwixsite",
                       help="Educational sites directory")
    parser.add_argument("--config-dir", default="config",
                       help="Configuration directory [default: config]")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(args.config_dir)
        
        # Initialize configuration if requested
        if args.init_config:
            logger.info("Initializing configuration...")
            if config_manager.create_default_config(args.config_password):
                logger.info("Configuration initialized successfully")
                return 0
            else:
                logger.error("Failed to initialize configuration")
                return 1
        
        # Load configuration
        config = config_manager.load_config(args.config_password)
        if not config:
            logger.error("Failed to load configuration. Run with --init-config first.")
            return 1
        
        # Initialize educational browser
        browser_system = EducationalBrowser(
            sessions_dir=args.sessions_dir,
            maxsites_dir=args.maxsites_dir,
            config_file=os.path.join(args.config_dir, "config.json")
        )
        
        # Initialize proxy manager
        if not args.no_proxy:
            if not browser_system.initialize_proxy_manager():
                logger.warning("Failed to initialize proxy manager, continuing without proxy")
        
        # Handle different commands
        if args.list_sessions:
            sessions = browser_system.list_available_sessions()
            complete_sessions = browser_system.get_complete_sessions()
            
            print(f"\n📊 Available Sessions: {len(sessions)}")
            print(f"✅ Complete Sessions: {len(complete_sessions)}")
            print("\n📋 Session List:")
            
            for session_id in sessions:
                is_complete = any(s['session_id'] == session_id for s in complete_sessions)
                status = "✅" if is_complete else "⚠️"
                print(f"  {status} {session_id}")
            
            return 0
        
        if args.summary and args.session_id:
            summary = browser_system.get_session_summary(args.session_id)
            if summary:
                print(f"\n📋 Session Summary: {args.session_id}")
                print(f"  Complete: {summary.get('complete', False)}")
                print(f"  Email: {summary.get('email', 'Unknown')}")
                print(f"  User Agent: {summary.get('user_agent', 'Unknown')}")
                print(f"  Screen: {summary.get('screen_resolution', 'Unknown')}")
                print(f"  Timezone: {summary.get('timezone', 'Unknown')}")
                print(f"  Country: {summary.get('country', 'Unknown')}")
                print(f"  WebGL: {summary.get('webgl_vendor', 'Unknown')} / {summary.get('webgl_renderer', 'Unknown')}")
            else:
                logger.error(f"Session {args.session_id} not found")
                return 1
            
            return 0
        
        if args.stats:
            stats = browser_system.get_statistics()
            print(f"\n📊 System Statistics:")
            print(f"  Total Sessions Processed: {stats.get('total_sessions_processed', 0)}")
            print(f"  Successful Logins: {stats.get('successful_logins', 0)}")
            print(f"  Failed Logins: {stats.get('failed_logins', 0)}")
            print(f"  Checkpoint Encounters: {stats.get('checkpoint_encounters', 0)}")
            print(f"  Proxy Failures: {stats.get('proxy_failures', 0)}")
            print(f"  Fingerprint Injections: {stats.get('fingerprint_injections', 0)}")
            print(f"  Active Instances: {stats.get('active_instances', 0)}")
            print(f"  Available Sessions: {stats.get('available_sessions', 0)}")
            print(f"  Complete Sessions: {stats.get('complete_sessions', 0)}")
            
            return 0
        
        if args.export and args.session_id:
            if browser_system.export_session_data(args.session_id, args.export):
                logger.info(f"Session {args.session_id} exported to {args.export}")
                return 0
            else:
                logger.error(f"Failed to export session {args.session_id}")
                return 1
        
        # Determine target URL
        target_url = args.target_url
        if not target_url:
            target_config = config_manager.get_target_config(args.target, args.config_password)
            if target_config:
                target_url = target_config.get('url', 'https://www.facebook.com/')
            else:
                target_url = 'https://www.facebook.com/'
        
        # Determine country
        country = args.country
        if args.country_auto and args.session_id:
            # Auto-detect country from fingerprint
            session_data = browser_system.credential_manager.get_session_with_credentials_and_fingerprint(args.session_id)
            if session_data and session_data['fingerprint']:
                country = browser_system.fingerprint_replay.get_country_from_fingerprint(session_data['fingerprint'])
                logger.info(f"Auto-detected country: {country}")
        
        # Execute session analysis
        if args.session_id:
            logger.info(f"Starting session analysis: {args.session_id}")
            logger.info(f"Target URL: {target_url}")
            logger.info(f"Country: {country or 'Auto-detect'}")
            logger.info(f"Headless: {args.headless}")
            
            success = browser_system.analyze_session(
                session_id=args.session_id,
                target_url=target_url,
                country=country,
                headless=args.headless
            )
            
            if success:
                logger.info(f"✅ Session {args.session_id} analyzed successfully!")
                return 0
            else:
                logger.error(f"❌ Session {args.session_id} analysis failed!")
                return 1
        
        elif args.replay_all:
            logger.info("Starting analysis of all sessions...")
            logger.info(f"Target URL: {target_url}")
            logger.info(f"Country: {country or 'Auto-detect'}")
            logger.info(f"Concurrent: {args.concurrent}")
            logger.info(f"Headless: {args.headless}")
            
            results = browser_system.analyze_all_sessions(
                target_url=target_url,
                country=country,
                headless=args.headless,
                max_concurrent=args.concurrent
            )
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"\n📊 Analysis Summary:")
            print(f"  ✅ Successful: {successful}")
            print(f"  ❌ Failed: {total - successful}")
            print(f"  📋 Total: {total}")
            
            if successful > 0:
                logger.info(f"✅ {successful}/{total} sessions analyzed successfully!")
                return 0
            else:
                logger.error(f"❌ All {total} sessions failed!")
                return 1
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    finally:
        # Cleanup
        try:
            if 'browser_system' in locals():
                browser_system.cleanup_all_instances()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
