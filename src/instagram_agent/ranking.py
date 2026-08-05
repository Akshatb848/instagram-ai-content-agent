from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreInputs:
    recency: float
    authority: float
    relevance: float
    usefulness: float
    originality: float
    evidence: float
    visual: float
    misinformation_risk: float
    copyright_risk: float


WEIGHTS = {
    "recency": 0.14,
    "authority": 0.16,
    "relevance": 0.15,
    "usefulness": 0.13,
    "originality": 0.10,
    "evidence": 0.17,
    "visual": 0.08,
    "misinformation_risk": -0.04,
    "copyright_risk": -0.03,
}


def calculate_score(inputs: ScoreInputs) -> tuple[float, dict[str, float]]:
    values = vars(inputs)
    if any(value < 0 or value > 100 for value in values.values()):
        raise ValueError("Scores must be between 0 and 100")
    contributions = {name: round(values[name] * weight, 4) for name, weight in WEIGHTS.items()}
    return round(max(0.0, min(100.0, sum(contributions.values()))), 4), contributions
