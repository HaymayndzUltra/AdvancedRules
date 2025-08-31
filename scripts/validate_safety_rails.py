#!/usr/bin/env python3
"""
AdvancedRules v2 Safety Rails Validator
Validates all safety constraints and scaffolding components
"""

import json
import yaml
import os
import sys
from pathlib import Path

class SafetyRailsValidator:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.errors = []
        self.warnings = []

    def log_error(self, message: str):
        """Log an error that prevents validation"""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """Log a warning that should be reviewed"""
        self.warnings.append(message)
        print(f"⚠️  {message}")

    def log_success(self, message: str):
        """Log a successful validation"""
        print(f"✅ {message}")

    def validate_json_files(self):
        """Validate all JSON schema files and envelope v2"""
        print("\n🔍 Validating JSON Schemas and Envelopes")
        print("-" * 40)

        json_files = [
            "schemas/task_schema.json",
            "schemas/flow_schema.json",
            "schemas/memory_doc_schema.json",
            "schemas/metrics_schema.json",
            "tools/envelopes/action_envelope_v2.json"
        ]

        for file_path in json_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                self.log_error(f"Missing required file: {file_path}")
                continue

            try:
                with open(full_path, 'r') as f:
                    json.load(f)
                self.log_success(f"{file_path}")
            except json.JSONDecodeError as e:
                self.log_error(f"Invalid JSON in {file_path}: {e}")
            except Exception as e:
                self.log_error(f"Error reading {file_path}: {e}")

    def validate_yaml_config(self):
        """Validate YAML configuration file"""
        print("\n🔍 Validating YAML Configuration")
        print("-" * 35)

        config_path = self.root_dir / "config" / "advanced_rules.yaml"
        if not config_path.exists():
            self.log_error("Missing config/advanced_rules.yaml")
            return None

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.log_success("config/advanced_rules.yaml")
            return config
        except yaml.YAMLError as e:
            self.log_error(f"Invalid YAML in config/advanced_rules.yaml: {e}")
            return None
        except Exception as e:
            self.log_error(f"Error reading config file: {e}")
            return None

    def validate_safety_gates(self, config: dict):
        """Validate safety gate configurations"""
        print("\n🛡️  Validating Safety Gates")
        print("-" * 25)

        required_safety_settings = {
            "safety.dry_run_default": True,
            "safety.human_approval_required": True,
            "safety.branch_only_workflow": True
        }

        for setting_path, expected_value in required_safety_settings.items():
            keys = setting_path.split('.')
            value = config
            try:
                for key in keys:
                    value = value[key]
                if value == expected_value:
                    self.log_success(f"{setting_path} = {expected_value}")
                else:
                    self.log_error(f"{setting_path} should be {expected_value}, got {value}")
            except KeyError:
                self.log_error(f"Missing required setting: {setting_path}")

        # Check protected paths
        if "safety" in config and "protected_paths" in config["safety"]:
            protected_paths = config["safety"]["protected_paths"]
            if len(protected_paths) > 0:
                self.log_success(f"Protected paths configured ({len(protected_paths)} paths)")
            else:
                self.log_warning("No protected paths configured")
        else:
            self.log_error("Missing protected_paths configuration")

    def validate_feature_flags(self, config: dict):
        """Validate feature flags are conservatively set"""
        print("\n🚩 Validating Feature Flags")
        print("-" * 25)

        if "features" not in config:
            self.log_error("Missing features section in config")
            return

        features = config["features"]
        disabled_features = []
        enabled_features = []

        for feature, enabled in features.items():
            if enabled:
                enabled_features.append(feature)
            else:
                disabled_features.append(feature)

        if enabled_features:
            self.log_warning(f"Features enabled: {', '.join(enabled_features)}")
        else:
            self.log_success("All features disabled (conservative default)")

        if disabled_features:
            self.log_success(f"Features properly disabled: {', '.join(disabled_features)}")

    def validate_envelope_compatibility(self):
        """Validate envelope v2 backwards compatibility"""
        print("\n📬 Validating Envelope Compatibility")
        print("-" * 35)

        v1_path = self.root_dir / "tools" / "envelopes" / "action_envelope.json"
        v2_path = self.root_dir / "tools" / "envelopes" / "action_envelope_v2.json"

        if not v1_path.exists():
            self.log_warning("Original action_envelope.json not found - skipping compatibility test")
            return

        if not v2_path.exists():
            self.log_error("action_envelope_v2.json not found")
            return

        try:
            with open(v1_path, 'r') as f:
                v1_data = json.load(f)
            with open(v2_path, 'r') as f:
                v2_data = json.load(f)

            # Check for shared keys (backwards compatibility)
            v1_keys = set(v1_data.keys())
            v2_keys = set(v2_data.keys())
            shared_keys = v1_keys & v2_keys
            compatibility_ratio = len(shared_keys) / len(v1_keys) if v1_keys else 0

            print(f"Envelope v2 backwards compatible: {len(shared_keys)}/{len(v1_keys)} keys match ({compatibility_ratio:.1%})")

            if compatibility_ratio >= 0.8:
                self.log_success("Backwards compatibility maintained")
            else:
                self.log_warning("Partial backwards compatibility - review envelope v2 design")

            # Check for new tracking fields
            new_fields = ["flow_id", "task_id", "step_id"]
            missing_new_fields = [field for field in new_fields if field not in v2_data]
            if missing_new_fields:
                self.log_warning(f"Missing new tracking fields in v2: {missing_new_fields}")
            else:
                self.log_success("New tracking fields (flow_id, task_id, step_id) present")

        except Exception as e:
            self.log_error(f"Compatibility test failed: {e}")

    def validate_git_workflow(self):
        """Validate git workflow safety"""
        print("\n🌳 Validating Git Workflow")
        print("-" * 25)

        try:
            import subprocess
            result = subprocess.run(["git", "branch", "--show-current"],
                                  capture_output=True, text=True, cwd=self.root_dir)
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                if current_branch in ["main", "master"]:
                    self.log_warning(f"Currently on protected branch: {current_branch}")
                    self.log_warning("Consider switching to feature branch for development")
                else:
                    self.log_success(f"On feature branch: {current_branch}")
            else:
                self.log_warning("Not in a git repository")
        except Exception as e:
            self.log_warning(f"Could not check git status: {e}")

    def generate_report(self):
        """Generate final validation report"""
        print("\n🎯 Validation Report")
        print("=" * 20)

        if not self.errors and not self.warnings:
            print("✅ ALL VALIDATIONS PASSED")
            print("🛡️  Safety rails are properly configured")
            return True
        else:
            if self.errors:
                print(f"❌ {len(self.errors)} ERRORS found:")
                for error in self.errors:
                    print(f"   • {error}")

            if self.warnings:
                print(f"⚠️  {len(self.warnings)} WARNINGS:")
                for warning in self.warnings:
                    print(f"   • {warning}")

            return len(self.errors) == 0

    def run_full_validation(self):
        """Run complete validation suite"""
        print("🛡️  AdvancedRules v2 Safety Rails Validator")
        print("=" * 45)

        # Phase 1: File structure validation
        self.validate_json_files()

        # Phase 2: Configuration validation
        config = self.validate_yaml_config()
        if config:
            self.validate_safety_gates(config)
            self.validate_feature_flags(config)

        # Phase 3: Compatibility validation
        self.validate_envelope_compatibility()

        # Phase 4: Workflow validation
        self.validate_git_workflow()

        # Phase 5: Final report
        return self.generate_report()


def main():
    validator = SafetyRailsValidator()
    success = validator.run_full_validation()

    if success:
        print("\n🚀 SCAFFOLDING VALIDATION COMPLETE")
        print("Ready for safe deployment with conservative defaults")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED")
        print("Address errors before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()
