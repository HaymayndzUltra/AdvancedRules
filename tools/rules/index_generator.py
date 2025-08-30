#!/usr/bin/env python3
"""Generate machine-readable index of .mdc rules for runtime consumption."""
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set
from tools.rules.mdc_linter import parse_frontmatter, extract_rule_blocks, extract_required_artifacts, extract_gates

ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = ROOT / ".cursor/rules"
RULES_INDEX = ROOT / "memory-bank/rules_index.json"


def build_rules_index() -> Dict:
    """Build comprehensive index of all .mdc rules."""
    index = {
        "version": "1.0",
        "rules": {},
        "gates": {},
        "artifacts": {},
        "attachments": {},
        "glob_mappings": {},
        "always_apply": []
    }
    
    # Process all .mdc files
    mdc_files = list(RULES_DIR.rglob("*.mdc"))
    
    for mdc_file in mdc_files:
        try:
            content = mdc_file.read_text(encoding='utf-8')
            rel_path = str(mdc_file.relative_to(ROOT))
            
            # Parse frontmatter
            frontmatter, _ = parse_frontmatter(content)
            if not frontmatter:
                continue
            
            # Extract components
            rule_blocks = extract_rule_blocks(content)
            artifacts = extract_required_artifacts(content)
            gates = extract_gates(content)
            
            # Build rule entry
            rule_entry = {
                "file": rel_path,
                "description": frontmatter.get('description', ''),
                "globs": frontmatter.get('globs', []),
                "always_apply": frontmatter.get('alwaysApply', False),
                "rules": rule_blocks,
                "gates": gates,
                "required_artifacts": artifacts
            }
            
            # Add to main index
            rule_id = mdc_file.stem  # Use filename without extension as ID
            index["rules"][rule_id] = rule_entry
            
            # Track always-apply rules
            if rule_entry["always_apply"]:
                index["always_apply"].append(rule_id)
            
            # Build reverse mappings
            # Gates -> Rules mapping
            for gate in gates:
                if gate not in index["gates"]:
                    index["gates"][gate] = []
                index["gates"][gate].append(rule_id)
            
            # Artifacts -> Rules mapping
            for artifact in artifacts:
                if artifact not in index["artifacts"]:
                    index["artifacts"][artifact] = []
                index["artifacts"][artifact].append(rule_id)
            
            # Glob -> Rules mapping
            for glob_pattern in rule_entry["globs"]:
                if glob_pattern not in index["glob_mappings"]:
                    index["glob_mappings"][glob_pattern] = []
                index["glob_mappings"][glob_pattern].append(rule_id)
            
            # Process attachments
            attach_refs = []
            if 'attach_rules' in content:
                import re
                # Look for attach_rules in actions - handle both bracket and dash syntax
                # Pattern 1: Bracket syntax [...]
                attach_pattern1 = r'attach_rules.*?rules:\s*\[(.*?)\]'
                matches1 = re.findall(attach_pattern1, content, re.DOTALL)
                for match in matches1:
                    items = re.findall(r'["\']*([^"\',\s]+\.mdc)["\']*', match)
                    attach_refs.extend(items)
                
                # Pattern 2: YAML dash syntax - "file.mdc"
                attach_pattern2 = r'rules:\s*\n(?:\s*-\s*["\']*([^"\'\n]+\.mdc)["\']*\n?)+'
                matches2 = re.findall(attach_pattern2, content, re.MULTILINE)
                attach_refs.extend(matches2)
            
            if attach_refs:
                # Deduplicate
                attach_refs = list(set(attach_refs))
                index["attachments"][rule_id] = attach_refs
                
        except Exception as e:
            print(f"Error processing {mdc_file}: {e}")
            continue
    
    # Add statistics
    index["statistics"] = {
        "total_rules": len(index["rules"]),
        "total_gates": len(index["gates"]),
        "total_artifacts": len(index["artifacts"]),
        "always_apply_count": len(index["always_apply"])
    }
    
    return index


def find_applicable_rules(context: Dict, index: Dict) -> List[str]:
    """Find rules applicable to given context."""
    applicable = set()
    
    # Always apply rules
    applicable.update(index.get("always_apply", []))
    
    # Check glob matches
    if "files" in context:
        for file_path in context["files"]:
            for glob_pattern, rule_ids in index.get("glob_mappings", {}).items():
                from pathlib import Path
                if Path(file_path).match(glob_pattern):
                    applicable.update(rule_ids)
    
    # Check artifact presence
    if "artifacts" in context:
        for artifact in context["artifacts"]:
            if artifact in index.get("artifacts", {}):
                applicable.update(index["artifacts"][artifact])
    
    # Check gate requirements
    if "gates" in context:
        for gate in context["gates"]:
            if gate in index.get("gates", {}):
                applicable.update(index["gates"][gate])
    
    return list(applicable)


def get_required_artifacts_for_rules(rule_ids: List[str], index: Dict) -> Set[str]:
    """Get all required artifacts for a set of rules."""
    artifacts = set()
    
    for rule_id in rule_ids:
        if rule_id in index.get("rules", {}):
            rule = index["rules"][rule_id]
            artifacts.update(rule.get("required_artifacts", []))
    
    return artifacts


