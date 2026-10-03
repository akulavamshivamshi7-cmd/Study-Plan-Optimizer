"""
Greedy Algorithm for Study Plan Optimization.

Algorithm Description:
----------------------
Calculates the marginal Return-on-Investment (Value Density) for each topic:
    Value Density = Benefit Score / Study Time (Yield per hour)

Topics are sorted in descending order of value density. The algorithm iterates
through the sorted list and greedily admits topics as long as their study time
fits within the remaining time budget.

Complexity:
-----------
- Time Complexity: O(N log N), dominated by the comparison-based sorting step.
- Space Complexity: O(N) to store sorted list and selected subsets.

Trade-off:
----------
Greedy runs very quickly, but because it commits greedily without backtracking,
it may leave unused slack hours that a combination of smaller items could have filled,
sometimes resulting in sub-optimal overall benefit compared to Dynamic Programming.
"""
import time
from typing import List
from models.topic import Topic
from algorithms.result import OptimizationResult


def solve_greedy(
    topics: List[Topic],
    available_hours: float
) -> OptimizationResult:
    """
    Executes the Greedy selection algorithm based on Value Density (Benefit / Study Time).

    Args:
        topics: List of candidate Topic objects
        available_hours: Study time budget constraint

    Returns:
        OptimizationResult containing selected items and execution metrics.
    """
    start_time = time.perf_counter()
    logs: List[str] = []

    if available_hours <= 0 or not topics:
        return OptimizationResult(
            algorithm_name="Greedy (Value Density)",
            selected_topics=[],
            unselected_topics=list(topics),
            total_study_time=0.0,
            available_hours=available_hours,
            total_benefit=0.0,
            total_expected_marks=0.0,
            execution_time_ms=(time.perf_counter() - start_time) * 1000,
            time_complexity="O(N log N)",
            space_complexity="O(N)",
            explanation="Available hours <= 0 or topic list empty.",
            logs=["No study hours allocated."]
        )

    # 1. Sort topics by Value Density in descending order
    # In case of tie, sort by higher expected marks, then lower study time
    sorted_topics = sorted(
        topics,
        key=lambda t: (t.value_density, t.expected_marks, -t.study_time),
        reverse=True
    )

    logs.append(f"Sorted {len(sorted_topics)} topics by Value Density (Benefit / Hour) descending.")

    selected_topics: List[Topic] = []
    unselected_topics: List[Topic] = []
    current_time = 0.0

    # 2. Iterate and greedily select
    for idx, topic in enumerate(sorted_topics):
        if round(current_time + topic.study_time, 2) <= round(available_hours, 2):
            current_time += topic.study_time
            selected_topics.append(topic)
            logs.append(
                f"[ACCEPTED] Rank #{idx + 1}: '{topic.name}' | Density: {topic.value_density:.2f}/hr | "
                f"Time: {topic.study_time}h | Cumulative: {current_time:.1f}/{available_hours:.1f}h"
            )
        else:
            unselected_topics.append(topic)
            remaining_slack = available_hours - current_time
            logs.append(
                f"[REJECTED] Rank #{idx + 1}: '{topic.name}' | Needs {topic.study_time}h but only "
                f"{remaining_slack:.1f}h slack remains."
            )

    total_time = sum(t.study_time for t in selected_topics)
    total_benefit = sum(t.benefit_score for t in selected_topics)
    total_marks = sum(t.expected_marks for t in selected_topics)

    runtime_ms = (time.perf_counter() - start_time) * 1000

    explanation = (
        f"Greedy prioritized topics by yield per hour (Value Density). "
        f"Selected {len(selected_topics)} topics utilizing {total_time:.1f}/{available_hours:.1f} hours "
        f"with total benefit {total_benefit:.2f} in {runtime_ms:.3f} ms."
    )

    return OptimizationResult(
        algorithm_name="Greedy (Value Density)",
        selected_topics=selected_topics,
        unselected_topics=unselected_topics,
        total_study_time=round(total_time, 2),
        available_hours=available_hours,
        total_benefit=round(total_benefit, 2),
        total_expected_marks=round(total_marks, 2),
        execution_time_ms=runtime_ms,
        time_complexity=f"O(N log N) ~ O({len(topics)} log {len(topics)})",
        space_complexity=f"O(N) ~ {len(topics)} items",
        explanation=explanation,
        logs=logs
    )
