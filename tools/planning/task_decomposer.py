#!/usr/bin/env python3
"""
AdvancedRules Task Decomposer
Rules+LLM hybrid approach for converting goals into ordered subtask graphs

Features:
- Cycle-free dependency graph generation
- Priority-based ordering
- Rules-driven decomposition with LLM enhancement
- JSON schema compliance
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx  # For cycle detection and topological sorting


@dataclass
class TaskStep:
    """Individual step within a task"""
    id: str
    description: str
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    estimated_time: int = 60  # minutes
    status: str = "pending"  # pending, in_progress, completed, blocked


@dataclass
class Task:
    """Task containing multiple steps"""
    id: str
    title: str
    description: str
    steps: List[TaskStep] = field(default_factory=list)
    priority: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"


class TaskDecomposer:
    """Rules+LLM hybrid task decomposition engine"""

    def __init__(self, rules_file: str = None):
        self.rules = self._load_decomposition_rules(rules_file)
        self.task_counter = 0
        self.step_counter = 0

    def _load_decomposition_rules(self, rules_file: str = None) -> Dict:
        """Load decomposition rules from file or use defaults"""
        default_rules = {
            "patterns": {
                "implementation": [
                    "design", "implement", "test", "deploy", "document"
                ],
                "research": [
                    "gather_requirements", "analyze", "research", "validate", "document"
                ],
                "planning": [
                    "analyze", "design", "schedule", "resource", "execute"
                ]
            },
            "dependencies": {
                "design": [],
                "implement": ["design"],
                "test": ["implement"],
                "deploy": ["test"],
                "document": ["implement"],
                "analyze": [],
                "research": ["analyze"],
                "validate": ["research"],
                "schedule": ["analyze"],
                "resource": ["schedule"],
                "execute": ["resource"]
            },
            "priorities": {
                "design": 1, "analyze": 1, "research": 1,
                "implement": 2, "validate": 2, "schedule": 2,
                "test": 3, "resource": 3, "document": 3,
                "deploy": 4, "execute": 4
            }
        }
        return default_rules

    def _generate_id(self, prefix: str) -> str:
        """Generate unique IDs for tasks and steps"""
        if prefix == "task":
            self.task_counter += 1
            return f"task_{self.task_counter:03d}"
        elif prefix == "step":
            self.step_counter += 1
            return f"step_{self.step_counter:03d}"
        return f"{prefix}_{datetime.now().strftime('%H%M%S')}"

    def _extract_goal_type(self, goal: str) -> str:
        """Extract goal type from goal description using pattern matching"""
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["build", "implement", "create", "develop"]):
            return "implementation"
        elif any(word in goal_lower for word in ["research", "investigate", "study", "analyze"]):
            return "research"
        elif any(word in goal_lower for word in ["plan", "organize", "schedule", "coordinate"]):
            return "planning"
        else:
            return "implementation"  # default

    def _apply_rules_decomposition(self, goal: str, goal_type: str) -> List[str]:
        """Apply rules-based decomposition patterns"""
        steps = []

        if goal_type in self.rules["patterns"]:
            pattern = self.rules["patterns"][goal_type]
            for i, step_name in enumerate(pattern):
                step_desc = f"{step_name.title()} phase for: {goal}"
                steps.append(step_desc)

        return steps

    def _enhance_with_llm(self, goal: str, rule_steps: List[str]) -> List[str]:
        """Enhance rules with LLM-style reasoning (pseudo-implementation)"""
        enhanced_steps = []

        for step in rule_steps:
            # Pseudo-LLM enhancement - in real implementation, this would call an LLM
            if "design" in step.lower():
                enhanced_steps.append(f"Design detailed specifications and architecture for {goal}")
            elif "implement" in step.lower():
                enhanced_steps.append(f"Implement core functionality with proper error handling for {goal}")
            elif "test" in step.lower():
                enhanced_steps.append(f"Create comprehensive tests and validate implementation for {goal}")
            elif "deploy" in step.lower():
                enhanced_steps.append(f"Deploy to production environment with monitoring for {goal}")
            else:
                enhanced_steps.append(step)

        return enhanced_steps

    def _create_dependency_graph(self, steps: List[str], goal_type: str) -> Dict[str, List[str]]:
        """Create dependency relationships between steps"""
        dependencies = {}

        if goal_type in self.rules["dependencies"]:
            dep_rules = self.rules["dependencies"]

            for i, step in enumerate(steps):
                step_key = step.split()[0].lower()  # extract first word as key
                deps = []

                # Add dependencies based on rules
                for prev_step in steps[:i]:
                    prev_key = prev_step.split()[0].lower()
                    if prev_key in dep_rules and step_key in dep_rules[prev_key]:
                        deps.append(prev_step)

                dependencies[step] = deps

        return dependencies

    def _assign_priorities(self, steps: List[str], dependencies: Dict[str, List[str]]) -> Dict[str, int]:
        """Assign priorities based on dependencies and rules"""
        priorities = {}

        for step in steps:
            step_key = step.split()[0].lower()
            base_priority = self.rules["priorities"].get(step_key, 2)

            # Boost priority if step has many dependents
            dependents = sum(1 for deps in dependencies.values() if step in deps)
            priority = base_priority + dependents

            priorities[step] = min(priority, 5)  # Cap at 5

        return priorities

    def _ensure_acyclic(self, dependencies: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Ensure dependency graph is acyclic using NetworkX"""
        try:
            G = nx.DiGraph()
            for step, deps in dependencies.items():
                for dep in deps:
                    G.add_edge(dep, step)

            # Check for cycles
            if nx.is_directed_acyclic_graph(G):
                return dependencies
            else:
                # Remove problematic edges to break cycles
                cycles = list(nx.simple_cycles(G))
                cleaned_deps = dependencies.copy()

                for cycle in cycles:
                    # Remove the last dependency in cycle
                    if len(cycle) > 1:
                        last_step = cycle[-1]
                        if last_step in cleaned_deps and cycle[-2] in cleaned_deps[last_step]:
                            cleaned_deps[last_step].remove(cycle[-2])

                return cleaned_deps

        except Exception:
            # Fallback: return original dependencies if graph analysis fails
            return dependencies

    def decompose_goal(self, goal: str) -> Task:
        """Main method to decompose a goal into an ordered task with steps"""

        # Extract goal type and apply rules
        goal_type = self._extract_goal_type(goal)

        # Rule-based decomposition
        rule_steps = self._apply_rules_decomposition(goal, goal_type)

        # LLM enhancement
        enhanced_steps = self._enhance_with_llm(goal, rule_steps)

        # Create dependency graph
        dependencies = self._create_dependency_graph(enhanced_steps, goal_type)

        # Ensure acyclic dependencies
        clean_dependencies = self._ensure_acyclic(dependencies)

        # Assign priorities
        priorities = self._assign_priorities(enhanced_steps, clean_dependencies)

        # Create TaskStep objects
        task_steps = []
        for step_desc in enhanced_steps:
            step = TaskStep(
                id=self._generate_id("step"),
                description=step_desc,
                priority=priorities.get(step_desc, 2),
                dependencies=clean_dependencies.get(step_desc, []),
                estimated_time=60
            )
            task_steps.append(step)

        # Create Task object
        task = Task(
            id=self._generate_id("task"),
            title=f"Task: {goal[:50]}...",
            description=goal,
            steps=task_steps,
            priority=2
        )

        return task

    def validate_task_graph(self, task: Task) -> Tuple[bool, List[str]]:
        """Validate that task graph is well-formed"""
        issues = []

        # Check for cycles
        try:
            G = nx.DiGraph()
            for step in task.steps:
                for dep in step.dependencies:
                    G.add_edge(dep, step.description)

            if not nx.is_directed_acyclic_graph(G):
                issues.append("Task graph contains cycles")
        except Exception as e:
            issues.append(f"Graph validation error: {e}")

        # Check dependency validity
        step_descriptions = {step.description for step in task.steps}
        for step in task.steps:
            for dep in step.dependencies:
                if dep not in step_descriptions:
                    issues.append(f"Invalid dependency '{dep}' in step '{step.description}'")

        return len(issues) == 0, issues


def main():
    """CLI interface for task decomposition"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python task_decomposer.py 'your goal here'")
        sys.exit(1)

    goal = sys.argv[1]
    decomposer = TaskDecomposer()

    print(f"🔍 Decomposing goal: {goal}")
    print("=" * 50)

    task = decomposer.decompose_goal(goal)

    # Validate the result
    is_valid, issues = decomposer.validate_task_graph(task)

    if not is_valid:
        print("❌ Validation issues:")
        for issue in issues:
            print(f"   • {issue}")
        sys.exit(1)

    print("✅ Task decomposition successful!")
    print(f"Task ID: {task.id}")
    print(f"Steps: {len(task.steps)}")
    print("\n📋 Execution Order:")
    print("-" * 30)

    for i, step in enumerate(task.steps, 1):
        deps_str = f" ← {', '.join(step.dependencies)}" if step.dependencies else ""
        print(f"{i}. {step.description}{deps_str}")
        print(f"   Priority: {step.priority}, Est. Time: {step.estimated_time}min")


if __name__ == "__main__":
    main()
