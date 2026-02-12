#!/usr/bin/env python3
"""Compute Markov-style sign statistics from token sequences.

Key format contract (used consistently across emitted fields):
- Bigrams use: "<sign_1>|<sign_2>"  (example: "M1|M305")
- Trigrams use: "<sign_1>|<sign_2>|<sign_3>"  (example: "M1|M305|M89")

This string key format is used for:
- `bigrams`
- `trigrams`
- `transition_probs`

`position_counts` is emitted as a plain nested dictionary of shape:
{sign_id: {position: count}}
where all keys are strings and all counts are ints.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

DELIMITER = "|"


def make_ngram_key(signs: Sequence[str]) -> str:
    """Create a stable string key for an n-gram using `DELIMITER`."""
    return DELIMITER.join(str(sign) for sign in signs)


def normalize_sequences(raw: object) -> List[List[str]]:
    """Normalize supported JSON shapes into `List[List[str]]`.

    Supported inputs:
    - [["M1", "M305", ...], ...]
    - {"sequences": [[...], ...]}
    """
    if isinstance(raw, dict):
        sequences = raw.get("sequences")
    else:
        sequences = raw

    if not isinstance(sequences, list):
        raise ValueError("Input JSON must be a list of sequences or a dict with `sequences`.")

    normalized: List[List[str]] = []
    for idx, seq in enumerate(sequences):
        if not isinstance(seq, list):
            raise ValueError(f"Sequence at index {idx} is not a list.")
        normalized.append([str(token) for token in seq])
    return normalized


def compute_markov_stats(sequences: Iterable[Sequence[str]]) -> Dict[str, object]:
    """Compute unigram, bigram, trigram, transition probabilities, and positions."""
    unigram_counts: Counter[str] = Counter()
    bigram_counts: Counter[Tuple[str, str]] = Counter()
    trigram_counts: Counter[Tuple[str, str, str]] = Counter()

    # sign_id -> Counter(position -> count)
    position_counts: defaultdict[str, Counter[int]] = defaultdict(Counter)

    for seq in sequences:
        if not seq:
            continue

        unigram_counts.update(seq)

        for position, sign in enumerate(seq):
            position_counts[sign][position] += 1

        for i in range(len(seq) - 1):
            pair = (seq[i], seq[i + 1])
            bigram_counts[pair] += 1

        for i in range(len(seq) - 2):
            triple = (seq[i], seq[i + 1], seq[i + 2])
            trigram_counts[triple] += 1

    # Use one stable key format across related outputs.
    bigrams = {make_ngram_key(k): int(v) for k, v in bigram_counts.items()}
    trigrams = {make_ngram_key(k): int(v) for k, v in trigram_counts.items()}

    transition_probs: Dict[str, float] = {}
    for pair, count in bigram_counts.items():
        source_sign = pair[0]
        denom = unigram_counts[source_sign]
        transition_probs[make_ngram_key(pair)] = float(count / denom) if denom else 0.0

    # Convert defaultdict(Counter) -> plain nested dictionaries with string keys.
    serialized_position_counts: Dict[str, Dict[str, int]] = {
        str(sign_id): {str(position): int(count) for position, count in counter.items()}
        for sign_id, counter in position_counts.items()
    }

    payload: Dict[str, object] = {
        "unigrams": {str(k): int(v) for k, v in unigram_counts.items()},
        "bigrams": bigrams,
        "trigrams": trigrams,
        "transition_probs": transition_probs,
        "position_counts": serialized_position_counts,
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path, help="Input JSON containing sign sequences.")
    parser.add_argument("output_json", type=Path, help="Path to write computed Markov payload JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw = json.loads(args.input_json.read_text(encoding="utf-8"))
    sequences = normalize_sequences(raw)
    payload = compute_markov_stats(sequences)

    # Validation step before writing: ensure payload is JSON-serializable.
    json.dumps(payload)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
