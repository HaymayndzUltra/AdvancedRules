#!/usr/bin/env python3
"""
AdvancedRules Task Management CLI
Planning pipeline interface with plan, print, and export commands

Usage:
  python ar_tasks.py plan "goal description"
  python ar_tasks.py print [task_id]
  python ar_tasks.py export [task_id] [--format json|text] [--output file]
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from planning.task_decomposer import TaskDecomposer, Task
from planning.priority_scheduler import PriorityScheduler, SchedulingAlgorithm


class TaskManager:
    """Task management interface for CLI operations"""

    def __init__(self, workflow_file: str = "workflow_state.json"):
        self.workflow_file = Path(workflow_file)
        self.task_decomposer = TaskDecomposer()
        self.scheduler = PriorityScheduler()

    def _load_workflow_state(self) -> Dict[str, Any]:
        """Load current workflow state"""
        if not self.workflow_file.exists():
            return {"tasks": []}

        try:
            with open(self.workflow_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"tasks": []}

    def _save_workflow_state(self, state: Dict[str, Any]) -> None:
        """Save updated workflow state"""
        with open(self.workflow_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _extend_workflow_with_tasks(self, task: Task) -> Dict[str, Any]:
        """Extend workflow state with new task and steps"""
        state = self._load_workflow_state()

        # Convert Task object to serializable format
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "created_at": task.created_at,
            "status": task.status,
            "steps": []
        }

        for step in task.steps:
            step_data = {
                "id": step.id,
                "description": step.description,
                "priority": step.priority,
                "dependencies": step.dependencies,
                "estimated_time": step.estimated_time,
                "status": step.status
            }
            task_data["steps"].append(step_data)

        # Add to tasks array
        if "tasks" not in state:
            state["tasks"] = []
        state["tasks"].append(task_data)

        # Update state metadata
        state["last_updated"] = datetime.now().isoformat()
        state["total_tasks"] = len(state["tasks"])

        return state

    def plan_goal(self, goal: str) -> Task:
        """Plan a goal by decomposing it into tasks and steps"""
        print(f"🎯 Planning goal: {goal}")
        print("=" * 60)

        # Decompose the goal
        task = self.task_decomposer.decompose_goal(goal)

        # Validate the task graph
        is_valid, issues = self.task_decomposer.validate_task_graph(task)

        if not is_valid:
            print("❌ Task decomposition validation failed:")
            for issue in issues:
                print(f"   • {issue}")
            return None

        # Extend workflow state
        updated_state = self._extend_workflow_with_tasks(task)
        self._save_workflow_state(updated_state)

        print("✅ Goal planned successfully!")
        print(f"📋 Task ID: {task.id}")
        print(f"📝 Steps: {len(task.steps)}")
        print(f"🎯 Status: Ready for execution")

        return task

    def print_tasks(self, task_id: Optional[str] = None) -> None:
        """Print tasks and their status"""
        state = self._load_workflow_state()

        if "tasks" not in state or not state["tasks"]:
            print("📭 No tasks found in workflow state")
            return

        tasks = state["tasks"]
        if task_id:
            tasks = [t for t in tasks if t["id"] == task_id]
            if not tasks:
                print(f"❌ Task not found: {task_id}")
                return

        print("📋 TASKS OVERVIEW")
        print("=" * 50)

        for task in tasks:
            print(f"\n🎯 Task: {task['title']}")
            print(f"   ID: {task['id']}")
            print(f"   Status: {task.get('status', 'unknown')}")
            print(f"   Priority: {task.get('priority', 'N/A')}")
            print(f"   Created: {task.get('created_at', 'N/A')[:19]}")
            print(f"   Steps: {len(task.get('steps', []))}")

            if task.get("steps"):
                print("   📝 Step Details:")
                for i, step in enumerate(task["steps"], 1):
                    status_icon = {
                        "pending": "⏳",
                        "in_progress": "🔄",
                        "completed": "✅",
                        "blocked": "🚫"
                    }.get(step.get("status", "pending"), "❓")

                    deps = step.get("dependencies", [])
                    deps_str = f" ← {', '.join(deps)}" if deps else ""

                    print(f"     {i}. {status_icon} {step['description']}{deps_str}")
                    print(f"        Priority: {step.get('priority', 'N/A')}, "
                          f"Time: {step.get('estimated_time', 'N/A')}min")

    def export_tasks(self, task_id: Optional[str] = None,
                    format: str = "json", output_file: Optional[str] = None) -> None:
        """Export tasks in specified format"""
        state = self._load_workflow_state()

        if "tasks" not in state:
            print("❌ No tasks found to export")
            return

        tasks_to_export = state["tasks"]
        if task_id:
            tasks_to_export = [t for t in tasks_to_export if t["id"] == task_id]
            if not tasks_to_export:
                print(f"❌ Task not found: {task_id}")
                return

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "format": format,
            "tasks": tasks_to_export
        }

        if format == "json":
            output = json.dumps(export_data, indent=2)
        elif format == "text":
            lines = ["📋 EXPORTED TASKS", "=" * 40]
            lines.append(f"Exported: {datetime.now().isoformat()}")
            lines.append(f"Format: {format}")
            lines.append("")

            for task in tasks_to_export:
                lines.append(f"🎯 {task['title']}")
                lines.append(f"ID: {task['id']}")
                lines.append(f"Description: {task['description']}")
                lines.append(f"Priority: {task['priority']}")
                lines.append("")

                if task.get("steps"):
                    lines.append("📝 Steps:")
                    for i, step in enumerate(task["steps"], 1):
                        lines.append(f"  {i}. {step['description']}")
                        lines.append(f"     Priority: {step.get('priority')}")
                        lines.append(f"     Time: {step.get('estimated_time')}min")
                        if step.get("dependencies"):
                            lines.append(f"     Dependencies: {', '.join(step['dependencies'])}")
                        lines.append("")

                lines.append("-" * 40)

            output = "\n".join(lines)
        else:
            print(f"❌ Unsupported format: {format}")
            return

        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"✅ Exported to file: {output_file}")
        else:
            print(output)


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python ar_tasks.py <command> [options]")
        print("")
        print("Commands:")
        print("  plan <goal>              Plan a new goal")
        print("  print [task_id]          Print tasks (all or specific)")
        print("  export [task_id]         Export tasks")
        print("                           --format json|text (default: json)")
        print("                           --output <file>")
        print("")
        print("Examples:")
        print("  python ar_tasks.py plan 'Build a web application'")
        print("  python ar_tasks.py print")
        print("  python ar_tasks.py export task_001 --format text --output tasks.txt")
        sys.exit(1)

    command = sys.argv[1].lower()
    task_manager = TaskManager()

    if command == "plan":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a goal to plan")
            print("Usage: python ar_tasks.py plan 'your goal here'")
            sys.exit(1)

        goal = " ".join(sys.argv[2:])
        task = task_manager.plan_goal(goal)

        if task:
            print("\n📋 Quick Summary:")
            task_manager.print_tasks(task.id)

    elif command == "print":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        task_manager.print_tasks(task_id)

    elif command == "export":
        # Parse arguments
        task_id = None
        format_type = "json"
        output_file = None

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--format" and i + 1 < len(sys.argv):
                format_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            elif not sys.argv[i].startswith("--"):
                task_id = sys.argv[i]
                i += 1
            else:
                i += 1

        task_manager.export_tasks(task_id, format_type, output_file)

    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: plan, print, export")
        sys.exit(1)


if __name__ == "__main__":
    main()
