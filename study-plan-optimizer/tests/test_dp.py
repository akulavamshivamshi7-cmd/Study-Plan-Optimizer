"""
Unit tests for 0/1 Knapsack Dynamic Programming algorithm.
"""
from models.topic import Topic
from services.scoring import update_topics_scores
from algorithms.dynamic_programming import solve_knapsack_dp


def get_test_topics():
    topics = [
        Topic("1", "CS", "Item A", 2.0, 5, 8, 10.0, 20.0, 8), # high marks, 2h
        Topic("2", "CS", "Item B", 3.0, 5, 8, 14.0, 20.0, 8), # higher marks, 3h
        Topic("3", "CS", "Item C", 4.0, 5, 8, 16.0, 20.0, 8), # 4h
        Topic("4", "CS", "Item D", 1.0, 5, 8, 5.0, 20.0, 8)   # 1h
    ]
    return update_topics_scores(topics)


def test_dp_optimal_selection():
    topics = get_test_topics()
    # Available hours: 5.0
    # Best combination of 5h: Item A (2h) + Item B (3h) or others that maximize total benefit
    result = solve_knapsack_dp(topics, available_hours=5.0)

    assert result.total_study_time <= 5.0
    assert len(result.selected_topics) >= 1
    assert result.total_benefit > 0
    # DP table must be generated
    assert result.dp_table is not None


def test_dp_zero_hours():
    topics = get_test_topics()
    result = solve_knapsack_dp(topics, available_hours=0.0)
    assert len(result.selected_topics) == 0
    assert result.total_study_time == 0.0
    assert result.total_benefit == 0.0


def test_dp_excess_hours():
    topics = get_test_topics()
    total_time = sum(t.study_time for t in topics)
    result = solve_knapsack_dp(topics, available_hours=total_time + 10.0)
    # When available hours exceed all topics, all topics should be selected
    assert len(result.selected_topics) == len(topics)
    assert abs(result.total_study_time - total_time) < 0.01


def test_dp_empty_topics():
    result = solve_knapsack_dp([], available_hours=10.0)
    assert len(result.selected_topics) == 0
    assert result.total_benefit == 0.0
