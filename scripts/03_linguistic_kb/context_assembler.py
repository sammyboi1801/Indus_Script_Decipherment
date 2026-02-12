"""Utilities for assembling sign-context payloads for linguistic prompts.

This module computes transition evidence for *all* occurrences of a sign in a
sequence and preserves backward-compatible fields expected by older callers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from statistics import mean
from typing import Any


def _lookup_transition_probability(
    transition_stats: Mapping[Any, Any] | None,
    current_sign: Any,
    next_sign: Any,
) -> float | None:
    """Best-effort lookup for transition probability in heterogeneous mappings.

    Supported `transition_stats` shapes include:
    - {(current, next): probability}
    - {current: {next: probability}}
    - {"current": {"next": probability}}
    """
    if transition_stats is None:
        return None

    if (current_sign, next_sign) in transition_stats:
        value = transition_stats[(current_sign, next_sign)]
        return float(value) if value is not None else None

    current_bucket = transition_stats.get(current_sign)
    if isinstance(current_bucket, Mapping) and next_sign in current_bucket:
        value = current_bucket[next_sign]
        return float(value) if value is not None else None

    current_bucket = transition_stats.get(str(current_sign))
    if isinstance(current_bucket, Mapping) and str(next_sign) in current_bucket:
        value = current_bucket[str(next_sign)]
        return float(value) if value is not None else None

    return None


def _aggregate_probabilities(values: Sequence[float], method: str) -> float | None:
    if not values:
        return None
    if method == "max":
        return max(values)
    return mean(values)


def get_sign_context(
    sign_id: Any,
    sequence: Sequence[Any] | None,
    transition_stats: Mapping[Any, Any] | None = None,
    aggregate_method: str = "mean",
) -> dict[str, Any]:
    """Build context payload for a sign across all its occurrences in sequence.

    Backward-compatible keys are retained (`sign_id`, `follows`,
    `follows_prob`), while richer fields are added (`occurrence_indices`,
    `transition_evidence`, `follows_prob_per_occurrence`).
    """
    if not sequence:
        return {
            "sign_id": sign_id,
            "sequence": sequence,
            "occurrence_indices": [],
            "follows": None,
            "follows_prob": None,
            "follows_prob_per_occurrence": [],
            "transition_evidence": {
                "aggregate_method": aggregate_method,
                "aggregate_probability": None,
                "available_probability_count": 0,
                "occurrences": [],
                "notes": "No sequence data provided.",
            },
        }

    occurrence_indices = [idx for idx, token in enumerate(sequence) if token == sign_id]

    occurrence_rows: list[dict[str, Any]] = []
    follows: list[Any] = []
    follows_prob_per_occurrence: list[float | None] = []

    for idx in occurrence_indices:
        next_sign = sequence[idx + 1] if idx + 1 < len(sequence) else None
        prob = (
            _lookup_transition_probability(transition_stats, sign_id, next_sign)
            if next_sign is not None
            else None
        )

        follows.append(next_sign)
        follows_prob_per_occurrence.append(prob)
        occurrence_rows.append(
            {
                "index": idx,
                "next_sign": next_sign,
                "transition_probability": prob,
            }
        )

    valid_probs = [p for p in follows_prob_per_occurrence if p is not None]
    aggregate_probability = _aggregate_probabilities(valid_probs, aggregate_method)

    if not occurrence_rows:
        follows_value: Any = None
    elif len(occurrence_rows) == 1:
        follows_value = occurrence_rows[0]["next_sign"]
    else:
        follows_value = follows

    return {
        "sign_id": sign_id,
        "sequence": sequence,
        "occurrence_indices": occurrence_indices,
        "follows": follows_value,
        # Backward compatibility: keep legacy scalar/nullable field.
        "follows_prob": aggregate_probability,
        # New richer representation.
        "follows_prob_per_occurrence": follows_prob_per_occurrence,
        "transition_evidence": {
            "aggregate_method": aggregate_method,
            "aggregate_probability": aggregate_probability,
            "available_probability_count": len(valid_probs),
            "occurrences": occurrence_rows,
        },
    }


def build_transition_prompt_fragment(sign_context: Mapping[str, Any]) -> str:
    """Render transition evidence for prompt-generation consumers.

    Handles both legacy `follows_prob` payloads and richer
    `transition_evidence`/`follows_prob_per_occurrence` payloads.
    """
    sign_id = sign_context.get("sign_id")
    evidence = sign_context.get("transition_evidence")

    if isinstance(evidence, Mapping):
        method = evidence.get("aggregate_method", "mean")
        aggregate_probability = evidence.get("aggregate_probability")
        occurrence_rows = evidence.get("occurrences", []) or []
        lines = [
            f"Sign {sign_id}: aggregate follow-transition probability "
            f"({method}) = {aggregate_probability}."
        ]
        if occurrence_rows:
            lines.append("Per occurrence:")
            for row in occurrence_rows:
                lines.append(
                    "- index={index}, next_sign={next_sign}, p={transition_probability}".format(
                        **row
                    )
                )
        return "\n".join(lines)

    return (
        f"Sign {sign_id}: follow-transition probability = "
        f"{sign_context.get('follows_prob')}"
    )
