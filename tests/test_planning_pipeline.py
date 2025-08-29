#!/usr/bin/env python3
"""
Unit Tests for AdvancedRules Planning Pipeline
Minimal test coverage for core planning components
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from planning.task_decomposer import TaskDecomposer, Task, TaskStep
from planning.priority_scheduler import PriorityScheduler, SchedulingAlgorithm


class TestTaskDecomposer:
    """Test cases for TaskDecomposer"""

    def test_goal_type_extraction(self):
        """Test goal type extraction from various goal descriptions"""
        decomposer = TaskDecomposer()

        # Test implementation goals
        assert decomposer._extract_goal_type("Build a web application") == "implementation"
        assert decomposer._extract_goal_type("Implement user authentication") == "implementation"
        assert decomposer._extract_goal_type("Create a new feature") == "implementation"

        # Test research goals
        assert decomposer._extract_goal_type("Research machine learning algorithms") == "research"
        assert decomposer._extract_goal_type("Investigate performance issues") == "research"
        assert decomposer._extract_goal_type("Analyze user behavior") == "research"

        # Test planning goals
        assert decomposer._extract_goal_type("Plan project timeline") == "planning"
        assert decomposer._extract_goal_type("Organize team workflow") == "planning"

    def test_task_creation(self):
        """Test basic task creation and structure"""
        decomposer = TaskDecomposer()
        goal = "Build a simple web application"

        task = decomposer.decompose_goal(goal)

        # Verify task structure
        assert isinstance(task, Task)
        assert task.id.startswith("task_")
        assert task.title == f"Task: {goal[:50]}..."
        assert task.description == goal
        assert len(task.steps) > 0

        # Verify step structure
        for step in task.steps:
            assert isinstance(step, TaskStep)
            assert step.id.startswith("step_")
            assert step.description
            assert step.priority >= 1
            assert step.estimated_time > 0

    def test_dependency_graph_validation(self):
        """Test dependency graph validation"""
        decomposer = TaskDecomposer()

        # Create a simple task
        task = decomposer.decompose_goal("Implement user login system")

        # Validate the graph
        is_valid, issues = decomposer.validate_task_graph(task)

        # Should be valid (acyclic)
        assert is_valid, f"Validation failed: {issues}"
        assert len(issues) == 0

    def test_cycle_detection(self):
        """Test cycle detection in dependency graphs"""
        decomposer = TaskDecomposer()

        # Create a task with potential cycles
        task = Task(
            id="test_task",
            title="Test Task",
            description="Test",
            steps=[
                TaskStep("step1", "Step 1", dependencies=["step3"]),  # Points to later step
                TaskStep("step2", "Step 2", dependencies=["step1"]),
                TaskStep("step3", "Step 3", dependencies=["step2"]),  # Creates cycle
            ]
        )

        is_valid, issues = decomposer.validate_task_graph(task)

        # Should detect cycle
        assert not is_valid
        assert any("cycle" in issue.lower() for issue in issues)


class TestPriorityScheduler:
    """Test cases for PriorityScheduler"""

    def test_priority_first_scheduling(self):
        """Test priority-first scheduling algorithm"""
        scheduler = PriorityScheduler(SchedulingAlgorithm.PRIORITY_FIRST)

        # Create test tasks
        tasks = [
            {
                "id": "task1",
                "steps": [
                    {"id": "step1", "description": "High priority step", "priority": 5, "estimated_time": 60, "dependencies": []},
                    {"id": "step2", "description": "Low priority step", "priority": 1, "estimated_time": 30, "dependencies": []}
                ]
            }
        ]

        scheduled = scheduler.schedule_tasks(tasks)

        # Verify scheduling order (high priority first)
        assert len(scheduled) == 2
        assert scheduled[0].priority >= scheduled[1].priority

    def test_dependency_resolution(self):
        """Test dependency resolution in scheduling"""
        scheduler = PriorityScheduler(SchedulingAlgorithm.PRIORITY_FIRST)

        tasks = [
            {
                "id": "task1",
                "steps": [
                    {"id": "step1", "description": "Step 1", "priority": 3, "estimated_time": 60, "dependencies": []},
                    {"id": "step2", "description": "Step 2", "priority": 3, "estimated_time": 30, "dependencies": ["Step 1"]}
                ]
            }
        ]

        scheduled = scheduler.schedule_tasks(tasks)

        # Step 1 should come before Step 2
        step1_idx = next(i for i, s in enumerate(scheduled) if s.description == "Step 1")
        step2_idx = next(i for i, s in enumerate(scheduled) if s.description == "Step 2")

        assert step1_idx < step2_idx

    def test_schedule_export(self):
        """Test schedule export functionality"""
        scheduler = PriorityScheduler()

        tasks = [
            {
                "id": "task1",
                "steps": [
                    {"id": "step1", "description": "Test step", "priority": 3, "estimated_time": 60, "dependencies": []}
                ]
            }
        ]

        scheduled = scheduler.schedule_tasks(tasks)

        # Test JSON export
        json_export = scheduler.export_schedule(scheduled, "json")
        json_data = json.loads(json_export)
        assert len(json_data) == 1
        assert json_data[0]["description"] == "Test step"

        # Test text export
        text_export = scheduler.export_schedule(scheduled, "text")
        assert "Test step" in text_export


class TestIntegration:
    """Integration tests for planning pipeline"""

    def test_full_pipeline(self):
        """Test complete planning pipeline"""
        # Decompose goal
        decomposer = TaskDecomposer()
        task = decomposer.decompose_goal("Build a user registration system")

        # Validate decomposition
        is_valid, issues = decomposer.validate_task_graph(task)
        assert is_valid, f"Decomposition validation failed: {issues}"

        # Convert to scheduler format
        tasks_data = [{
            "id": task.id,
            "steps": [
                {
                    "id": step.id,
                    "description": step.description,
                    "priority": step.priority,
                    "estimated_time": step.estimated_time,
                    "dependencies": step.dependencies
                }
                for step in task.steps
            ]
        }]

        # Schedule tasks
        scheduler = PriorityScheduler()
        scheduled = scheduler.schedule_tasks(tasks_data)

        # Verify scheduling
        assert len(scheduled) == len(task.steps)

        # Export results
        export = scheduler.export_schedule(scheduled, "json")
        assert export

    def test_workflow_state_integration(self):
        """Test integration with workflow_state.json"""
        decomposer = TaskDecomposer()

        # Create a temporary workflow file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"tasks": []}, f)
            temp_file = f.name

        try:
            # Create task manager with temp file
            from cli.ar_tasks import TaskManager
            manager = TaskManager(temp_file)

            # Plan a goal
            task = manager.plan_goal("Create a simple API")

            # Verify workflow state was updated
            state = manager._load_workflow_state()
            assert "tasks" in state
            assert len(state["tasks"]) == 1
            assert state["tasks"][0]["id"] == task.id

        finally:
            Path(temp_file).unlink()


def run_tests():
    """Run all tests and report results"""
    print("🧪 Running Planning Pipeline Tests")
    print("=" * 40)

    test_classes = [TestTaskDecomposer, TestPriorityScheduler, TestIntegration]
    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        print("-" * 30)

        instance = test_class()

        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    print(f"✅ {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"❌ {method_name}: {e}")
                    failed += 1

    print("\n🎯 Test Results")
    print("=" * 20)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
