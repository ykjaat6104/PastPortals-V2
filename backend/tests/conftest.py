"""Pytest bootstrap for backend tests.

Ensures both the repository root and the backend package directory are on
sys.path so tests can import backend.* and legacy utils.* modules when pytest
is launched from inside backend/.
"""
from __future__ import annotations

import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

for path in (PROJECT_ROOT, BACKEND_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)