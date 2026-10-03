"""
Topic Model Definition.
Represents an academic topic with syllabus attributes, study metrics, and DSA metadata.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Topic:
    """
    Topic entity containing academic attributes and calculated algorithmic scores.
    """
    id: str
    subject: str
    name: str
    study_time: float               # Required study time in hours (e.g., 2.5)
    difficulty: int                 # 1 to 10
    importance: int                 # 1 to 10
    expected_marks: float           # Marks weightage in exam (e.g., 15.0)
    current_prep: float             # Current student preparation (0.0 to 100.0 %)
    priority: int                   # Student/Exam priority (1 to 10)
    prerequisites: List[str] = field(default_factory=list) # List of prerequisite topic IDs
    
    # Algorithmic metrics (computed dynamically)
    benefit_score: float = 0.0      # Expected utility score from learning model
    value_density: float = 0.0      # Benefit score per hour (benefit_score / study_time)
    prep_gap: float = 0.0           # 100 - current_prep

    def to_dict(self) -> Dict[str, Any]:
        """Convert Topic instance to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "subject": self.subject,
            "name": self.name,
            "study_time": self.study_time,
            "difficulty": self.difficulty,
            "importance": self.importance,
            "expected_marks": self.expected_marks,
            "current_prep": self.current_prep,
            "priority": self.priority,
            "prerequisites": list(self.prerequisites),
            "benefit_score": round(self.benefit_score, 2),
            "value_density": round(self.value_density, 3),
            "prep_gap": round(self.prep_gap, 2)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Topic":
        """Factory method to instantiate a Topic from dictionary."""
        return cls(
            id=str(data.get("id", "")),
            subject=str(data.get("subject", "General")),
            name=str(data.get("name", "Untitled Topic")),
            study_time=float(data.get("study_time", 1.0)),
            difficulty=int(data.get("difficulty", 5)),
            importance=int(data.get("importance", 5)),
            expected_marks=float(data.get("expected_marks", 5.0)),
            current_prep=float(data.get("current_prep", 0.0)),
            priority=int(data.get("priority", 5)),
            prerequisites=list(data.get("prerequisites", []))
        )
