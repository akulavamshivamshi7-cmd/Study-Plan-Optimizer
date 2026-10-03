"""
Unit tests for data validation utilities.
"""
from models.student import StudentProfile
from models.topic import Topic
from utils.validation import validate_topic_dict, validate_student_profile, validate_topic_collection


def test_validate_topic_valid():
    data = {
        "name": "Graph BFS",
        "study_time": 2.5,
        "difficulty": 6,
        "importance": 8,
        "expected_marks": 12.0,
        "current_prep": 40.0,
        "priority": 7
    }
    valid, msg = validate_topic_dict(data)
    assert valid is True
    assert msg == ""


def test_validate_topic_invalid_time():
    data = {"name": "Test", "study_time": -1, "difficulty": 5, "importance": 5, "expected_marks": 5, "current_prep": 0, "priority": 5}
    valid, msg = validate_topic_dict(data)
    assert valid is False
    assert "Study time must be greater than 0" in msg


def test_validate_topic_invalid_difficulty():
    data = {"name": "Test", "study_time": 2, "difficulty": 15, "importance": 5, "expected_marks": 5, "current_prep": 0, "priority": 5}
    valid, msg = validate_topic_dict(data)
    assert valid is False
    assert "Difficulty must be an integer between 1 and 10" in msg


def test_validate_topic_invalid_prep():
    data = {"name": "Test", "study_time": 2, "difficulty": 5, "importance": 5, "expected_marks": 5, "current_prep": 120, "priority": 5}
    valid, msg = validate_topic_dict(data)
    assert valid is False
    assert "Current preparation percentage must be between 0 and 100" in msg


def test_validate_topic_collection_duplicates():
    topics = [
        Topic("T1", "A", "Topic 1", 2.0, 5, 5, 5.0, 0.0, 5),
        Topic("T1", "A", "Topic 1 Duplicate", 2.0, 5, 5, 5.0, 0.0, 5)
    ]
    valid, issues = validate_topic_collection(topics)
    assert valid is False
    assert any("Duplicate Topic ID" in issue for issue in issues)


def test_validate_student_profile():
    profile = StudentProfile(available_hours=-5)
    valid, msg = validate_student_profile(profile)
    assert valid is False
    assert "Available study hours must be greater than 0" in msg
