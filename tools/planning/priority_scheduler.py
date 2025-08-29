#!/usr/bin/env python3
"""
AdvancedRules Priority Scheduler
Simple heuristic-based task scheduling with pluggable algorithms

Features:
- Multiple scheduling algorithms
- Priority-based ordering
- Dependency-aware scheduling
- Configurable heuristics
"""

import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class SchedulingAlgorithm(Enum):
    """Available scheduling algorithms"""
    PRIORITY_FIRST = "priority_first"
    DEADLINE_DRIVEN = "deadline_driven"
    EFFORT_BALANCED = "effort_balanced"
    DEPENDENCY_CHAIN = "dependency_chain"


@dataclass
class ScheduledTask:
    """Scheduled task with timing information"""
    task_id: str
    step_id: str
    description: str
    priority: int
    estimated_time: int
    dependencies: List[str]
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: str = "pending"


class PriorityScheduler:
    """Pluggable priority-based task scheduler"""

    def __init__(self, algorithm: SchedulingAlgorithm = SchedulingAlgorithm.PRIORITY_FIRST):
        self.algorithm = algorithm
        self.scheduling_functions = {
            SchedulingAlgorithm.PRIORITY_FIRST: self._priority_first_scheduling,
            SchedulingAlgorithm.DEADLINE_DRIVEN: self._deadline_driven_scheduling,
            SchedulingAlgorithm.EFFORT_BALANCED: self._effort_balanced_scheduling,
            SchedulingAlgorithm.DEPENDENCY_CHAIN: self._dependency_chain_scheduling,
        }

    def schedule_tasks(self, tasks: List[Dict[str, Any]],
                     start_time: Optional[datetime] = None) -> List[ScheduledTask]:
        """Main scheduling method - delegates to specific algorithm"""

        if start_time is None:
            start_time = datetime.now()

        if self.algorithm not in self.scheduling_functions:
            raise ValueError(f"Unknown scheduling algorithm: {self.algorithm}")

        scheduler_func = self.scheduling_functions[self.algorithm]
        return scheduler_func(tasks, start_time)

    def _priority_first_scheduling(self, tasks: List[Dict[str, Any]],
                                  start_time: datetime) -> List[ScheduledTask]:
        """Priority-first scheduling: High priority tasks first, then by dependencies"""

        # Convert to ScheduledTask objects
        scheduled_tasks = []
        for task_data in tasks:
            for step_data in task_data.get("steps", []):
                task = ScheduledTask(
                    task_id=task_data["id"],
                    step_id=step_data["id"],
                    description=step_data["description"],
                    priority=step_data.get("priority", 1),
                    estimated_time=step_data.get("estimated_time", 60),
                    dependencies=step_data.get("dependencies", [])
                )
                scheduled_tasks.append(task)

        # Sort by priority (higher first), then by dependency count (fewer first)
        scheduled_tasks.sort(key=lambda x: (-x.priority, len(x.dependencies)))

        # Schedule with dependency resolution
        scheduled = []
        current_time = start_time
        processed = set()

        while scheduled_tasks:
            # Find tasks with no unresolved dependencies
            available = []
            for task in scheduled_tasks:
                deps_resolved = all(dep in processed for dep in task.dependencies)
                if deps_resolved:
                    available.append(task)

            if not available:
                # No tasks can be scheduled - dependency issue
                break

            # Take the highest priority available task
            next_task = max(available, key=lambda x: x.priority)

            # Schedule it
            next_task.scheduled_start = current_time
            next_task.scheduled_end = current_time + timedelta(minutes=next_task.estimated_time)

            scheduled.append(next_task)
            processed.add(next_task.description)
            scheduled_tasks.remove(next_task)
            current_time = next_task.scheduled_end

        return scheduled

    def _deadline_driven_scheduling(self, tasks: List[Dict[str, Any]],
                                  start_time: datetime) -> List[ScheduledTask]:
        """Deadline-driven: Prioritize tasks with nearest deadlines"""

        # For this implementation, we'll use priority as a proxy for urgency/deadline
        # In a real system, this would use actual deadline data

        scheduled_tasks = []
        for task_data in tasks:
            for step_data in task_data.get("steps", []):
                task = ScheduledTask(
                    task_id=task_data["id"],
                    step_id=step_data["id"],
                    description=step_data["description"],
                    priority=step_data.get("priority", 1),
                    estimated_time=step_data.get("estimated_time", 60),
                    dependencies=step_data.get("dependencies", [])
                )
                scheduled_tasks.append(task)

        # Sort by "urgency" (inverse of priority, higher priority = more urgent)
        scheduled_tasks.sort(key=lambda x: (len(x.dependencies), -x.priority))

        return self._schedule_with_dependencies(scheduled_tasks, start_time)

    def _effort_balanced_scheduling(self, tasks: List[Dict[str, Any]],
                                  start_time: datetime) -> List[ScheduledTask]:
        """Effort-balanced: Alternate between high and low effort tasks"""

        scheduled_tasks = []
        for task_data in tasks:
            for step_data in task_data.get("steps", []):
                task = ScheduledTask(
                    task_id=task_data["id"],
                    step_id=step_data["id"],
                    description=step_data["description"],
                    priority=step_data.get("priority", 1),
                    estimated_time=step_data.get("estimated_time", 60),
                    dependencies=step_data.get("dependencies", [])
                )
                scheduled_tasks.append(task)

        # Sort by effort (estimated_time), alternating high/low
        high_effort = [t for t in scheduled_tasks if t.estimated_time >= 120]
        low_effort = [t for t in scheduled_tasks if t.estimated_time < 120]

        # Interleave high and low effort tasks
        result = []
        max_len = max(len(high_effort), len(low_effort))

        for i in range(max_len):
            if i < len(high_effort):
                result.append(high_effort[i])
            if i < len(low_effort):
                result.append(low_effort[i])

        return self._schedule_with_dependencies(result, start_time)

    def _dependency_chain_scheduling(self, tasks: List[Dict[str, Any]],
                                   start_time: datetime) -> List[ScheduledTask]:
        """Dependency chain: Follow longest dependency chains first"""

        scheduled_tasks = []
        for task_data in tasks:
            for step_data in task_data.get("steps", []):
                task = ScheduledTask(
                    task_id=task_data["id"],
                    step_id=step_data["id"],
                    description=step_data["description"],
                    priority=step_data.get("priority", 1),
                    estimated_time=step_data.get("estimated_time", 60),
                    dependencies=step_data.get("dependencies", [])
                )
                scheduled_tasks.append(task)

        # Sort by dependency chain length (longest first)
        def get_chain_length(task):
            # Simple heuristic: count dependencies as proxy for chain length
            return len(task.dependencies) + task.priority

        scheduled_tasks.sort(key=lambda x: -get_chain_length(x))

        return self._schedule_with_dependencies(scheduled_tasks, start_time)

    def _schedule_with_dependencies(self, tasks: List[ScheduledTask],
                                  start_time: datetime) -> List[ScheduledTask]:
        """Helper method to schedule tasks respecting dependencies"""

        scheduled = []
        current_time = start_time
        processed = set()

        remaining = tasks.copy()

        while remaining:
            # Find tasks whose dependencies are satisfied
            available = []
            for task in remaining:
                deps_satisfied = all(dep in processed for dep in task.dependencies)
                if deps_satisfied:
                    available.append(task)

            if not available:
                # Deadlock - schedule remaining tasks without dependency resolution
                available = remaining[:]

            # Schedule the first available task
            task_to_schedule = available[0]

            task_to_schedule.scheduled_start = current_time
            task_to_schedule.scheduled_end = current_time + timedelta(minutes=task_to_schedule.estimated_time)

            scheduled.append(task_to_schedule)
            processed.add(task_to_schedule.description)
            remaining.remove(task_to_schedule)
            current_time = task_to_schedule.scheduled_end

        return scheduled

    def export_schedule(self, scheduled_tasks: List[ScheduledTask],
                       format: str = "json") -> str:
        """Export schedule in various formats"""

        if format == "json":
            schedule_data = []
            for task in scheduled_tasks:
                schedule_data.append({
                    "task_id": task.task_id,
                    "step_id": task.step_id,
                    "description": task.description,
                    "priority": task.priority,
                    "estimated_time": task.estimated_time,
                    "scheduled_start": task.scheduled_start.isoformat() if task.scheduled_start else None,
                    "scheduled_end": task.scheduled_end.isoformat() if task.scheduled_end else None,
                    "dependencies": task.dependencies
                })
            return json.dumps(schedule_data, indent=2)

        elif format == "text":
            lines = ["📅 SCHEDULED TASKS", "=" * 50]
            current_day = None

            for task in scheduled_tasks:
                if task.scheduled_start:
                    day = task.scheduled_start.strftime("%Y-%m-%d")
                    if day != current_day:
                        lines.append(f"\n📆 {day}")
                        current_day = day

                    start_time = task.scheduled_start.strftime("%H:%M")
                    end_time = task.scheduled_end.strftime("%H:%M") if task.scheduled_end else "TBD"

                    lines.append(f"  {start_time}-{end_time}: {task.description}")
                    lines.append(f"    Priority: {task.priority}, Duration: {task.estimated_time}min")

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")


def main():
    """CLI interface for priority scheduling"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="AdvancedRules Priority Scheduler")
    parser.add_argument("--algorithm", choices=[a.value for a in SchedulingAlgorithm],
                       default=SchedulingAlgorithm.PRIORITY_FIRST.value,
                       help="Scheduling algorithm to use")
    parser.add_argument("--input", required=True,
                       help="JSON file containing tasks to schedule")
    parser.add_argument("--output", help="Output file for schedule")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format")

    args = parser.parse_args()

    # Load tasks from JSON file
    try:
        with open(args.input, 'r') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in input file: {args.input}")
        sys.exit(1)

    # Create scheduler and generate schedule
    algorithm = SchedulingAlgorithm(args.algorithm)
    scheduler = PriorityScheduler(algorithm)

    print(f"📅 Scheduling with algorithm: {algorithm.value}")
    print(f"📋 Input tasks: {len(tasks)}")
    print("=" * 50)

    scheduled_tasks = scheduler.schedule_tasks(tasks)

    # Export and display results
    result = scheduler.export_schedule(scheduled_tasks, args.format)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"✅ Schedule saved to: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
