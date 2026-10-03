"""
Result dataclass representing the outcome of an optimization run.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from models.topic import Topic


@dataclass
class OptimizationResult:
    """
    Encapsulates results, selected topics, and execution metrics from an optimization algorithm.
    """
    algorithm_name: str
    selected_topics: List[Topic] = field(default_factory=list)
    unselected_topics: List[Topic] = field(default_factory=list)
    total_study_time: float = 0.0
    available_hours: float = 0.0
    total_benefit: float = 0.0
    total_expected_marks: float = 0.0
    execution_time_ms: float = 0.0
    time_complexity: str = ""
    space_complexity: str = ""
    explanation: str = ""
    logs: List[str] = field(default_factory=list)
    
    # Algorithm-specific introspection structures
    dp_table: Optional[List[List[float]]] = None
    dp_weight_labels: Optional[List[float]] = None
    dp_topic_labels: Optional[List[str]] = None
    heap_trace: Optional[List[Dict[str, Any]]] = None

    def to_summary_dict(self) -> Dict[str, Any]:
        """Summary representation for comparison tables."""
        return {
            "Algorithm": self.algorithm_name,
            "Study Time (hrs)": round(self.total_study_time, 2),
            "Expected Benefit": round(self.total_benefit, 2),
            "Expected Marks": round(self.total_expected_marks, 2),
            "Topics Selected": len(self.selected_topics),
            "Time Complexity": self.time_complexity,
            "Space Complexity": self.space_complexity,
            "Runtime (ms)": round(self.execution_time_ms, 3)
        }
