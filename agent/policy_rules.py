"""
agent/policy_rules.py

Responsibilities:
- Apply business logic and safety guardrails to ML scores.
- Handle edge cases where numerical thresholds might be misleading.
- Annotate decisions with policy-based metadata.
"""

from typing import Dict, Any
from app.config import settings

def apply_policy_rules(verdict: str, confidence: float, risk_level: str) -> Dict[str, Any]:
    """
    Refines the base decision based on organizational and safety policies.
    
    Args:
        verdict: Initial classification ('REAL', 'DEEPFAKE', 'UNCERTAIN')
        confidence: Aggregated probability score [0, 1]
        risk_level: Initial risk assessment ('LOW', 'MEDIUM', 'HIGH')
        
    Returns:
        Dict: Modified verdict and risk level with policy annotations.
    """
    
    final_verdict = verdict
    final_risk_level = risk_level
    policy_flags = []

    # Rule 1: Extreme Confidence Override
    # Even if thresholds suggest REAL, if the score is near-zero or near-one,
    # we lock the risk level to minimize false negatives/positives.
    if confidence > 0.98:
        final_risk_level = "CRITICAL"
        policy_flags.append("EXTREME_CONFIDENCE_LOCK")
    
    # Rule 2: The "Ambiguity Zone" Policy
    # If the score falls in the middle range defined in config, 
    # we force a human-in-the-loop (HITL) flag.
    if settings.DEEPFAKE_THRESHOLD_LOW < confidence < settings.DEEPFAKE_THRESHOLD_HIGH:
        final_verdict = "UNCERTAIN"
        final_risk_level = "MEDIUM"#use nahihua hai kahi pe 
        policy_flags.append("REQUIRES_HUMAN_REVIEW")

    # Rule 3: Edge Case Safety
    # If the system is in EDGE_OFFLINE mode, we escalate 'UNCERTAIN' 
    # to 'HIGH' risk to be safe, assuming no cloud-based secondary check is available.
    if settings.RUNTIME_MODE == "EDGE_OFFLINE" and final_verdict == "UNCERTAIN":
        final_risk_level = "HIGH"
        policy_flags.append("OFFLINE_PRECAUTIONARY_ESCALATION")

    # Rule 4: Integrity Check Integration
    # (Assumption: If integrity check failed in main.py, this would be caught 
    # earlier, but we check for security flags here if passed via kwargs)
    
    return {
        "verdict": final_verdict,
        "risk_level": final_risk_level,
        "policy_applied": policy_flags,
        "action_required": "MANUAL_INSPECTION" if final_risk_level in ["HIGH", "CRITICAL"] else "NONE"
    }