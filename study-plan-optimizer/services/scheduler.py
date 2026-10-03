"""
Study Session Scheduler and Timetable Generator.

Splits selected study topics into chronologically ordered Pomodoro-style sessions:
- Customizable study session duration (e.g. 50 minutes)
- Customizable short break duration (e.g. 10 minutes)
- Day-wise capacity constraints (e.g. 4 hours/day)
- Realistic clock-time advancement (e.g. starting at 09:00 AM)
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from models.topic import Topic


@dataclass
class SessionSlot:
    """Represents an individual study or break interval."""
    day: int
    start_time: str
    end_time: str
    slot_type: str          # "Study", "Break", "Long Break"
    topic_id: Optional[str] = None
    topic_name: Optional[str] = None
    subject: Optional[str] = None
    duration_minutes: int = 50

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Day": f"Day {self.day}",
            "Time Interval": f"{self.start_time} - {self.end_time}",
            "Type": self.slot_type,
            "Topic / Activity": self.topic_name if self.topic_name else self.slot_type,
            "Subject": self.subject or "-",
            "Duration": f"{self.duration_minutes} min"
        }


@dataclass
class DailyPlan:
    """Represents one day's scheduled activities."""
    day: int
    total_study_minutes: int
    slots: List[SessionSlot] = field(default_factory=list)
    topics_covered: List[str] = field(default_factory=list)


@dataclass
class StudySchedule:
    """Full multi-day study schedule."""
    total_days: int
    total_study_hours: float
    total_break_hours: float
    daily_plans: List[DailyPlan] = field(default_factory=list)

    def to_flat_slots(self) -> List[Dict[str, Any]]:
        """Flattens all slots across days for table presentation."""
        rows = []
        for day in self.daily_plans:
            for s in day.slots:
                rows.append(s.to_dict())
        return rows


def generate_study_schedule(
    selected_topics: List[Topic],
    daily_study_hours: float = 4.0,
    session_minutes: int = 50,
    break_minutes: int = 10,
    start_time_str: str = "09:00"
) -> StudySchedule:
    """
    Generates a structured, chronological daily study schedule from a list of selected topics.

    Args:
        selected_topics: Ordered list of topics to study
        daily_study_hours: Maximum study hours allowed per day
        session_minutes: Duration of each active study block
        break_minutes: Duration of each rest interval
        start_time_str: Daily start time in 'HH:MM' (24-hour format)

    Returns:
        StudySchedule object containing day-by-day timetable and slots.
    """
    if not selected_topics:
        return StudySchedule(total_days=0, total_study_hours=0.0, total_break_hours=0.0)

    daily_study_minutes_limit = int(round(daily_study_hours * 60))
    session_minutes = max(15, min(120, session_minutes))
    break_minutes = max(0, min(60, break_minutes))

    # Break topics into individual study chunks of size <= session_minutes
    chunks: List[Dict[str, Any]] = []
    for topic in selected_topics:
        total_topic_minutes = int(round(topic.study_time * 60))
        rem = total_topic_minutes

        chunk_num = 1
        total_chunks = max(1, (total_topic_minutes + session_minutes - 1) // session_minutes)

        while rem > 0:
            current_chunk_duration = min(session_minutes, rem)
            chunk_label = (
                f"{topic.name} (Part {chunk_num}/{total_chunks})"
                if total_chunks > 1 else topic.name
            )
            chunks.append({
                "topic_id": topic.id,
                "topic_name": chunk_label,
                "subject": topic.subject,
                "duration": current_chunk_duration
            })
            rem -= current_chunk_duration
            chunk_num += 1

    # Distribute chunks across days
    daily_plans: List[DailyPlan] = []
    current_day = 1
    current_clock = datetime.strptime(start_time_str, "%H:%M")
    current_day_study_min = 0
    current_day_slots: List[SessionSlot] = []
    current_day_topics: Set[str] = set()
    consecutive_sessions = 0

    def finalize_day():
        nonlocal current_day, current_clock, current_day_study_min, current_day_slots, current_day_topics, consecutive_sessions
        daily_plans.append(DailyPlan(
            day=current_day,
            total_study_minutes=current_day_study_min,
            slots=current_day_slots,
            topics_covered=list(current_day_topics)
        ))
        current_day += 1
        current_clock = datetime.strptime(start_time_str, "%H:%M")
        current_day_study_min = 0
        current_day_slots = []
        current_day_topics = set()
        consecutive_sessions = 0

    for i, chunk in enumerate(chunks):
        dur = chunk["duration"]

        # Check if adding this chunk exceeds daily limit (if we already have sessions today)
        if current_day_study_min > 0 and (current_day_study_min + dur > daily_study_minutes_limit):
            finalize_day()

        # Add study slot
        start_fmt = current_clock.strftime("%H:%M")
        end_clock = current_clock + timedelta(minutes=dur)
        end_fmt = end_clock.strftime("%H:%M")

        current_day_slots.append(SessionSlot(
            day=current_day,
            start_time=start_fmt,
            end_time=end_fmt,
            slot_type="Study",
            topic_id=chunk["topic_id"],
            topic_name=chunk["topic_name"],
            subject=chunk["subject"],
            duration_minutes=dur
        ))

        current_day_study_min += dur
        current_day_topics.add(chunk["subject"])
        current_clock = end_clock
        consecutive_sessions += 1

        # Check if there is a next chunk
        is_last_chunk = (i == len(chunks) - 1)
        will_continue_today = not is_last_chunk and (current_day_study_min + min(session_minutes, chunks[i+1]["duration"]) <= daily_study_minutes_limit)

        if will_continue_today and break_minutes > 0:
            # Check for long break after every 3 study sessions
            break_len = break_minutes * 2 if consecutive_sessions % 3 == 0 else break_minutes
            b_start = current_clock.strftime("%H:%M")
            b_end_clock = current_clock + timedelta(minutes=break_len)
            b_end = b_end_clock.strftime("%H:%M")

            current_day_slots.append(SessionSlot(
                day=current_day,
                start_time=b_start,
                end_time=b_end,
                slot_type="Long Break" if break_len > break_minutes else "Break",
                topic_id=None,
                topic_name="Rest & Recharge",
                subject="-",
                duration_minutes=break_len
            ))
            current_clock = b_end_clock

    if current_day_slots:
        finalize_day()

    total_study_min = sum(d.total_study_minutes for d in daily_plans)
    total_break_min = sum(
        s.duration_minutes for d in daily_plans for s in d.slots if s.slot_type != "Study"
    )

    return StudySchedule(
        total_days=len(daily_plans),
        total_study_hours=round(total_study_min / 60.0, 2),
        total_break_hours=round(total_break_min / 60.0, 2),
        daily_plans=daily_plans
    )
