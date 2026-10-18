"""
AI Reasoning & Moderation Service.

Evaluates citizen reasoning submissions to ensure they contain substantive, evidence-backed
arguments rather than baseless slander, defamation, or generic spam.
Enforces the governance guardrails discussed in the architecture framework.
"""

import re
from typing import List, Tuple
from models.review import AIReasoningAssessment


class AIReasoningModerator:
    def __init__(self):
        # Defamation & ungrounded emotional attack indicators
        self.defamation_patterns = [
            r"\b(thieves|chor|looters|scammers|criminals|jail them|frauds|bribe takers)\b",
            r"\b(corrupt dogs|bloodsuckers|hang them|kill them)\b",
        ]

        # Substantive infrastructure audit keywords
        self.technical_substantive_keywords = [
            "bitumen", "tar", "asphalt", "aggregate", "curing", "drainage",
            "pothole", "cracks", "sub-base", "thickness", "slope", "culvert",
            "delay", "months", "deadline", "equipment", "roller", "paver",
            "traffic", "monsoon", "waterlogging", "quality", "test", "grade",
            "flyover", "girder", "expansion joint", "pavement", "wearing course"
        ]

    def evaluate_reasoning(self, text: str) -> AIReasoningAssessment:
        """
        Analyzes the submitted text and returns a structured AI quality assessment.
        """
        cleaned = text.strip()
        words = re.findall(r"\w+", cleaned.lower())
        word_count = len(words)

        # 1. Defamation check
        contains_defamation = False
        for pat in self.defamation_patterns:
            if re.search(pat, cleaned, re.IGNORECASE):
                contains_defamation = True
                break

        # 2. Substantive technical vocabulary check
        matched_technical_terms = [
            kw for kw in self.technical_substantive_keywords if kw in cleaned.lower()
        ]
        cites_metrics = len(matched_technical_terms) >= 2 or bool(re.search(r"\d+(\.\d+)?\s*(km|meter|m|cm|crore|cr|month|year)", cleaned, re.IGNORECASE))

        # 3. Substance evaluation
        is_substantive = word_count >= 12 and (cites_metrics or len(matched_technical_terms) >= 1)

        # 4. Score calculation (0 to 100)
        base_score = min(40.0, word_count * 1.5)
        technical_score = min(40.0, len(matched_technical_terms) * 12.0)
        metric_bonus = 20.0 if cites_metrics else 0.0

        raw_score = base_score + technical_score + metric_bonus
        if contains_defamation:
            raw_score = max(0.0, raw_score - 70.0)

        final_score = round(min(100.0, max(0.0, raw_score)), 1)

        # Verdict
        if contains_defamation:
            verdict = "REJECTED"
            sentiment = "DEFAMATORY_OR_ABUSIVE"
            notes = (
                "Rejected by AI Moderator: Contains defamatory, unverified allegations. "
                "Constructive, evidence-backed critique is required."
            )
        elif final_score < 45.0:
            verdict = "REJECTED"
            sentiment = "INSUFFICIENT_SUBSTANCE"
            notes = (
                "Rejected by AI Moderator: Vague or emotional feedback. "
                "Please describe specific road features, observable defects, or contractor execution details."
            )
        elif final_score < 70.0:
            verdict = "APPROVED"
            sentiment = "OBJECTIVE"
            notes = "Approved: Standard substantive feedback referencing observable road conditions."
        else:
            verdict = "APPROVED"
            sentiment = "HIGH_QUALITY_ANALYTICAL"
            notes = f"Approved: Exemplary analytical feedback citing concrete metrics ({', '.join(matched_technical_terms[:3])})."

        return AIReasoningAssessment(
            is_substantive=is_substantive,
            contains_unsubstantiated_defamation=contains_defamation,
            cites_verifiable_metrics=cites_metrics,
            reasoning_quality_score=final_score,
            sentiment_balance=sentiment,
            moderation_verdict=verdict,
            feedback_notes=notes,
        )
