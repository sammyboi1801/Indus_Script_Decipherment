"""Extract and persist normalized seal analysis context."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from seal_context_schema import DEFAULT_SEAL_CONTEXT

DEFAULT_SEAL_CONTEXT_PATH = Path("data/ivs/features/seal_contexts.json")


def normalize_seal_analysis(inscription_id: str, analysis: dict[str, Any]) -> dict[str, Any]:
    """Convert variable vision outputs into the canonical seal-context shape."""

    water = analysis.get("water_motifs_present")
    if water is None:
        water = analysis.get("has_water")

    astronomical = analysis.get("astronomical_motifs")
    if astronomical is None:
        astronomical = analysis.get("celestial_symbols", [])

    primary_animal = analysis.get("primary_animal")
    if primary_animal is None:
        primary_animal = analysis.get("dominant_animal")

    normalized = {
        **DEFAULT_SEAL_CONTEXT,
        "inscription_id": inscription_id,
        "water_motifs_present": water,
        "astronomical_motifs": list(astronomical or []),
        "primary_animal": primary_animal,
        "secondary_animals": list(analysis.get("secondary_animals", [])),
        "motif_density": analysis.get("motif_density"),
        "seal_condition": analysis.get("seal_condition"),
        "confidence": analysis.get("confidence"),
    }
    return normalized


def persist_seal_contexts(
    raw_analysis_by_inscription: dict[str, dict[str, Any]],
    output_path: Path = DEFAULT_SEAL_CONTEXT_PATH,
) -> dict[str, dict[str, Any]]:
    """Persist canonical seal context entries keyed by inscription_id."""

    contexts = {
        inscription_id: normalize_seal_analysis(inscription_id, analysis)
        for inscription_id, analysis in raw_analysis_by_inscription.items()
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(contexts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return contexts


def load_seal_contexts(path: Path = DEFAULT_SEAL_CONTEXT_PATH) -> dict[str, dict[str, Any]]:
    """Read persisted seal contexts; return an empty map when file is absent."""

    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
