#!/usr/bin/env python3
"""
AdvancedRules CLI v2.0 - Unified Command Interface
Main entry point for all AdvancedRules operations

Usage:
    arx [flow|tasks] [subcommand] [options]

Examples:
    arx flow lint --flow=feature_request_to_pr
    arx flow run --flow=feature_request_to_pr --task-id=T-0001
    arx tasks plan "goal description"
    arx tasks print
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main CLI entry point - dispatches to subcommands"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(2)

    # Parse subcommand
    subcommand = sys.argv[1]

    if subcommand == "flow":
        # Import and delegate to flow commands
        try:
            from cli.ar_flow import main as flow_main
            flow_main(sys.argv[2:])
        except ImportError as e:
            print(f"❌ Failed to import flow module: {e}")
            print("Make sure flow tools are properly installed")
            sys.exit(1)

    elif subcommand == "tasks":
        # Import and delegate to tasks commands
        try:
            from cli.ar_tasks import main as tasks_main
            tasks_main(sys.argv[2:])
        except ImportError as e:
            print(f"❌ Failed to import tasks module: {e}")
            print("Make sure planning tools are properly installed")
            sys.exit(1)

    elif subcommand in ["--help", "-h", "help"]:
        print_usage()

    elif subcommand in ["--version", "-v", "version"]:
        print_version()

    else:
        print(f"❌ Unknown subcommand: {subcommand}")
        print_usage()
        sys.exit(2)


def print_usage():
    """Print CLI usage information"""
    print("🛠️  AdvancedRules CLI v2.0")
    print("=" * 40)
    print()
    print("Usage:")
    print("  arx <subcommand> [options]")
    print()
    print("Subcommands:")
    print("  flow     Flow management and execution")
    print("  tasks    Task planning and orchestration")
    print("  help     Show this help message")
    print("  version  Show version information")
    print()
    print("Flow Commands:")
    print("  arx flow lint --flow=<flow_id>           Validate flow definition")
    print("  arx flow run --flow=<flow_id>            Execute flow (dry-run by default)")
    print("  arx flow render --flow=<flow_id>         Render flow as diagram")
    print("  arx flow list                            List available flows")
    print()
    print("Tasks Commands:")
    print("  arx tasks plan <goal>                    Plan a new goal")
    print("  arx tasks print [task_id]               Print tasks")
    print("  arx tasks export [task_id]              Export tasks")
    print()
    print("Examples:")
    print("  arx flow lint --flow=feature_request_to_pr")
    print("  arx flow run --flow=feature_request_to_pr --task-id=T-0001")
    print("  arx tasks plan 'Build a web application'")
    print("  arx tasks print")
    print()
    print("Safety Notes:")
    print("  • All operations default to dry-run mode")
    print("  • Live execution requires AR_ENABLE_FLOW_ENGINE=1")
    print("  • Branch protection prevents main branch execution")
    print("  • Guards enforce safety constraints")


def print_version():
    """Print version information"""
    version_file = project_root / "pyproject.toml"
    version = "2.0.0"  # Default fallback

    if version_file.exists():
        try:
            import tomllib
            with open(version_file, 'rb') as f:
                data = tomllib.load(f)
                version = data.get('project', {}).get('version', version)
        except ImportError:
            # tomllib not available in older Python versions
            try:
                import tomli
                with open(version_file, 'rb') as f:
                    data = tomli.load(f)
                    version = data.get('project', {}).get('version', version)
            except ImportError:
                # Fallback: read as text and parse
                with open(version_file, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.strip().startswith('version = '):
                            version = line.split('=')[1].strip().strip('"\'')
                            break

    print(f"AdvancedRules CLI v{version}")
    print(f"Python: {sys.version}")
    print(f"Project: {project_root}")


if __name__ == "__main__":
    main()
