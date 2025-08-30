#!/usr/bin/env python3
"""
Minimal setup.py for backward compatibility and to ensure CLI entry points work.
Configuration is primarily in pyproject.toml.
"""
from setuptools import setup

# The actual configuration is in pyproject.toml
# This file exists for compatibility with older pip versions
# and to ensure the CLI entry points are properly registered

if __name__ == "__main__":
    setup()