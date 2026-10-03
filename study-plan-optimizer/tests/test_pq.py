"""
Unit tests for MaxHeap and Priority Queue optimization.
"""
from models.topic import Topic
from services.scoring import update_topics_scores
from algorithms.priority_queue import MaxHeap, solve_priority_queue


def test_max_heap_properties():
    heap = MaxHeap()
    t1 = Topic("1", "S", "Low", 2.0, 5, 5, 5.0, 50.0, 5)
    t2 = Topic("2", "S", "High", 2.0, 5, 10, 20.0, 10.0, 10)
    t3 = Topic("3", "S", "Medium", 2.0, 5, 7, 10.0, 30.0, 7)

    heap.insert((1.5, 5), t1)
    heap.insert((5.0, 10), t2)
    heap.insert((3.0, 7), t3)

    assert len(heap) == 3
    # Peek must be the maximum
    peeked = heap.peek()
    assert peeked[1].name == "High"

    # Extract max must return in descending order
    first = heap.extract_max()
    assert first[1].name == "High"

    second = heap.extract_max()
    assert second[1].name == "Medium"

    third = heap.extract_max()
    assert third[1].name == "Low"

    assert heap.is_empty()


def test_priority_queue_solver():
    topics = [
        Topic("1", "A", "T1", 2.0, 5, 8, 10.0, 30.0, 8),
        Topic("2", "A", "T2", 3.0, 8, 10, 15.0, 20.0, 9),
        Topic("3", "A", "T3", 1.5, 4, 6, 6.0, 60.0, 6)
    ]
    update_topics_scores(topics)

    res = solve_priority_queue(topics, available_hours=4.0)

    assert res.total_study_time <= 4.0
    assert len(res.selected_topics) >= 1
    assert res.heap_trace is not None
    assert len(res.heap_trace) > 0
