#!/usr/bin/env python3
import json
import sys
import unicodedata
from pathlib import Path

import re
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / ".cursor/commands/registry.yaml"
SCHEMA_PATH = ROOT / "schemas/registry.schema.json"
REPORT_PATH = ROOT / "registry_report.json"


def to_kebab_ascii(s: str) -> str:
    # Normalize unicode → ASCII, lower, replace non-alnum with '-'
    # Preserve separators for common unicode arrows/dashes
    s = s.replace("→", "-").replace("—", "-").replace("–", "-")
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    import re
    ascii_str = ascii_str.lower()
    ascii_str = re.sub(r"[^a-z0-9]+", "-", ascii_str).strip("-")
    return ascii_str


def main() -> int:
    if not REG_PATH.exists():
        print(f"Missing registry: {REG_PATH}")
        return 1

    # Load YAML (ignore heredoc line if present)
    raw = REG_PATH.read_text(encoding="utf-8").splitlines()
    # Strip heredoc preface and sentinel if present
    if raw and raw[0].startswith("cat > ") and "<<'YAML'" in raw[0]:
        # drop first line and trailing sentinel line 'YAML'
        raw = raw[1:]
        if raw and raw[-1].strip() == "YAML":
            raw = raw[:-1]
    data = yaml.safe_load("\n".join(raw))

    # Normalize IDs to kebab ascii and add aliases if necessary
    seen = set()
    problems = []
    for cmd in data.get("commands", []):
        original_id = cmd.get("id", "")
        norm_id = to_kebab_ascii(original_id)
        if not norm_id:
            problems.append({"id": original_id, "error": "empty_normalized_id"})
            continue
        # If current id lacks separators but an alias provides clearer kebab form, prefer that
        candidate_norm = norm_id
        aliases = cmd.get("aliases", [])
        hyphenated_aliases = []
        for al in aliases:
            al_norm = to_kebab_ascii(al)
            if al_norm and ("-" in al_norm) and al_norm != candidate_norm:
                hyphenated_aliases.append(al_norm)
        if ("-" not in candidate_norm) and hyphenated_aliases:
            # pick the longest alias norm (most tokens)
            candidate_norm = sorted(hyphenated_aliases, key=len, reverse=True)[0]

        norm_id = candidate_norm
        if norm_id in seen:
            problems.append({"id": original_id, "normalized": norm_id, "error": "duplicate_normalized_id"})
        seen.add(norm_id)
        if original_id != norm_id:
            # Preserve original as alias and set normalized id
            aliases = cmd.get("aliases", [])
            if original_id not in aliases:
                aliases.append(original_id)
            cmd["aliases"] = aliases
            cmd["id"] = norm_id

    # Validate against schema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    report = {
        "ok": len(errors) == 0 and len([p for p in problems if p.get("error")]) == 0,
        "problems": problems,
        "errors": [
            {
                "path": "/" + "/".join(str(p) for p in err.path),
                "message": err.message,
                "validator": err.validator,
            }
            for err in errors
        ],
        "ids": [
            {
                "id": cmd.get("id"),
                "aliases": cmd.get("aliases", []),
                "label": (cmd.get("ui") or {}).get("label"),
            }
            for cmd in data.get("commands", [])
        ],
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if report["ok"]:
        print("OK: registry valid and normalized →", REPORT_PATH)
        # Overwrite normalized registry
        (ROOT / ".cursor/commands/registry.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8"
        )
        return 0
    else:
        print("FAIL: registry has issues →", REPORT_PATH)
        return 2


if __name__ == "__main__":
    sys.exit(main())

