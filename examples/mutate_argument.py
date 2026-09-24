def normalize_scores(scores: list[float]) -> None:
    """Scale scores into the 0..1 range, in place."""
    lo, hi = min(scores), max(scores)
    span = (hi - lo) or 1.0
    for i, value in enumerate(scores):
        scores[i] = (value - lo) / span
    scores.append(sum(scores) / len(scores))
