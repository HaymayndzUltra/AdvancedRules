#!/usr/bin/env python3
"""MDC Rule File Linter - validates .mdc files for completeness and correctness."""
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from glob import glob as glob_match

ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = ROOT / ".cursor/rules"
LINT_REPORT = ROOT / "memory-bank/mdc_lint_report.json"


@dataclass
class LintIssue:
    """Represents a linting issue found in an .mdc file."""
    file: str
    line: int
    severity: str  # "error", "warning", "info"
    category: str  # "frontmatter", "glob", "structure", "reference"
    message: str


@dataclass
class RuleMetadata:
    """Extracted metadata from an .mdc file."""
    description: Optional[str]
    globs: List[str]
    always_apply: bool
    attachments: List[str]
    gates: List[str]
    required_artifacts: List[str]
    actions: List[Dict]


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], int]:
    """Parse YAML frontmatter from .mdc content."""
    lines = content.split('\n')
    if not lines or lines[0] != '---':
        return None, 0
    
    # Find closing ---
    end_idx = -1
    for i in range(1, min(len(lines), 50)):  # Limit search to first 50 lines
        if lines[i] == '---':
            end_idx = i
            break
    
    if end_idx == -1:
        return None, 0
    
    # Parse YAML
    yaml_content = '\n'.join(lines[1:end_idx])
    try:
        data = yaml.safe_load(yaml_content) or {}
        return data, end_idx + 1
    except yaml.YAMLError as e:
        return None, 0


def validate_glob_pattern(pattern: str) -> Tuple[bool, Optional[str]]:
    """Validate a glob pattern."""
    # Check for prohibited patterns
    prohibited = [
        ('/**/**/', 'Double wildcards are redundant'),
        ('../', 'Parent directory traversal not allowed'),
        ('/./', 'Current directory reference is redundant'),
    ]
    
    for prohibited_pattern, reason in prohibited:
        if prohibited_pattern in pattern:
            return False, reason
    
    # Check if pattern is valid
    try:
        # Test glob pattern
        list(glob_match(pattern, recursive=True))
        return True, None
    except Exception as e:
        return False, f"Invalid glob pattern: {e}"


def extract_rule_blocks(content: str) -> List[Dict]:
    """Extract <rule> blocks from .mdc content."""
    rules = []
    pattern = r'<rule>(.*?)</rule>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        rule_data = {}
        # Extract fields
        for line in match.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key in ['name', 'description']:
                    rule_data[key] = value
        
        # Extract actions
        if 'actions:' in match:
            actions_text = match.split('actions:')[1]
            # Simple extraction of action types
            action_types = re.findall(r'type:\s*(\w+)', actions_text)
            rule_data['actions'] = action_types
        
        if rule_data:
            rules.append(rule_data)
    
    return rules


def extract_required_artifacts(content: str) -> List[str]:
    """Extract required artifact paths from .mdc content."""
    artifacts = []
    
    # Pattern 1: memory-bank paths
    mb_pattern = r'memory-bank/[a-zA-Z0-9_/.-]+'
    artifacts.extend(re.findall(mb_pattern, content))
    
    # Pattern 2: must_exist references
    must_exist_pattern = r'must_exist:\s*\[(.*?)\]'
    matches = re.findall(must_exist_pattern, content, re.DOTALL)
    for match in matches:
        # Parse list items
        items = re.findall(r'"([^"]+)"', match)
        artifacts.extend(items)
    
    # Pattern 3: file existence checks in conditions
    file_check_pattern = r'(?:exists|present|required).*?([a-zA-Z0-9_/.-]+\.(?:json|yaml|md|txt))'
    artifacts.extend(re.findall(file_check_pattern, content, re.IGNORECASE))
    
    # Deduplicate and clean
    cleaned = []
    for artifact in artifacts:
        # Remove quotes and whitespace
        clean = artifact.strip().strip('"').strip("'")
        if clean and clean not in cleaned:
            cleaned.append(clean)
    
    return cleaned


def extract_gates(content: str) -> List[str]:
    """Extract gate definitions from .mdc content."""
    gates = []
    
    # Pattern 1: gate names in rule blocks
    gate_pattern = r'gate[s]?:\s*\[(.*?)\]'
    matches = re.findall(gate_pattern, content, re.DOTALL)
    for match in matches:
        items = re.findall(r'"([^"]+)"', match)
        gates.extend(items)
    
    # Pattern 2: named gates
    named_gate_pattern = r'(?:gate|check|validate)_(\w+)'
    gates.extend(re.findall(named_gate_pattern, content))
    
    return list(set(gates))


