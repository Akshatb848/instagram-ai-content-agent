import pytest


@pytest.fixture
def valid_package() -> dict:
    return {
        "topic": "A verified AI update",
        "target_audience_level": "beginner",
        "reel_objective": "Explain a practical update",
        "hook": "This AI update changes one useful workflow.",
        "narration_script": "A concise, evidence-based explanation for a short Reel.",
        "estimated_duration_seconds": 30,
        "scenes": [
            {
                "start_seconds": 0,
                "end_seconds": 30,
                "narration": "Explanation",
                "on_screen_text": "Verified update",
                "visual_type": "kinetic_text",
            }
        ],
        "caption": "A concise explanation with sources.",
        "hashtags": ["#AI"],
        "source_disclosures": ["https://example.com/source"],
        "claims": ["A supported claim"],
        "evidence": [
            {
                "claim": "A supported claim",
                "url": "https://example.com/source",
                "excerpt": "Short evidence",
                "primary_source": True,
                "confidence": 0.95,
            }
        ],
        "unsupported_claims": [],
        "confidence": 0.95,
        "safety_notes": [],
    }
