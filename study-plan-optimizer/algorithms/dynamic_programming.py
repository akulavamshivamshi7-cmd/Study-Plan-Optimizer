"""
Dynamic Programming (0/1 Knapsack) Implementation for Study Plan Optimization.

Algorithm Description:
----------------------
The 0/1 Knapsack problem is solved using a 2D dynamic programming table `dp[i][w]`,
where `dp[i][w]` represents the maximum expected benefit achievable using a subset of the
first `i` topics with a total study time capacity of `w` units.

Recurrence Relation:
-------------------
For each topic `i` (1 to N) with scaled study time `weight[i]` and `benefit[i]`:
- If weight[i] > w:
      dp[i][w] = dp[i-1][w]   (Topic cannot fit in remaining capacity)
- Else:
      dp[i][w] = max(dp[i-1][w], dp[i-1][w - weight[i]] + benefit[i])

Reconstruction (Backtracking):
------------------------------
Starting from dp[N][W], we trace backwards:
If dp[i][w] != dp[i-1][w], topic `i` was selected, and we transition to w = w - weight[i].
Otherwise, topic `i` was skipped.

Complexity:
-----------
- Time Complexity: O(N * W), where N is number of topics and W is scaled available hours.
- Space Complexity: O(N * W) for 2D DP memoization table.
"""
import time
from typing import List, Tuple
from models.topic import Topic
from algorithms.result import OptimizationResult


def solve_knapsack_dp(
    topics: List[Topic],
    available_hours: float,
    time_granularity: float = 0.5
) -> OptimizationResult:
    """
    Solves 0/1 Knapsack optimization using a 2D Dynamic Programming table.

    Args:
        topics: List of Topic candidates
        available_hours: Total available study hours budget
        time_granularity: Step size in hours for discretizing time (default 0.5h)

    Returns:
        OptimizationResult containing optimal topic subset, metrics, and DP table.
    """
    start_time = time.perf_counter()
    logs: List[str] = []

    if available_hours <= 0 or not topics:
        return OptimizationResult(
            algorithm_name="Dynamic Programming (0/1 Knapsack)",
            selected_topics=[],
            unselected_topics=list(topics),
            total_study_time=0.0,
            available_hours=available_hours,
            total_benefit=0.0,
            total_expected_marks=0.0,
            execution_time_ms=(time.perf_counter() - start_time) * 1000,
            time_complexity="O(N * W)",
            space_complexity="O(N * W)",
            explanation="Available hours <= 0 or topic list empty. No topics selected.",
            logs=["Study budget is 0 or empty topic list."]
        )

    # 1. Discretize continuous study hours into integer weights
    scale = int(round(1.0 / time_granularity))
    W = int(round(available_hours * scale))
    N = len(topics)

    weights: List[int] = []
    benefits: List[float] = []

    for t in topics:
        # Scale to integer weight, minimum 1 discrete unit
        w_scaled = max(1, int(round(t.study_time * scale)))
        weights.append(w_scaled)
        benefits.append(float(t.benefit_score))

    logs.append(f"Discretized {N} topics into scale factor {scale} (Granularity: {time_granularity} hrs).")
    logs.append(f"Integer capacity W = {W} units (representing {available_hours:.1f} hours).")

    # 2. Initialize 2D DP table: size (N + 1) x (W + 1)
    dp = [[0.0 for _ in range(W + 1)] for _ in range(N + 1)]

    # 3. Fill DP table iteratively
    for i in range(1, N + 1):
        item_w = weights[i - 1]
        item_b = benefits[i - 1]
        for w in range(W + 1):
            if item_w <= w:
                include_val = dp[i - 1][w - item_w] + item_b
                exclude_val = dp[i - 1][w]
                dp[i][w] = include_val if include_val > exclude_val else exclude_val
            else:
                dp[i][w] = dp[i - 1][w]

    # 4. Backtrack to reconstruct the optimal subset
    selected_indices = []
    curr_w = W
    for i in range(N, 0, -1):
        # If value changed from previous row, item was included
        if abs(dp[i][curr_w] - dp[i - 1][curr_w]) > 1e-6:
            selected_indices.append(i - 1)
            curr_w -= weights[i - 1]
            logs.append(f"Backtracking: Selected '{topics[i - 1].name}' (Benefit: {benefits[i-1]:.2f}, Weight: {topics[i - 1].study_time} hrs)")

    # Backtracked in reverse order, reverse to restore original sequence
    selected_indices.reverse()
    selected_set = set(selected_indices)

    selected_topics = [topics[idx] for idx in selected_indices]
    unselected_topics = [topics[idx] for idx in range(N) if idx not in selected_set]

    total_time = sum(t.study_time for t in selected_topics)
    total_benefit = sum(t.benefit_score for t in selected_topics)
    total_marks = sum(t.expected_marks for t in selected_topics)

    runtime_ms = (time.perf_counter() - start_time) * 1000

    # Subsample DP table for visualization if W is large (e.g. max 20 columns)
    col_step = max(1, W // 15)
    sampled_w_indices = list(range(0, W + 1, col_step))
    if W not in sampled_w_indices:
        sampled_w_indices.append(W)

    dp_subtable = []
    for row in dp:
        dp_subtable.append([round(row[w_idx], 2) for w_idx in sampled_w_indices])

    dp_weight_labels = [round(w_idx / scale, 1) for w_idx in sampled_w_indices]
    dp_topic_labels = ["Initial (0 items)"] + [t.name[:20] for t in topics]

    explanation = (
        f"Dynamic Programming evaluated all combinations pseudo-polynomially across an "
        f"({N} x {W}) grid. Globally optimal solution found with total benefit {total_benefit:.2f} "
        f"and total study time {total_time:.1f}/{available_hours:.1f} hours."
    )

    return OptimizationResult(
        algorithm_name="Dynamic Programming (0/1 Knapsack)",
        selected_topics=selected_topics,
        unselected_topics=unselected_topics,
        total_study_time=round(total_time, 2),
        available_hours=available_hours,
        total_benefit=round(total_benefit, 2),
        total_expected_marks=round(total_marks, 2),
        execution_time_ms=runtime_ms,
        time_complexity=f"O(N * W) ~ O({N} * {W}) = {N * W:,} ops",
        space_complexity=f"O(N * W) ~ {N + 1}x{W + 1} grid",
        explanation=explanation,
        logs=logs,
        dp_table=dp_subtable,
        dp_weight_labels=dp_weight_labels,
        dp_topic_labels=dp_topic_labels
    )
