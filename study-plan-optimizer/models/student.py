"""
Student Profile Model Definition.
Contains student preferences, constraints, target marks, and scheduling parameters.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class StudentProfile:
    name: str = "Student"
    available_hours: float = 15.0
    exam_date: str = "2026-10-15"
    target_marks: float = 85.0
    daily_study_hours: float = 4.0
    session_duration_minutes: int = 50
    break_duration_minutes: int = 10
    start_time_str: str = "09:00"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "available_hours": self.available_hours,
            "exam_date": self.exam_date,
            "target_marks": self.target_marks,
            "daily_study_hours": self.daily_study_hours,
            "session_duration_minutes": self.session_duration_minutes,
            "break_duration_minutes": self.break_duration_minutes,
            "start_time_str": self.start_time_str
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProfile":
        return cls(
            name=str(data.get("name", "Student")),
            available_hours=float(data.get("available_hours", 15.0)),
            exam_date=str(data.get("exam_date", "2026-10-15")),
            target_marks=float(data.get("target_marks", 85.0)),
            daily_study_hours=float(data.get("daily_study_hours", 4.0)),
            session_duration_minutes=int(data.get("session_duration_minutes", 50)),
            break_duration_minutes=int(data.get("break_duration_minutes", 10)),
            start_time_str=str(data.get("start_time_str", "09:00"))
        )
