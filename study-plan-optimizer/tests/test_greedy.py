"""
Unit tests for Greedy optimization algorithm.
"""
from models.topic import Topic
from services.scoring import update_topics_scores
from algorithms.greedy import solve_greedy


def test_greedy_selection():
    topics = [
        Topic("1", "A", "High Yield", 1.0, 5, 10, 20.0, 0.0, 10),  # Very high density
        Topic("2", "A", "Medium Yield", 2.0, 5, 8, 10.0, 20.0, 8),
        Topic("3", "A", "Low Yield", 5.0, 5, 5, 5.0, 50.0, 5)
    ]
    update_topics_scores(topics)

    result = solve_greedy(topics, available_hours=3.0)

    assert result.total_study_time <= 3.0
    # High yield must be chosen first
    assert any(t.name == "High Yield" for t in result.selected_topics)
    assert len(result.logs) > 0


def test_greedy_equal_density():
    # Two topics with identical density
    topics = [
        Topic("1", "A", "T1", 2.0, 5, 10, 10.0, 0.0, 10),
        Topic("2", "A", "T2", 2.0, 5, 10, 10.0, 0.0, 10)
    ]
    update_topics_scores(topics)
    result = solve_greedy(topics, available_hours=2.0)

    # Fits exactly 1 topic
    assert len(result.selected_topics) == 1
    assert result.total_study_time == 2.0
