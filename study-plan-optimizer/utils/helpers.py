"""
Helper utility functions for data loading, time formatting, and table conversions.
"""
import json
import os
from typing import List, Dict, Any
from models.topic import Topic


def load_topics_from_json(file_path: str) -> List[Topic]:
    """Loads a list of Topic models from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Topic file not found at: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Topic.from_dict(item) for item in data]


def save_topics_to_json(topics: List[Topic], file_path: str) -> None:
    """Saves a list of Topic models to a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in topics], f, indent=2)


def format_hours_to_hours_minutes(hours: float) -> str:
    """Converts decimal hours (e.g., 2.5) to '2h 30m'."""
    total_minutes = int(round(hours * 60))
    h = total_minutes // 60
    m = total_minutes % 60
    if h > 0 and m > 0:
        return f"{h}h {m}m"
    elif h > 0:
        return f"{h}h"
    else:
        return f"{m}m"


def topics_to_display_list(topics: List[Topic]) -> List[Dict[str, Any]]:
    """Converts topics list to tabular format suitable for Pandas and Streamlit display."""
    rows = []
    for t in topics:
        rows.append({
            "ID": t.id,
            "Subject": t.subject,
            "Topic Name": t.name,
            "Study Time (hrs)": t.study_time,
            "Marks": t.expected_marks,
            "Difficulty": f"{t.difficulty}/10",
            "Importance": f"{t.importance}/10",
            "Prep %": f"{t.current_prep:.0f}%",
            "Priority": f"{t.priority}/10",
            "Benefit Score": round(t.benefit_score, 2),
            "Value/Hour": round(t.value_density, 2),
            "Prerequisites": ", ".join(t.prerequisites) if t.prerequisites else "None"
        })
    return rows
