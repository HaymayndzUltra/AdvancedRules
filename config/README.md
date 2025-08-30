# Configuration Directory

This directory contains all configuration files and state management files for the AdvancedRules AI Framework.

## 📁 Configuration Files

### Workflow State Files
- `workflow_state.json` - Current workflow state and progress tracking
- `workflow_state_backup.json` - Backup of workflow state for recovery purposes

### Action Envelopes
- `action_envelope.json` - Action definitions and configurations
- `action_envelope_cmd.json` - Command-based action configurations

### Decision Management
- `decision_candidates.json` - Decision scoring candidates and options
- `rule_attach_log.json` - Rule attachment and execution logs

## 🔧 Usage

These configuration files are used by various components of the framework:

1. **Workflow State**: Tracks the current state of AI persona workflows and maintains progress across sessions
2. **Action Envelopes**: Define available actions and their parameters for the orchestration system
3. **Decision Management**: Supports the decision scoring system and maintains audit logs of rule applications

## ⚠️ Important Notes

- **Do not manually edit** workflow state files while the system is running
- Always create backups before modifying configuration files
- The `rule_attach_log.json` contains important audit information and should be preserved

## 🔄 File Updates

These files are automatically updated by the framework during operation:
- Workflow states are persisted after each significant operation
- Decision candidates are updated based on context and available options
- Rule attachment logs are appended with each rule application

For more information about the configuration system, see the main documentation in the `docs/` directory.