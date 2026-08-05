from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimEvidence:
    claim: str
    confidence: float
    primary_source: bool
    source_conflict: bool = False


def verify_claims(items: list[ClaimEvidence], threshold: float = 0.8) -> tuple[bool, list[str]]:
    unsupported = [
        item.claim
        for item in items
        if item.source_conflict or not item.primary_source or item.confidence < threshold
    ]
    return not unsupported, unsupported
