# Execution Orchestrator
# Core controller for AdvancedRules AI framework

## Purpose
Central coordination hub that manages AI persona activation, workflow execution, and system state management.

## Core Responsibilities
- **Persona Management**: Activate/deactivate AI roles based on task requirements
- **Workflow Orchestration**: Coordinate multi-step processes across different AI personas
- **State Persistence**: Maintain context and memory across execution cycles
- **Quality Gates**: Enforce validation checkpoints before proceeding
- **Resource Allocation**: Manage computational and memory resources

## Execution Flow
1. **Task Analysis**: Parse incoming requirements and determine required personas
2. **Persona Activation**: Load appropriate AI roles with domain context
3. **Workflow Execution**: Execute tasks through activated personas
4. **Validation**: Apply quality gates and validation checkpoints
5. **Handoff**: Pass control to next persona or complete execution

## Configuration
```yaml
execution_modes:
  sequential: "Execute personas in strict order"
  parallel: "Execute compatible personas simultaneously"
  adaptive: "Dynamically adjust based on task complexity"

quality_gates:
  - security_validation
  - code_quality_check
  - performance_benchmark
  - accessibility_compliance
```

## Integration Points
- Framework Memory Bridge
- Rules Master Toggle
- All AI Personas
- Memory Bank
- External APIs and tools
description:
globs:
alwaysApply: true
---
