"""
Unit tests for Study Schedule Generator.
"""
from models.topic import Topic
from services.scheduler import generate_study_schedule


def test_scheduler_basic():
    t1 = Topic("1", "DSA", "Topic A", 2.0, 5, 5, 5.0, 0.0, 5) # 120 min
    t2 = Topic("2", "OS", "Topic B", 1.5, 5, 5, 5.0, 0.0, 5)  # 90 min

    # Daily study hours: 4.0 (240 min)
    # Total topic time: 210 min (fits in 1 day)
    schedule = generate_study_schedule(
        selected_topics=[t1, t2],
        daily_study_hours=4.0,
        session_minutes=50,
        break_minutes=10,
        start_time_str="09:00"
    )

    assert schedule.total_days == 1
    assert schedule.total_study_hours == 3.5
    assert len(schedule.daily_plans) == 1
    # Check slots exist
    slots = schedule.daily_plans[0].slots
    assert len(slots) > 0
    # First slot starts at 09:00
    assert slots[0].start_time == "09:00"
    assert slots[0].slot_type == "Study"


def test_scheduler_multiday():
    # 3 topics of 3 hours each = 9 hours total
    # daily limit = 4 hours -> should span at least 3 days
    t1 = Topic("1", "DSA", "T1", 3.0, 5, 5, 5.0, 0.0, 5)
    t2 = Topic("2", "DSA", "T2", 3.0, 5, 5, 5.0, 0.0, 5)
    t3 = Topic("3", "DSA", "T3", 3.0, 5, 5, 5.0, 0.0, 5)

    schedule = generate_study_schedule(
        selected_topics=[t1, t2, t3],
        daily_study_hours=4.0,
        session_minutes=50,
        break_minutes=10
    )

    assert schedule.total_days >= 3
    assert schedule.total_study_hours == 9.0
