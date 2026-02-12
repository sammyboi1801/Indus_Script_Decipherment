# Sumerian Trade Anchors

This note documents provenance and curation for `trade_anchors.json`.

## Provenance

- The anchors are seed entries curated as a starter lexicon for trade-related interpretation work.
- Terms and glosses are normalized into ASCII transliteration and concise English descriptors.
- Confidence values are heuristic initialization scores in the `[0.0, 1.0]` range.

## Curation Rules

1. JSON must remain strict RFC-8259:
   - no comments,
   - no trailing commas,
   - UTF-8 encoded text.
2. Each anchor must include: `id`, `term`, `gloss`, `domain`, and `confidence`.
3. `id` values should be stable and unique (format: `TA-###`).
4. `confidence` should be a float in the range `[0.0, 1.0]`.
5. Any explanatory rationale belongs in markdown files like this one, not inline in JSON.
