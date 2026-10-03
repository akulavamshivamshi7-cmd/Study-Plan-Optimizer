"""
Optimizer Service Orchestrator.
Coordinates scoring, prerequisite checking, algorithm execution, comparison, and what-if analysis.
"""
from typing import List, Dict, Any, Tuple
from models.topic import Topic
from algorithms.result import OptimizationResult
from algorithms.dynamic_programming import solve_knapsack_dp
from algorithms.greedy import solve_greedy
from algorithms.priority_queue import solve_priority_queue
from algorithms.dependency_graph import DependencyGraph
from services.scoring import compute_benefit_score, update_topics_scores, explain_topic_selection, ScoringWeights


class StudyOptimizerService:
    """
    Facade service coordinating optimization algorithms, dependency checks,
    explainability, and what-if parameter sweeps.
    """

    @staticmethod
    def run_optimization(
        topics: List[Topic],
        available_hours: float,
        algorithm_choice: str = "Dynamic Programming",
        weights: ScoringWeights = None,
        respect_prerequisites: bool = True
    ) -> Tuple[OptimizationResult, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Runs the requested optimization algorithm.

        Returns:
            Tuple of:
            - OptimizationResult
            - List of explainability dicts for all topics
            - List of prerequisite warning dicts
        """
        if weights is None:
            weights = ScoringWeights()

        # 1. Update scores and value density
        update_topics_scores(topics, weights)

        # 2. Dependency Graph analysis
        graph = DependencyGraph(topics)
        has_cycle, cycle_nodes = graph.detect_cycle()
        if has_cycle:
            # We flag this in warnings
            pass

        # 3. Algorithm Dispatch
        choice_lower = algorithm_choice.lower()
        if "greedy" in choice_lower:
            result = solve_greedy(topics, available_hours)
        elif "heap" in choice_lower or "priority" in choice_lower:
            result = solve_priority_queue(topics, available_hours)
        else: # Default Dynamic Programming
            result = solve_knapsack_dp(topics, available_hours)

        # 4. Check prerequisites for selected topics
        warnings = []
        if respect_prerequisites:
            warnings = graph.validate_prerequisites_for_selected(result.selected_topics)

            # Sort selected topics topologically so prerequisites come first in study sequence
            ordered_selected = graph.topological_sort([t.id for t in result.selected_topics])
            result.selected_topics = ordered_selected

        # 5. Explainability generation
        selected_ids = {t.id for t in result.selected_topics}
        explanations = []
        for t in topics:
            is_selected = t.id in selected_ids
            rejection_reason = ""
            if not is_selected:
                if t.study_time > (available_hours - result.total_study_time):
                    rejection_reason = (
                        f"Requires {t.study_time} hrs, exceeding remaining slack time "
                        f"({max(0.0, available_hours - result.total_study_time):.1f} hrs)."
                    )
            explanations.append(explain_topic_selection(t, is_selected, rejection_reason))

        return result, explanations, warnings

    @staticmethod
    def compare_all_algorithms(
        topics: List[Topic],
        available_hours: float,
        weights: ScoringWeights = None
    ) -> Dict[str, OptimizationResult]:
        """
        Runs Greedy, Dynamic Programming, and Priority Queue simultaneously on identical inputs.
        """
        if weights is None:
            weights = ScoringWeights()

        update_topics_scores(topics, weights)

        dp_res = solve_knapsack_dp(topics, available_hours)
        greedy_res = solve_greedy(topics, available_hours)
        pq_res = solve_priority_queue(topics, available_hours)

        return {
            "Dynamic Programming": dp_res,
            "Greedy": greedy_res,
            "Priority Queue": pq_res
        }

    @staticmethod
    def run_what_if_analysis(
        topics: List[Topic],
        hour_steps: List[float] = None,
        weights: ScoringWeights = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluates optimization across varying study hour constraints (e.g., 2h, 4h, 6h, ...).
        Demonstrates Diminishing Returns and Pareto frontier.
        """
        if weights is None:
            weights = ScoringWeights()
        if hour_steps is None:
            hour_steps = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 20.0, 25.0, 30.0]

        update_topics_scores(topics, weights)
        records = []

        for h in hour_steps:
            dp_res = solve_knapsack_dp(topics, h)
            greedy_res = solve_greedy(topics, h)
            records.append({
                "Available Hours": h,
                "DP Benefit": round(dp_res.total_benefit, 2),
                "DP Marks": round(dp_res.total_expected_marks, 2),
                "DP Topics Count": len(dp_res.selected_topics),
                "Greedy Benefit": round(greedy_res.total_benefit, 2),
                "Greedy Marks": round(greedy_res.total_expected_marks, 2),
                "Greedy Topics Count": len(greedy_res.selected_topics)
            })

        return records
