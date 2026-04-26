from typing import Dict

# Scoring Constants
SCORING_WEIGHTS = {
    "ride_completed": 2.5,
    "cancellation_late": -5.0,
    "cancellation_early": -1.0,
    "verification_step": 10.0,
    "positive_rating": 1.0,
    "negative_rating": -3.0,
    "complaint_resolved": -10.0
}

def calculate_new_score(current_score: float, event_type: str, weight_multiplier: float = 1.0) -> float:
    """
    Calculate the new trust score based on an event.
    Score is bounded between 0 and 100.
    """
    delta = SCORING_WEIGHTS.get(event_type, 0) * weight_multiplier
    new_score = current_score + delta
    return max(0.0, min(100.0, new_score))

def get_trust_tier(score: float) -> Dict[str, str]:
    """Return trust tier and associated benefits."""
    if score >= 90:
        return {"tier": "Elite", "color": "purple", "auto_approval": True}
    elif score >= 75:
        return {"tier": "Trusted", "color": "green", "auto_approval": False}
    elif score >= 50:
        return {"tier": "Neutral", "color": "blue", "auto_approval": False}
    else:
        return {"tier": "Probation", "color": "red", "auto_approval": False, "restrictions": True}
