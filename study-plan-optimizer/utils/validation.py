"""
Validation utilities for inputs and topic datasets.
Ensures data consistency and provides friendly, actionable validation error messages.
"""
from typing import List, Tuple, Dict, Any, Set
from models.topic import Topic
from models.student import StudentProfile


def validate_topic_dict(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates raw dictionary input for topic creation.
    Returns (is_valid, error_message).
    """
    name = str(data.get("name", "")).strip()
    if not name:
        return False, "Topic name cannot be empty."

    try:
        study_time = float(data.get("study_time", 0))
        if study_time <= 0:
            return False, "Study time must be greater than 0 hours."
        if study_time > 100:
            return False, "Study time per topic cannot exceed 100 hours."
    except (ValueError, TypeError):
        return False, "Study time must be a valid positive number."

    try:
        difficulty = int(data.get("difficulty", 0))
        if difficulty < 1 or difficulty > 10:
            return False, "Difficulty must be an integer between 1 and 10."
    except (ValueError, TypeError):
        return False, "Difficulty must be an integer between 1 and 10."

    try:
        importance = int(data.get("importance", 0))
        if importance < 1 or importance > 10:
            return False, "Importance must be an integer between 1 and 10."
    except (ValueError, TypeError):
        return False, "Importance must be an integer between 1 and 10."

    try:
        expected_marks = float(data.get("expected_marks", -1))
        if expected_marks < 0:
            return False, "Expected marks cannot be negative."
        if expected_marks > 100:
            return False, "Expected marks per topic cannot exceed 100."
    except (ValueError, TypeError):
        return False, "Expected marks must be a valid non-negative number."

    try:
        current_prep = float(data.get("current_prep", -1))
        if current_prep < 0 or current_prep > 100:
            return False, "Current preparation percentage must be between 0 and 100%."
    except (ValueError, TypeError):
        return False, "Current preparation must be a percentage between 0 and 100."

    try:
        priority = int(data.get("priority", 0))
        if priority < 1 or priority > 10:
            return False, "Priority must be an integer between 1 and 10."
    except (ValueError, TypeError):
        return False, "Priority must be an integer between 1 and 10."

    return True, ""


def validate_student_profile(profile: StudentProfile) -> Tuple[bool, str]:
    """Validates student parameters."""
    if profile.available_hours <= 0:
        return False, "Available study hours must be greater than 0."
    if profile.target_marks < 0:
        return False, "Target marks cannot be negative."
    if profile.daily_study_hours <= 0:
        return False, "Daily study hours must be greater than 0."
    if profile.session_duration_minutes <= 0:
        return False, "Study session duration must be greater than 0 minutes."
    if profile.break_duration_minutes < 0:
        return False, "Break duration cannot be negative."
    return True, ""


def validate_topic_collection(topics: List[Topic]) -> Tuple[bool, List[str]]:
    """
    Validates a list of topics for duplicate IDs, missing prerequisites, etc.
    Returns (is_valid, list_of_warnings_or_errors).
    """
    issues: List[str] = []
    seen_ids: Set[str] = set()

    for t in topics:
        if not t.id:
            issues.append(f"Topic '{t.name}' is missing an ID.")
        elif t.id in seen_ids:
            issues.append(f"Duplicate Topic ID found: '{t.id}'. IDs must be unique.")
        else:
            seen_ids.add(t.id)

    # Check prerequisites reference valid topic IDs
    for t in topics:
        for prereq_id in t.prerequisites:
            if prereq_id not in seen_ids:
                issues.append(
                    f"Topic '{t.name}' ({t.id}) references unknown prerequisite '{prereq_id}'."
                )

    return (len(issues) == 0), issues
