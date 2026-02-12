from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_seal_fields_flow_into_hypothesis_scorer(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]

    extractor = _load_module(
        repo_root / "scripts/02_vision_pipeline/seal_context_extractor.py",
        "seal_context_extractor",
    )
    assembler_mod = _load_module(
        repo_root / "scripts/03_linguistic_kb/context_assembler.py",
        "context_assembler",
    )
    scorer_mod = _load_module(
        repo_root / "scripts/05_multimodal_fusion/hypothesis_scorer.py",
        "hypothesis_scorer",
    )

    raw_analysis = json.loads((repo_root / "tests/fixtures/seal_analysis_raw.json").read_text())
    output_path = tmp_path / "seal_contexts.json"
    extractor.persist_seal_contexts(raw_analysis, output_path=output_path)

    assembler = assembler_mod.ContextAssembler(seal_context_path=output_path)
    context = assembler.get_sign_context(sign="𐨀", inscription_id="M-101")

    assert context["seal_context"]["primary_animal"] == "zebu"
    assert context["seal_context"]["water_motifs_present"] is False
    assert context["seal_context"]["astronomical_motifs"] == ["crescent"]

    scorer = scorer_mod.HypothesisScorer()
    hypothesis = {
        "id": "H-ZEBU",
        "expected_primary_animal": "zebu",
        "requires_water_motif": False,
        "expected_astronomical_motif": "crescent",
    }
    scored = scorer.score_hypothesis(hypothesis, context)

    assert scored["seal_context_used"]["primary_animal"] == "zebu"
    assert scored["components"]["seal"] > 0