def get_gates_for_rules(rule_ids: List[str], index: Dict) -> Set[str]:
    """Get all gates defined by a set of rules."""
    gates = set()
    
    for rule_id in rule_ids:
        if rule_id in index.get("rules", {}):
            rule = index["rules"][rule_id]
            gates.update(rule.get("gates", []))
    
    return gates


def check_runtime_parity(index: Dict) -> Dict:
    """Check parity between documented requirements and runtime."""
    parity_report = {
        "matches": [],
        "mismatches": [],
        "missing_in_runtime": [],
        "missing_in_docs": []
    }
    
    # Load registry to check against runtime
    registry_path = ROOT / ".cursor/commands/registry.yaml"
    if registry_path.exists():
        with open(registry_path) as f:
            registry = yaml.safe_load(f)
        
        # Extract runtime requirements
        runtime_artifacts = set()
        runtime_gates = set()
        
        for command in registry.get("commands", []):
            # Get must_exist requirements
            contexts = command.get("contexts", {})
            must_exist = contexts.get("must_exist", [])
            runtime_artifacts.update(must_exist)
            
            # Get gate requirements
            gates = contexts.get("gates", [])
            runtime_gates.update(gates)
        
        # Compare with documented requirements
        doc_artifacts = set()
        doc_gates = set()
        
        for rule in index["rules"].values():
            doc_artifacts.update(rule.get("required_artifacts", []))
            doc_gates.update(rule.get("gates", []))
        
        # Find matches and mismatches
        artifact_matches = runtime_artifacts & doc_artifacts
        artifact_missing_runtime = doc_artifacts - runtime_artifacts
        artifact_missing_docs = runtime_artifacts - doc_artifacts
        
        gate_matches = runtime_gates & doc_gates
        gate_missing_runtime = doc_gates - runtime_gates
        gate_missing_docs = runtime_gates - doc_gates
        
        parity_report["matches"] = {
            "artifacts": list(artifact_matches),
            "gates": list(gate_matches)
        }
        
        parity_report["missing_in_runtime"] = {
            "artifacts": list(artifact_missing_runtime),
            "gates": list(gate_missing_runtime)
        }
        
        parity_report["missing_in_docs"] = {
            "artifacts": list(artifact_missing_docs),
            "gates": list(gate_missing_docs)
        }
        
        # Calculate parity score
        total_items = len(doc_artifacts) + len(doc_gates) + len(runtime_artifacts) + len(runtime_gates)
        matched_items = len(artifact_matches) * 2 + len(gate_matches) * 2
        
        parity_report["parity_score"] = matched_items / total_items if total_items > 0 else 1.0
        parity_report["parity_passed"] = parity_report["parity_score"] >= 0.8
    
    return parity_report


def save_rules_index(index: Dict) -> None:
    """Save rules index to file."""
    from tools.io.fs import atomic_write_text
    RULES_INDEX.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(RULES_INDEX, json.dumps(index, indent=2))


def main():
    """Generate rules index and check parity."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate rules index")
    parser.add_argument("--check-parity", action="store_true", help="Check runtime parity")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--query", help="Query rules for context (JSON)")
    
    args = parser.parse_args()
    
    # Build index
    index = build_rules_index()
    save_rules_index(index)
    
    if args.query:
        # Query mode
        context = json.loads(args.query)
        applicable = find_applicable_rules(context, index)
        artifacts = get_required_artifacts_for_rules(applicable, index)
        gates = get_gates_for_rules(applicable, index)
        
        result = {
            "applicable_rules": applicable,
            "required_artifacts": list(artifacts),
            "gates": list(gates)
        }
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Applicable rules: {', '.join(applicable)}")
            print(f"Required artifacts: {', '.join(artifacts)}")
            print(f"Gates: {', '.join(gates)}")
    
    elif args.check_parity:
        # Parity check mode
        parity = check_runtime_parity(index)
        
        if args.json:
            print(json.dumps(parity, indent=2))
        else:
            print(f"Runtime Parity Check")
            print(f"====================")
            print(f"Parity Score: {parity.get('parity_score', 0):.2%}")
            print(f"Status: {'✅ PASSED' if parity.get('parity_passed') else '❌ FAILED'}")
            
            if parity.get('missing_in_runtime'):
                print(f"\nMissing in Runtime:")
                for category, items in parity['missing_in_runtime'].items():
                    if items:
                        print(f"  {category}: {', '.join(items[:5])}")
            
            if parity.get('missing_in_docs'):
                print(f"\nMissing in Documentation:")
                for category, items in parity['missing_in_docs'].items():
                    if items:
                        print(f"  {category}: {', '.join(items[:5])}")
    
    else:
        # Default: show summary
        if args.json:
            print(json.dumps(index, indent=2))
        else:
            print(f"Rules Index Generated")
            print(f"====================")
            print(f"Total rules: {index['statistics']['total_rules']}")
            print(f"Total gates: {index['statistics']['total_gates']}")
            print(f"Total artifacts: {index['statistics']['total_artifacts']}")
            print(f"Always-apply rules: {index['statistics']['always_apply_count']}")
            print(f"\nIndex saved to: {RULES_INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()