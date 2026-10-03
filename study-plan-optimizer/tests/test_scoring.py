"""
Unit tests for scoring and benefit calculations.
"""
import pytest
from models.topic import Topic
from services.scoring import compute_benefit_score, ScoringWeights, update_topics_scores


def test_benefit_score_basic():
    t = Topic(
        id="T01",
        subject="DSA",
        name="Dynamic Programming",
        study_time=3.0,
        difficulty=8,
        importance=10,
        expected_marks=15.0,
        current_prep=30.0,
        priority=10
    )
    score = compute_benefit_score(t)
    assert score > 0
    # Expected: 15 * 0.70 * 1.0 * 1.0 * (1 + 0.2*(8-5)/10) = 15 * 0.7 * 1.06 = ~11.13
    assert 10.0 <= score <= 13.0


def test_benefit_score_fully_prepared():
    t = Topic(
        id="T02",
        subject="DSA",
        name="Arrays",
        study_time=2.0,
        difficulty=3,
        importance=5,
        expected_marks=10.0,
        current_prep=100.0,
        priority=5
    )
    # Even if 100% prepared, revision yield provides small baseline
    score = compute_benefit_score(t)
    assert 0.0 < score < 1.0


def test_benefit_score_zero_prep():
    t = Topic(
        id="T03",
        subject="OS",
        name="Deadlocks",
        study_time=3.0,
        difficulty=5,
        importance=10,
        expected_marks=10.0,
        current_prep=0.0,
        priority=10
    )
    score = compute_benefit_score(t)
    # 10 * 1.0 * 1.0 * 1.0 * 1.0 = 10.0
    assert abs(score - 10.0) < 0.1


def test_update_topics_scores():
    topics = [
        Topic("1", "A", "T1", 2.0, 5, 10, 10.0, 50.0, 10),
        Topic("2", "A", "T2", 1.0, 5, 10, 10.0, 50.0, 10)
    ]
    update_topics_scores(topics)
    assert topics[0].benefit_score > 0
    assert topics[1].benefit_score > 0
    # Topic 2 has half the study time, so value density should be roughly double
    assert topics[1].value_density > topics[0].value_density
