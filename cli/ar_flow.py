#!/usr/bin/env python3
"""
AdvancedRules Flow CLI Module
Handles flow-related operations: lint, run, render, list

Usage:
    python -m cli.ar_flow [command] [options]
    arx flow [command] [options]
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.flow.flow_linter import FlowLinter
from tools.flow.flow_runner import FlowRunner


def main(args: Optional[List[str]] = None):
    """Main entry point for flow commands"""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="AdvancedRules Flow CLI",
        prog="arx flow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arx flow lint --flow=feature_request_to_pr
  arx flow run --flow=feature_request_to_pr --task-id=T-0001
  arx flow render --flow=feature_request_to_pr --out=flow.mmd
  arx flow list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Flow command to execute")

    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Validate flow definition")
    lint_parser.add_argument("--flow", required=True, help="Flow ID to validate")
    lint_parser.add_argument("--registry", default="flow/flow_registry.yaml",
                           help="Path to flow registry file")

    # Run command
    run_parser = subparsers.add_parser("run", help="Execute flow")
    run_parser.add_argument("--flow", required=True, help="Flow ID to execute")
    run_parser.add_argument("--task-id", help="Task ID for execution tracking")
    run_parser.add_argument("--registry", default="flow/flow_registry.yaml",
                           help="Path to flow registry file")
    run_parser.add_argument("--dry-run", action="store_true", default=True,
                           help="Execute in dry-run mode (default)")
    run_parser.add_argument("--live", action="store_true",
                           help="Execute in live mode (requires AR_ENABLE_FLOW_ENGINE=1)")
    run_parser.add_argument("--param", action="append",
                           help="Parameter in key=value format")

    # Render command
    render_parser = subparsers.add_parser("render", help="Render flow as diagram")
    render_parser.add_argument("--flow", required=True, help="Flow ID to render")
    render_parser.add_argument("--registry", default="flow/flow_registry.yaml",
                              help="Path to flow registry file")
    render_parser.add_argument("--out", help="Output file path")
    render_parser.add_argument("--format", choices=["mmd", "dot", "json"],
                              default="mmd", help="Output format (default: mmd)")

    # List command
    list_parser = subparsers.add_parser("list", help="List available flows")
    list_parser.add_argument("--registry", default="flow/flow_registry.yaml",
                           help="Path to flow registry file")

    # Parse arguments
    if not args:
        parser.print_help()
        return

    parsed_args = parser.parse_args(args)

    # Check feature flag for run and render commands
    if parsed_args.command in ["run", "render"]:
        flow_engine_enabled = os.getenv("AR_ENABLE_FLOW_ENGINE", "0") == "1"
        if not flow_engine_enabled:
            print("❌ Flow engine disabled - set AR_ENABLE_FLOW_ENGINE=1 to enable")
            print("   This is a safety feature to prevent accidental execution")
            sys.exit(1)

    # Execute command
    if parsed_args.command == "lint":
        cmd_lint(parsed_args)
    elif parsed_args.command == "run":
        cmd_run(parsed_args)
    elif parsed_args.command == "render":
        cmd_render(parsed_args)
    elif parsed_args.command == "list":
        cmd_list(parsed_args)
    else:
        print(f"❌ Unknown command: {parsed_args.command}")
        parser.print_help()
        sys.exit(1)


def cmd_lint(args):
    """Lint flow definition"""
    registry_path = Path(args.registry)

    if not registry_path.exists():
        print(f"❌ Flow registry not found: {registry_path}")
        sys.exit(1)

    print(f"🔍 Linting flow: {args.flow}")
    print(f"   Registry: {registry_path}")
    print("-" * 40)

    linter = FlowLinter()
    results = linter.validate_flow_registry(str(registry_path))

    if args.flow not in results:
        print(f"❌ Flow '{args.flow}' not found in registry")
        print(f"   Available flows: {', '.join([k for k in results.keys() if k != 'registry'])}")
        sys.exit(1)

    flow_result = results[args.flow]
    registry_result = results["registry"]

    # Print results
    print(f"📋 Registry validation: {'✅ PASS' if registry_result.is_valid else '❌ FAIL'}")
    print(f"📋 Flow '{args.flow}' validation: {'✅ PASS' if flow_result.is_valid else '❌ FAIL'}")

    if not flow_result.is_valid:
        print("\n❌ Validation Errors:")
        for error in flow_result.errors:
            print(f"   • {error.code}: {error.message}")

    if flow_result.warnings:
        print("\n⚠️  Validation Warnings:")
        for warning in flow_result.warnings:
            print(f"   • {warning.code}: {warning.message}")

    success = flow_result.is_valid
    print(f"\n🎯 Lint Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)


def cmd_run(args):
    """Execute flow"""
    registry_path = Path(args.registry)

    if not registry_path.exists():
        print(f"❌ Flow registry not found: {registry_path}")
        sys.exit(1)

    # Parse parameters
    parameters = {}
    if args.param:
        for param in args.param:
            if "=" in param:
                key, value = param.split("=", 1)
                parameters[key] = value
            else:
                print(f"⚠️  Invalid parameter format: {param} (expected key=value)")
                continue

    # Determine execution mode
    dry_run = args.dry_run and not args.live

    print(f"🚀 Executing flow: {args.flow}")
    print(f"   Task ID: {args.task_id or 'auto-generated'}")
    print(f"   Dry-run: {dry_run}")
    print(f"   Parameters: {parameters}")
    print(f"   Registry: {registry_path}")
    print("-" * 60)

    try:
        runner = FlowRunner(str(registry_path))
        result = runner.execute_flow(args.flow, parameters, dry_run)

        # Print execution summary
        print("\n📊 Execution Summary:")
        print(f"   Flow ID: {result['flow_id']}")
        print(f"   Success Rate: {result['success_rate']:.1%}")
        print(f"   Duration: {result['execution_time']:.1f}s")
        print(f"   Nodes: {result['successful_nodes']}/{result['total_nodes']} successful")

        if result['failed_nodes'] > 0:
            print(f"   Failed: {result['failed_nodes']} nodes")
            print("\n❌ Execution completed with failures")
            sys.exit(1)
        else:
            print("\n✅ Execution completed successfully!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Flow execution failed: {e}")
        sys.exit(1)


def cmd_render(args):
    """Render flow as diagram"""
    registry_path = Path(args.registry)

    if not registry_path.exists():
        print(f"❌ Flow registry not found: {registry_path}")
        sys.exit(1)

    print(f"🎨 Rendering flow: {args.flow}")
    print(f"   Format: {args.format}")
    print(f"   Output: {args.out or 'stdout'}")
    print(f"   Registry: {registry_path}")
    print("-" * 40)

    # For now, provide basic text rendering
    # In a full implementation, this could generate Mermaid, DOT, or other formats
    try:
        import yaml
        with open(registry_path, 'r') as f:
            registry = yaml.safe_load(f)

        if "flows" not in registry or args.flow not in registry["flows"]:
            print(f"❌ Flow '{args.flow}' not found in registry")
            sys.exit(1)

        flow_def = registry["flows"][args.flow]

        if args.format == "mmd":
            output = render_mermaid(flow_def, args.flow)
        elif args.format == "dot":
            output = render_dot(flow_def, args.flow)
        elif args.format == "json":
            output = render_json(flow_def, args.flow)
        else:
            print(f"❌ Unsupported format: {args.format}")
            sys.exit(1)

        if args.out:
            with open(args.out, 'w') as f:
                f.write(output)
            print(f"✅ Rendered to file: {args.out}")
        else:
            print(output)

    except Exception as e:
        print(f"❌ Render failed: {e}")
        sys.exit(1)


def cmd_list(args):
    """List available flows"""
    registry_path = Path(args.registry)

    if not registry_path.exists():
        print(f"❌ Flow registry not found: {registry_path}")
        sys.exit(1)

    print(f"📋 Available Flows")
    print(f"   Registry: {registry_path}")
    print("-" * 40)

    try:
        import yaml
        with open(registry_path, 'r') as f:
            registry = yaml.safe_load(f)

        if "flows" not in registry:
            print("❌ No flows found in registry")
            sys.exit(1)

        flows = registry["flows"]
        if not flows:
            print("❌ Registry is empty")
            sys.exit(1)

        for flow_id, flow_def in flows.items():
            name = flow_def.get("name", "Unnamed Flow")
            description = flow_def.get("description", "No description")
            nodes_count = len(flow_def.get("nodes", {}))
            edges_count = len(flow_def.get("edges", []))

            print(f"🎯 {flow_id}")
            print(f"   Name: {name}")
            print(f"   Description: {description}")
            print(f"   Nodes: {nodes_count}, Edges: {edges_count}")
            print()

        print(f"📊 Total: {len(flows)} flows")

    except Exception as e:
        print(f"❌ List failed: {e}")
        sys.exit(1)


def render_mermaid(flow_def: dict, flow_id: str) -> str:
    """Render flow as Mermaid diagram"""
    lines = [f"---", f"title: {flow_def.get('name', flow_id)}", f"---"]
    lines.append("flowchart TD")

    nodes = flow_def.get("nodes", {})
    edges = flow_def.get("edges", [])

    # Add nodes
    for node_id, node_def in nodes.items():
        node_type = node_def.get("type", "command")
        node_name = node_def.get("name", node_id)
        lines.append(f"    {node_id}[\"{node_name}<br/>({node_type})\"]")

    lines.append("")

    # Add edges
    for edge in edges:
        from_node = edge.get("from")
        to_node = edge.get("to")
        condition = edge.get("when")

        if from_node and to_node:
            if condition:
                lines.append(f"    {from_node} -->|{condition}| {to_node}")
            else:
                lines.append(f"    {from_node} --> {to_node}")

    return "\n".join(lines)


def render_dot(flow_def: dict, flow_id: str) -> str:
    """Render flow as DOT graph"""
    lines = [f"digraph {flow_id} {{"]
    lines.append(f'    label="{flow_def.get("name", flow_id)}";')
    lines.append("    rankdir=TB;")

    nodes = flow_def.get("nodes", {})
    edges = flow_def.get("edges", [])

    # Add nodes
    for node_id, node_def in nodes.items():
        node_type = node_def.get("type", "command")
        node_name = node_def.get("name", node_id)
        lines.append(f'    {node_id} [label="{node_name}\\n({node_type})"];')

    lines.append("")

    # Add edges
    for edge in edges:
        from_node = edge.get("from")
        to_node = edge.get("to")
        condition = edge.get("when")

        if from_node and to_node:
            if condition:
                lines.append(f'    {from_node} -> {to_node} [label="{condition}"];')
            else:
                lines.append(f'    {from_node} -> {to_node};')

    lines.append("}")
    return "\n".join(lines)


def render_json(flow_def: dict, flow_id: str) -> str:
    """Render flow as JSON"""
    import json
    return json.dumps({
        "flow_id": flow_id,
        "definition": flow_def
    }, indent=2)


if __name__ == "__main__":
    main()