def lint_mdc_file(file_path: Path) -> Tuple[List[LintIssue], Optional[RuleMetadata]]:
    """Lint a single .mdc file."""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Get relative path for reporting
    try:
        rel_path = str(file_path.relative_to(ROOT))
    except ValueError:
        rel_path = str(file_path)
    
    # Check frontmatter
    frontmatter, content_start = parse_frontmatter(content)
    
    if not frontmatter:
        issues.append(LintIssue(
            file=rel_path,
            line=1,
            severity="error",
            category="frontmatter",
            message="Missing or invalid YAML frontmatter"
        ))
    else:
        # Validate frontmatter fields
        if 'description' not in frontmatter:
            issues.append(LintIssue(
                file=rel_path,
                line=1,
                severity="warning",
                category="frontmatter",
                message="Missing 'description' field in frontmatter"
            ))
        
        # Validate globs
        globs = frontmatter.get('globs', [])
        if isinstance(globs, str):
            globs = [globs]
        
        for glob_pattern in globs:
            valid, error = validate_glob_pattern(glob_pattern)
            if not valid:
                issues.append(LintIssue(
                    file=rel_path,
                    line=1,
                    severity="error",
                    category="glob",
                    message=f"Invalid glob pattern '{glob_pattern}': {error}"
                ))
    
    # Extract metadata
    rule_blocks = extract_rule_blocks(content)
    artifacts = extract_required_artifacts(content)
    gates = extract_gates(content)
    
    # Check for attachment references
    attachments = []
    attach_pattern = r'attach_rules.*?rules:\s*\[(.*?)\]'
    matches = re.findall(attach_pattern, content, re.DOTALL)
    for match in matches:
        items = re.findall(r'"([^"]+\.mdc)"', match)
        attachments.extend(items)
    
    # Validate attachment references exist
    for attachment in attachments:
        attach_path = RULES_DIR / attachment
        if not attach_path.exists():
            line_num = 0
            for i, line in enumerate(lines, 1):
                if attachment in line:
                    line_num = i
                    break
            
            issues.append(LintIssue(
                file=rel_path,
                line=line_num,
                severity="error",
                category="reference",
                message=f"Referenced attachment '{attachment}' does not exist"
            ))
    
    # Check for common issues
    # 1. Empty rule blocks
    if '<rule>' in content and '</rule>' in content:
        for rule in rule_blocks:
            if 'name' not in rule:
                issues.append(LintIssue(
                    file=rel_path,
                    line=0,
                    severity="warning",
                    category="structure",
                    message="Rule block missing 'name' field"
                ))
    
    # 2. Unreachable paths
    for artifact in artifacts:
        if artifact.startswith('/') and not artifact.startswith('/workspace'):
            line_num = 0
            for i, line in enumerate(lines, 1):
                if artifact in line:
                    line_num = i
                    break
            
            issues.append(LintIssue(
                file=rel_path,
                line=line_num,
                severity="warning",
                category="reference",
                message=f"Absolute path '{artifact}' may not be portable"
            ))
    
    # Build metadata
    metadata = RuleMetadata(
        description=frontmatter.get('description') if frontmatter else None,
        globs=globs if frontmatter else [],
        always_apply=frontmatter.get('alwaysApply', False) if frontmatter else False,
        attachments=attachments,
        gates=gates,
        required_artifacts=artifacts,
        actions=[{'type': a} for rule in rule_blocks for a in rule.get('actions', [])]
    )
    
    return issues, metadata


def lint_all_mdc_files() -> Dict:
    """Lint all .mdc files in the rules directory."""
    all_issues = []
    all_metadata = {}
    
    # Find all .mdc files
    mdc_files = list(RULES_DIR.rglob("*.mdc"))
    
    for mdc_file in mdc_files:
        issues, metadata = lint_mdc_file(mdc_file)
        
        if issues:
            all_issues.extend(issues)
        
        if metadata:
            all_metadata[str(mdc_file.relative_to(ROOT))] = asdict(metadata)
    
    # Generate report
    report = {
        "total_files": len(mdc_files),
        "files_with_issues": len(set(i.file for i in all_issues)),
        "total_issues": len(all_issues),
        "errors": len([i for i in all_issues if i.severity == "error"]),
        "warnings": len([i for i in all_issues if i.severity == "warning"]),
        "issues": [asdict(i) for i in all_issues],
        "metadata": all_metadata
    }
    
    return report


def save_lint_report(report: Dict) -> None:
    """Save lint report to file."""
    from tools.io.fs import atomic_write_text
    LINT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(LINT_REPORT, json.dumps(report, indent=2))


def main():
    """Run MDC linter and save report."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Lint .mdc rule files")
    parser.add_argument("--file", help="Lint specific file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    if args.file:
        # Lint single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found")
            return 1
        
        issues, metadata = lint_mdc_file(file_path)
        
        if args.json:
            print(json.dumps({
                "file": str(file_path),
                "issues": [asdict(i) for i in issues],
                "metadata": asdict(metadata) if metadata else None
            }, indent=2))
        else:
            if issues:
                print(f"Issues found in {file_path}:")
                for issue in issues:
                    icon = "❌" if issue.severity == "error" else "⚠️"
                    print(f"  {icon} Line {issue.line}: {issue.message}")
            else:
                print(f"✅ No issues found in {file_path}")
        
        if args.strict:
            return 1 if issues else 0
        else:
            return 1 if any(i.severity == "error" for i in issues) else 0
    
    else:
        # Lint all files
        report = lint_all_mdc_files()
        save_lint_report(report)
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"MDC Lint Report")
            print(f"===============")
            print(f"Total files: {report['total_files']}")
            print(f"Files with issues: {report['files_with_issues']}")
            print(f"Total issues: {report['total_issues']}")
            print(f"  Errors: {report['errors']}")
            print(f"  Warnings: {report['warnings']}")
            
            if report['errors'] > 0:
                print("\n❌ Errors found:")
                for issue in report['issues']:
                    if issue['severity'] == 'error':
                        print(f"  {issue['file']}:{issue['line']} - {issue['message']}")
            
            print(f"\nReport saved to: {LINT_REPORT.relative_to(ROOT)}")
        
        if args.strict:
            return 1 if report['total_issues'] > 0 else 0
        else:
            return 1 if report['errors'] > 0 else 0


if __name__ == "__main__":
    exit(main())