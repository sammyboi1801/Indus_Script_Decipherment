"""Utilities for scoring multimodal decipherment hypotheses."""

from __future__ import annotations


def score_visual_match(match_type: str) -> float:
    """Return visual-match confidence.

    Exact visual matches score 0.95, partial visual matches score 0.75,
    and non-matches (or unknown labels) score 0.30.
    """
    normalized = (match_type or "").strip().lower()

    if normalized == "exact":
        visual_match = 0.95
    elif normalized == "partial":
        visual_match = 0.75
    else:
        visual_match = 0.30

    return visual_match
