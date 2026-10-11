"""Final decision logic (frozen). Pure Python so it can be unit-tested."""

CONFIDENT = 20      # IVP verified points >= this -> confident match
POSSIBLE = 6        # IVP verified points >= this -> uncertain zone
AI_AGREE = 0.5      # AI confidence needed to upgrade an uncertain IVP result
AI_LED = 0.7        # AI confidence needed to lead when IVP found nothing

# Folder names used in the demo dataset -> for cross-referencing
DEMO_CATEGORY = {
    "confident_both_agree": "1_confident_match_both_agree",
    "confident_ivp_alone": "1_confident_match_ivp_alone",
    "possible_upgraded_by_ai": "2_possible_upgraded_by_ai",
    "possible_ivp_led": "3_possible_ai_disagrees",
    "possible_ai_led": "4_low_ivp_ai_confident",
    "new_leopard": "5_new_leopard_both_uncertain",
    "exact_record": "exact_record",
}


def decide(ivp_score, ivp_leopard, ai_leopard, ai_conf):
    if ivp_leopard and ivp_score >= CONFIDENT:
        agrees = (ai_leopard == ivp_leopard)
        return dict(decision="MATCH", path="confident_both_agree" if agrees else "confident_ivp_alone",
                    confidence_level="high", leopard_id=ivp_leopard, ai_agrees=agrees)
    if ivp_leopard and ivp_score >= POSSIBLE:
        if ai_leopard == ivp_leopard and ai_conf >= AI_AGREE:
            return dict(decision="MATCH", path="possible_upgraded_by_ai",
                        confidence_level="high", leopard_id=ivp_leopard, ai_agrees=True)
        return dict(decision="POSSIBLE_MATCH", path="possible_ivp_led",
                    confidence_level="medium", leopard_id=ivp_leopard, ai_agrees=False)
    if ai_leopard and ai_conf >= AI_LED:
        return dict(decision="POSSIBLE_MATCH", path="possible_ai_led",
                    confidence_level="medium", leopard_id=ai_leopard, ai_agrees=None)
    return dict(decision="NEW_LEOPARD", path="new_leopard",
                confidence_level="new", leopard_id=None, ai_agrees=None)
