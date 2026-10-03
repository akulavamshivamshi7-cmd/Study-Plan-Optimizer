"""
Scoring and Benefit Calculation Service.
Provides mathematically sound, configurable calculation of learning benefit / expected marks improvement.
Also provides explainability generation for why topics are selected or rejected.
"""
from dataclasses import dataclass
from typing import Dict, Any, List
from models.topic import Topic


@dataclass
class ScoringWeights:
    """
    Configurable weights and tuning parameters for scoring formula.
    """
    importance_weight: float = 1.0    # Exponent for importance factor
    prep_gap_weight: float = 1.0      # Exponent for preparation gap factor
    priority_weight: float = 1.0      # Exponent for priority factor
    difficulty_weight: float = 0.2    # Influence of topic difficulty (-0.5 to +0.5)
    base_revision_yield: float = 0.05 # Minimum yield even if prep is high (for revision benefit)


def compute_benefit_score(topic: Topic, weights: ScoringWeights = None) -> float:
    """
    Calculates the Expected Score Improvement / Benefit of studying a topic.

    Formula:
    1. Prep Gap = max((100 - current_prep) / 100, base_revision_yield)
    2. Normalized Importance = (importance / 10.0) ^ importance_weight
    3. Normalized Priority = (priority / 10.0) ^ priority_weight
    4. Difficulty Multiplier = 1.0 + difficulty_weight * ((difficulty - 5.0) / 10.0)
    5. Benefit Score = expected_marks * (Prep Gap ^ prep_gap_weight) * Normalized Importance * Normalized Priority * Difficulty Multiplier

    Returns:
        float: Normalized Expected Benefit Score (rounded to 3 decimal places)
    """
    if weights is None:
        weights = ScoringWeights()

    # Prep gap (0.0 to 1.0), with small baseline for revision
    raw_gap = (100.0 - float(topic.current_prep)) / 100.0
    effective_gap = max(raw_gap, weights.base_revision_yield)
    gap_factor = effective_gap ** weights.prep_gap_weight

    # Normalized attributes
    importance_factor = (max(1.0, float(topic.importance)) / 10.0) ** weights.importance_weight
    priority_factor = (max(1.0, float(topic.priority)) / 10.0) ** weights.priority_weight

    # Difficulty adjustment (centered at 5)
    diff_adjustment = 1.0 + (weights.difficulty_weight * ((float(topic.difficulty) - 5.0) / 10.0))
    diff_adjustment = max(0.5, min(1.5, diff_adjustment)) # clamp between 0.5 and 1.5

    benefit = float(topic.expected_marks) * gap_factor * importance_factor * priority_factor * diff_adjustment
    return max(0.01, round(benefit, 3))


def update_topics_scores(topics: List[Topic], weights: ScoringWeights = None) -> List[Topic]:
    """
    Updates the benefit_score, prep_gap, and value_density for all topics in place.
    """
    if weights is None:
        weights = ScoringWeights()

    for t in topics:
        t.prep_gap = max(0.0, 100.0 - t.current_prep)
        t.benefit_score = compute_benefit_score(t, weights)
        t.value_density = round(t.benefit_score / max(0.1, t.study_time), 3)

    return topics


def explain_topic_selection(topic: Topic, selected: bool, rejection_reason: str = "") -> Dict[str, Any]:
    """
    Generates explainable human-readable justification for why a topic was selected or omitted.
    """
    if selected:
        reasons = []
        if topic.expected_marks >= 12.0:
            reasons.append(f"High exam marks weightage: {topic.expected_marks} marks")
        elif topic.expected_marks >= 8.0:
            reasons.append(f"Moderate marks contribution: {topic.expected_marks} marks")
        else:
            reasons.append(f"Exam contribution: {topic.expected_marks} marks")

        if topic.importance >= 8:
            reasons.append(f"High subject importance: {topic.importance}/10")

        if topic.current_prep <= 40:
            reasons.append(f"Large preparation gap: {topic.prep_gap:.0f}% unmastered (current prep {topic.current_prep:.0f}%)")
        elif topic.current_prep <= 70:
            reasons.append(f"Moderate preparation gap: {topic.prep_gap:.0f}% (current prep {topic.current_prep:.0f}%)")
        else:
            reasons.append(f"Refinement & revision benefit: {topic.prep_gap:.0f}% remaining gap")

        if topic.priority >= 8:
            reasons.append(f"Top exam priority: {topic.priority}/10")

        reasons.append(f"High ROI (Value Density): {topic.value_density:.2f} score yield per study hour")

        return {
            "topic_id": topic.id,
            "topic_name": topic.name,
            "status": "Selected",
            "badge": "SUCCESS",
            "summary": f"Selected for study ({topic.study_time} hrs | +{topic.benefit_score:.1f} benefit)",
            "details": reasons
        }
    else:
        reasons = []
        if rejection_reason:
            reasons.append(rejection_reason)
        else:
            if topic.current_prep >= 75:
                reasons.append(f"Preparation is already high ({topic.current_prep:.0f}%), low marginal improvement")
            if topic.value_density < 2.0:
                reasons.append(f"Lower score yield per hour ({topic.value_density:.2f}/hr) compared to higher-priority alternatives")
            reasons.append(f"Study time budget exhausted; higher value-density topics took precedence")

        return {
            "topic_id": topic.id,
            "topic_name": topic.name,
            "status": "Not Selected",
            "badge": "WARNING",
            "summary": f"Omitted ({topic.study_time} hrs | {topic.benefit_score:.1f} benefit)",
            "details": reasons
        }
