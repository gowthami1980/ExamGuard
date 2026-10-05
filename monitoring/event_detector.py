"""
Rule-based suspicious event detection engine.

Watches browser activity and face-presence data as it is logged and
raises a row in `suspicious_events` whenever a candidate crosses one
of the configurable thresholds below. Kept deliberately simple and
transparent (per the project brief this is a rule engine, not a
model) so invigilators can see exactly why a flag was raised.
"""

from datetime import datetime, timedelta

# ------------------------------------------------------------
# CONFIGURABLE THRESHOLDS
# ------------------------------------------------------------
TAB_SWITCH_LIMIT = 3
FACE_ABSENT_SECONDS_LIMIT = 120 
FOCUS_LOSS_LIMIT = 5
FOCUS_LOSS_WINDOW_SECONDS = 300


def _already_flagged(connection, session_id, event_type):
    row = connection.execute("""
        SELECT id FROM suspicious_events
        WHERE session_id = ? AND event_type = ?
    """, (session_id, event_type)).fetchone()

    return row is not None


def _raise_flag(connection, candidate_id, session_id, event_type, reason, severity):
    if _already_flagged(connection, session_id, event_type):
        return

    connection.execute("""
        INSERT INTO suspicious_events
            (candidate_id, session_id, event_type, reason, event_time, severity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        candidate_id,
        session_id,
        event_type,
        reason,
        datetime.now().isoformat(),
        severity,
    ))

    connection.commit()


# ------------------------------------------------------------
# RULE: excessive tab switching
# ------------------------------------------------------------
def check_tab_switches(connection, candidate_id, session_id):
    count = connection.execute("""
        SELECT COUNT(*) AS total FROM browser_events
        WHERE session_id = ? AND event_type = 'tab_switch'
    """, (session_id,)).fetchone()["total"]

    if count > TAB_SWITCH_LIMIT:
        _raise_flag(
            connection, candidate_id, session_id,
            "excessive_tab_switching",
            f"Candidate switched away from the exam tab {count} times, "
            f"exceeding the allowed limit of {TAB_SWITCH_LIMIT}.",
            "High",
        )


# ------------------------------------------------------------
# RULE: excessive focus loss frequency
# ------------------------------------------------------------
def check_focus_loss_frequency(connection, candidate_id, session_id):
    window_start = (
        datetime.now() - timedelta(seconds=FOCUS_LOSS_WINDOW_SECONDS)
    ).isoformat()

    count = connection.execute("""
        SELECT COUNT(*) AS total FROM browser_events
        WHERE session_id = ?
          AND event_type = 'focus_lost'
          AND event_time >= ?
    """, (session_id, window_start)).fetchone()["total"]

    if count > FOCUS_LOSS_LIMIT:
        _raise_flag(
            connection, candidate_id, session_id,
            "excessive_focus_loss",
            f"Candidate's browser window lost focus {count} times within "
            f"the last {FOCUS_LOSS_WINDOW_SECONDS // 60} minutes, exceeding "
            f"the allowed limit of {FOCUS_LOSS_LIMIT}.",
            "Medium",
        )


# ------------------------------------------------------------
# RULE: face absent for too long
# ------------------------------------------------------------
def check_face_absence(connection, candidate_id, session_id, ongoing_seconds):
    if ongoing_seconds > FACE_ABSENT_SECONDS_LIMIT:
        _raise_flag(
            connection, candidate_id, session_id,
            "excessive_face_absence",
            f"Candidate's face has been absent from the camera for "
            f"{int(ongoing_seconds)} seconds, exceeding the "
            f"{FACE_ABSENT_SECONDS_LIMIT}-second limit.",
            "High",
        )


# ------------------------------------------------------------
# ENTRY POINT called from the browser-event route in app.py
# ------------------------------------------------------------
def evaluate_browser_event(connection, candidate_id, session_id, event_type):
    if event_type == "tab_switch":
        check_tab_switches(connection, candidate_id, session_id)

    elif event_type == "focus_lost":
        check_focus_loss_frequency(connection, candidate_id, session_id)