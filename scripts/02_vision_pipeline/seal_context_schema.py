"""Canonical seal-context schema shared across the pipeline."""

from __future__ import annotations

CANONICAL_SEAL_CONTEXT_KEYS = (
    "inscription_id",
    "water_motifs_present",
    "astronomical_motifs",
    "primary_animal",
    "secondary_animals",
    "motif_density",
    "seal_condition",
    "confidence",
)

DEFAULT_SEAL_CONTEXT = {
    "water_motifs_present": None,
    "astronomical_motifs": [],
    "primary_animal": None,
    "secondary_animals": [],
    "motif_density": None,
    "seal_condition": None,
    "confidence": None,
}
