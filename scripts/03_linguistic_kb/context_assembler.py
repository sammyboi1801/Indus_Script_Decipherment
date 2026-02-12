"""Build multimodal context used by downstream scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SEAL_CONTEXT_FIELDS = (
    "water_motifs_present",
    "astronomical_motifs",
    "primary_animal",
    "secondary_animals",
    "motif_density",
    "seal_condition",
    "confidence",
)


class ContextAssembler:
    """Assemble sign context from linguistic and vision-derived sources."""

    def __init__(self, seal_context_path: str | Path = "data/ivs/features/seal_contexts.json") -> None:
        self.seal_context_path = Path(seal_context_path)
        self._seal_contexts = self._load_seal_contexts()

    def _load_seal_contexts(self) -> dict[str, dict[str, Any]]:
        if not self.seal_context_path.exists():
            return {}
        return json.loads(self.seal_context_path.read_text(encoding="utf-8"))

    def get_sign_context(
        self,
        sign: str,
        inscription_id: str | None = None,
        base_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return assembled context for a sign and optional inscription."""

        ctx: dict[str, Any] = dict(base_context or {})
        ctx.setdefault("sign", sign)
        ctx.setdefault("seal_context", {})

        if inscription_id:
            record = self._seal_contexts.get(inscription_id, {})
            seal_ctx = ctx["seal_context"]
            for field in SEAL_CONTEXT_FIELDS:
                if field in record and record[field] is not None:
                    seal_ctx[field] = record[field]
            seal_ctx.setdefault("inscription_id", inscription_id)
        return ctx
