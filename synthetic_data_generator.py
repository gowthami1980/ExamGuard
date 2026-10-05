"""
Synthetic Session Log Data Generator
-------------------------------------
Milestone 1, Week 1 warm-up task from the project brief:

    "Synthetic Session Log Data — Generated using Python's Faker
    library and custom scripts to simulate candidate sessions with
    varied event patterns."

This creates fake candidates plus realistic exam_sessions,
browser_events and face_events rows using the exact same schema the
live Flask app writes to, so later modules (integrity scoring, the
LangChain report agent, the analytics dashboard) have a corpus of
session data to work with without running real proctored exams.

Run:
    python synthetic_data_generator.py
    python synthetic_data_generator.py 30   # generate 30 candidates
"""

import random
import sys
import uuid
from datetime import timedelta

from faker import Faker
from werkzeug.security import generate_password_hash

from database import init_db, get_db

fake = Faker()

BROWSER_EVENT_TYPES = [
    "tab_switch", "tab_return", "focus_lost", "focus_gained",
    "copy_attempt", "paste_attempt", "cut_attempt",
    "right_click", "keyboard_activity", "mouse_activity", "answer_selected",
]

DEFAULT_NUM_CANDIDATES = 15
MIN_EVENTS_PER_SESSION = 5
MAX_EVENTS_PER_SESSION = 40


def create_fake_candidate(connection):
    name = fake.name()
    email = fake.unique.email()
    password = generate_password_hash("password123")
    photo = f"static/uploads/synthetic_{uuid.uuid4().hex[:8]}.jpg"

    cursor = connection.execute("""
        INSERT INTO candidates (name, email, password, photo)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, photo))

    return cursor.lastrowid


def create_fake_session(connection, candidate_id):

    session_id = str(uuid.uuid4())
    started_at = fake.date_time_between(start_date="-14d", end_date="now")
    duration_minutes = random.randint(20, 90)
    submitted_at = started_at + timedelta(minutes=duration_minutes)

    connection.execute("""
        INSERT INTO exam_sessions
            (candidate_id, session_id, status, started_at, submitted_at)
        VALUES (?, ?, 'submitted', ?, ?)
    """, (candidate_id, session_id, started_at.isoformat(), submitted_at.isoformat()))

    # ---- Browser events ----
    num_events = random.randint(MIN_EVENTS_PER_SESSION, MAX_EVENTS_PER_SESSION)

    for _ in range(num_events):
        event_type = random.choice(BROWSER_EVENT_TYPES)
        event_time = fake.date_time_between(start_date=started_at, end_date=submitted_at)

        connection.execute("""
            INSERT INTO browser_events
                (candidate_id, session_id, event_type, event_time, details)
            VALUES (?, ?, ?, ?, ?)
        """, (
            candidate_id, session_id, event_type, event_time.isoformat(),
            f"Synthetic {event_type} event",
        ))

    # ---- Face-absence events (0-4 per session) ----
    for _ in range(random.randint(0, 4)):
        absence_start = fake.date_time_between(start_date=started_at, end_date=submitted_at)
        duration = random.randint(5, 180)
        absence_end = absence_start + timedelta(seconds=duration)

        connection.execute("""
            INSERT INTO face_events
                (candidate_id, session_id, event_type, started_at, ended_at, duration_seconds)
            VALUES (?, ?, 'face_absent', ?, ?, ?)
        """, (
            candidate_id, session_id,
            absence_start.isoformat(), absence_end.isoformat(), duration,
        ))

    return session_id


def generate(num_candidates=DEFAULT_NUM_CANDIDATES):

    init_db()
    connection = get_db()

    try:
        for _ in range(num_candidates):
            candidate_id = create_fake_candidate(connection)
            create_fake_session(connection, candidate_id)

        connection.commit()
        print(f"Generated {num_candidates} synthetic candidates with session logs.")

    finally:
        connection.close()


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_NUM_CANDIDATES
    generate(count)