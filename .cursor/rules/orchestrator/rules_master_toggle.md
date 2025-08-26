# Rules Master Toggle
# Central control system for AdvancedRules framework activation

## Purpose
Provides centralized control over which AI personas, domain rules, and execution modes are currently active in the system.

## Control Mechanisms
- **Persona Activation**: Enable/disable specific AI roles based on current needs
- **Rule Set Selection**: Choose appropriate rule sets for different project types
- **Execution Mode Control**: Switch between development, testing, and production modes
- **Feature Flags**: Toggle advanced features and experimental capabilities
- **Access Control**: Manage permissions for different user roles

## Toggle States
```yaml
system_states:
  development:
    personas: ["product_owner", "planning", "codegen", "qa"]
    rules: ["clean_code", "code_quality", "testing"]
    mode: "iterative"
    
  production:
    personas: ["auditor", "security", "observability"]
    rules: ["security", "performance", "monitoring"]
    mode: "strict"
    
  maintenance:
    personas: ["principal_engineer", "documentation"]
    rules: ["documentation", "maintenance"]
    mode: "conservative"
```

## Dynamic Configuration
```typescript
interface MasterToggle {
  activatePersona(personaId: string): Promise<void>;
  deactivatePersona(personaId: string): Promise<void>;
  setExecutionMode(mode: ExecutionMode): Promise<void>;
  toggleFeature(featureId: string, enabled: boolean): Promise<void>;
  getActiveConfiguration(): Promise<ActiveConfig>;
  validateConfiguration(config: ActiveConfig): Promise<ValidationResult>;
}
```

## Safety Features
- **Rollback Protection**: Prevent dangerous configuration changes
- **Validation Gates**: Ensure configuration consistency before activation
- **Audit Logging**: Track all toggle changes with full context
- **Emergency Override**: Quick access to safe default configuration
- **Dependency Checking**: Validate persona and rule dependencies

## Integration
- Controls execution orchestrator behavior
- Manages framework memory bridge access
- Coordinates with all AI personas
- Provides configuration API for external tools
description:
globs:
alwaysApply: true
---
