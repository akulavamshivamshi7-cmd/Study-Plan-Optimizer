"""
Unit tests for DependencyGraph, cycle detection, and topological sorting.
"""
from models.topic import Topic
from algorithms.dependency_graph import DependencyGraph


def test_dependency_graph_topological_sort():
    t1 = Topic("T1", "DSA", "Arrays", 2.0, 3, 5, 5.0, 80.0, 5, prerequisites=[])
    t2 = Topic("T2", "DSA", "Linked Lists", 2.0, 4, 6, 8.0, 60.0, 6, prerequisites=["T1"])
    t3 = Topic("T3", "DSA", "Trees", 3.0, 6, 8, 12.0, 40.0, 8, prerequisites=["T2"])
    t4 = Topic("T4", "DSA", "Graphs", 4.0, 8, 9, 15.0, 20.0, 9, prerequisites=["T3"])

    graph = DependencyGraph([t4, t2, t1, t3]) # Passed out of order

    has_cycle, _ = graph.detect_cycle()
    assert has_cycle is False

    sorted_topics = graph.topological_sort()
    sorted_ids = [t.id for t in sorted_topics]

    # Prerequisite must always appear before dependent topic
    assert sorted_ids.index("T1") < sorted_ids.index("T2")
    assert sorted_ids.index("T2") < sorted_ids.index("T3")
    assert sorted_ids.index("T3") < sorted_ids.index("T4")


def test_dependency_graph_cycle_detection():
    # T1 -> T2 -> T3 -> T1 (Cycle!)
    t1 = Topic("T1", "DSA", "A", 2.0, 5, 5, 5.0, 50.0, 5, prerequisites=["T3"])
    t2 = Topic("T2", "DSA", "B", 2.0, 5, 5, 5.0, 50.0, 5, prerequisites=["T1"])
    t3 = Topic("T3", "DSA", "C", 2.0, 5, 5, 5.0, 50.0, 5, prerequisites=["T2"])

    graph = DependencyGraph([t1, t2, t3])
    has_cycle, cycle_nodes = graph.detect_cycle()
    assert has_cycle is True
    assert len(cycle_nodes) == 3


def test_prerequisite_warning():
    t1 = Topic("T1", "DSA", "Arrays", 2.0, 3, 5, 5.0, 20.0, 5, prerequisites=[]) # low prep (20%)
    t2 = Topic("T2", "DSA", "Trees", 3.0, 6, 8, 12.0, 10.0, 8, prerequisites=["T1"])

    graph = DependencyGraph([t1, t2])

    # Only T2 is selected, but its prereq T1 has low prep (20% < 60%)
    warnings = graph.validate_prerequisites_for_selected([t2], prep_threshold=60.0)
    assert len(warnings) == 1
    assert "requires 'Arrays'" in warnings[0]["message"]
