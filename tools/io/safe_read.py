#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

from tools.io.fs import read_text, recover_file


def safe_read_json(path: Path, auto_recover: bool = True) -> Dict[str, Any] | None:
    """Safely read JSON with automatic recovery on failure.
    
    Returns parsed JSON or None if unrecoverable.
    """
    try:
        content = read_text(path)
        if not content:
            if auto_recover and recover_file(path):
                content = read_text(path)
            if not content:
                return None
        return json.loads(content)
    except json.JSONDecodeError:
        if auto_recover and recover_file(path):
            try:
                content = read_text(path)
                return json.loads(content)
            except Exception:
                pass
    except Exception:
        pass
    return None


def safe_read_text(path: Path, auto_recover: bool = True) -> str:
    """Safely read text with automatic recovery on empty/missing.
    
    Returns content or empty string if unrecoverable.
    """
    content = read_text(path)
    if not content and auto_recover:
        if recover_file(path):
            content = read_text(path)
    return content