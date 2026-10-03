"""
Binary Search Algorithms in Study Optimization.

DSA Concepts Implemented:
1. Classic Binary Search (O(log N)):
   Searches for a topic or threshold index in an array sorted by Value Density or Expected Marks.

2. Binary Search on Answer (O(log(Hours/eps) * N * W)):
   Finds the minimal study hours required to achieve a target marks/benefit threshold.
   Monotonic property: If 'H' hours yields >= target_marks, any H' > H also yields >= target_marks.
"""
from typing import List, Optional, Tuple
from models.topic import Topic
from algorithms.dynamic_programming import solve_knapsack_dp


def binary_search_by_value_density(
    sorted_topics: List[Topic],
    target_density: float
) -> int:
    """
    Finds the index of the topic with value density closest to or >= target_density
    in a descending sorted list using classic Binary Search.

    Args:
        sorted_topics: List of topics sorted in descending order of value_density
        target_density: Target density cutoff

    Returns:
        int: Index of matching/boundary element, or -1 if empty.
    """
    if not sorted_topics:
        return -1

    low = 0
    high = len(sorted_topics) - 1
    best_idx = 0

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_topics[mid].value_density

        # Since array is sorted DESCENDING:
        if mid_val >= target_density:
            best_idx = mid
            low = mid + 1 # Look further right for closer match
        else:
            high = mid - 1

    return best_idx


def find_minimum_hours_for_target(
    topics: List[Topic],
    target_marks: float,
    min_hours: float = 1.0,
    max_hours: float = 50.0,
    tolerance: float = 0.5
) -> Tuple[float, float, List[Topic]]:
    """
    Applies 'Binary Search on Answer' to find the minimum study hours
    necessary to achieve the student's target marks improvement.

    Args:
        topics: All available candidate topics
        target_marks: Target marks desired by student
        min_hours: Lower search bound
        max_hours: Upper search bound
        tolerance: Step precision (hours)

    Returns:
        Tuple: (optimal_hours, achieved_marks, selected_topics)
    """
    total_possible_marks = sum(t.expected_marks for t in topics)
    if target_marks > total_possible_marks:
        # Cannot reach target even with infinite hours
        res = solve_knapsack_dp(topics, max_hours)
        return max_hours, res.total_expected_marks, res.selected_topics

    low = min_hours
    high = max_hours
    best_hours = max_hours
    best_marks = 0.0
    best_selection: List[Topic] = []

    # Binary search within [min_hours, max_hours]
    while (high - low) >= tolerance:
        mid = round((low + high) / 2.0, 1)
        res = solve_knapsack_dp(topics, mid, time_granularity=0.5)

        if res.total_expected_marks >= target_marks:
            best_hours = mid
            best_marks = res.total_expected_marks
            best_selection = res.selected_topics
            high = mid # Try to achieve target with fewer hours
        else:
            low = mid + tolerance # Need more hours

    return best_hours, best_marks, best_selection
