"""Score hypotheses against assembled multimodal context."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class HypothesisScorer:
    """Simple heuristic scorer with seal-context component."""

    def score_hypothesis(self, hypothesis: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        seal_context = context.get("seal_context") or {}
        seal_component = self._seal_score(hypothesis, seal_context)
        return {
            "total_score": seal_component,
            "components": {"seal": seal_component},
            "seal_context_used": seal_context,
        }

    def _seal_score(self, hypothesis: dict[str, Any], seal_context: dict[str, Any] | None) -> float:
        """Score seal compatibility; return neutral score when context is absent."""

        if not seal_context:
            logger.info("Neutral seal score: no seal context provided.")
            return 0.0

        score = 0.0

        expected_animal = hypothesis.get("expected_primary_animal")
        observed_animal = seal_context.get("primary_animal")
        if expected_animal:
            if observed_animal is None:
                logger.info(
                    "Neutral animal contribution for hypothesis %s: primary_animal missing.",
                    hypothesis.get("id", "<unknown>"),
                )
            elif expected_animal == observed_animal:
                score += 1.0
            else:
                score -= 0.5

        wants_water = hypothesis.get("requires_water_motif")
        water = seal_context.get("water_motifs_present")
        if wants_water is not None:
            if water is None:
                logger.info(
                    "Neutral water contribution for hypothesis %s: water_motifs_present missing.",
                    hypothesis.get("id", "<unknown>"),
                )
            elif bool(water) == bool(wants_water):
                score += 0.5
            else:
                score -= 0.25

        astro_reference = hypothesis.get("expected_astronomical_motif")
        astronomical_motifs = seal_context.get("astronomical_motifs") or []
        if astro_reference:
            if not astronomical_motifs:
                logger.info(
                    "Neutral astronomy contribution for hypothesis %s: astronomical_motifs missing/empty.",
                    hypothesis.get("id", "<unknown>"),
                )
            elif astro_reference in astronomical_motifs:
                score += 0.5
            else:
                score -= 0.25

        return score
