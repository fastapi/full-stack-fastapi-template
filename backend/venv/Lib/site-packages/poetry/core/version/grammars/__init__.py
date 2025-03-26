from __future__ import annotations

from pathlib import Path


GRAMMAR_DIR = Path(__file__).parent

GRAMMAR_PEP_508_CONSTRAINTS = GRAMMAR_DIR / "pep508.lark"

GRAMMAR_PEP_508_MARKERS = GRAMMAR_DIR / "markers.lark"
