"""
Unit tests for Binary Search implementations.
"""
from models.topic import Topic
from services.scoring import update_topics_scores
from algorithms.binary_search import binary_search_by_value_density, find_minimum_hours_for_target


def test_binary_search_density():
    topics = [
        Topic("1", "A", "High", 1.0, 5, 10, 10.0, 0.0, 10),
        Topic("2", "A", "Med", 2.0, 5, 8, 8.0, 0.0, 8),
        Topic("3", "A", "Low", 4.0, 5, 5, 4.0, 0.0, 5)
    ]
    update_topics_scores(topics)
    # Sorted descending by density
    sorted_topics = sorted(topics, key=lambda t: t.value_density, reverse=True)

    idx = binary_search_by_value_density(sorted_topics, target_density=sorted_topics[1].value_density)
    assert idx >= 0
    assert sorted_topics[idx].value_density >= sorted_topics[1].value_density


def test_binary_search_min_hours():
    topics = [
        Topic("1", "A", "T1", 2.0, 5, 8, 10.0, 0.0, 8),
        Topic("2", "A", "T2", 3.0, 5, 8, 15.0, 0.0, 8),
        Topic("3", "A", "T3", 4.0, 5, 8, 20.0, 0.0, 8)
    ]
    update_topics_scores(topics)

    # We want at least 15 marks
    best_hours, achieved_marks, selection = find_minimum_hours_for_target(
        topics, target_marks=15.0, min_hours=1.0, max_hours=10.0, tolerance=0.5
    )

    assert achieved_marks >= 15.0
    assert best_hours <= 10.0
    assert len(selection) > 0
