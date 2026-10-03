"""
Algorithms package init.
"""
from algorithms.result import OptimizationResult
from algorithms.dynamic_programming import solve_knapsack_dp
from algorithms.greedy import solve_greedy
from algorithms.priority_queue import solve_priority_queue, MaxHeap
from algorithms.dependency_graph import DependencyGraph
from algorithms.binary_search import binary_search_by_value_density, find_minimum_hours_for_target

__all__ = [
    "OptimizationResult",
    "solve_knapsack_dp",
    "solve_greedy",
    "solve_priority_queue",
    "MaxHeap",
    "DependencyGraph",
    "binary_search_by_value_density",
    "find_minimum_hours_for_target"
]
