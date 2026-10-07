from datetime import datetime

from database import get_db
from monitoring import event_detector

_open_absences = {}


def log_face_state(candidate_id, session_id, current_state):

    key = (candidate_id, session_id)
    connection = get_db()

    try:
        if current_state == "face_absent":

            if key not in _open_absences:
                now = datetime.now()

                cursor = connection.execute("""
                    INSERT INTO face_events
                        (candidate_id, session_id, event_type, started_at)
                    VALUES (?, ?, 'face_absent', ?)
                """, (candidate_id, session_id, now.isoformat()))

                connection.commit()

                _open_absences[key] = {
                    "event_id": cursor.lastrowid,
                    "started_at": now,
                }

            started_at = _open_absences[key]["started_at"]

            ongoing_seconds = (
                datetime.now() - started_at
            ).total_seconds()

            event_detector.check_face_absence(
                connection,
                candidate_id,
                session_id,
                ongoing_seconds
            )

        else:

            if key in _open_absences:
                open_event = _open_absences.pop(key)

                ended_at = datetime.now()

                duration = (
                    ended_at - open_event["started_at"]
                ).total_seconds()

                connection.execute("""
                    UPDATE face_events
                    SET ended_at = ?, duration_seconds = ?
                    WHERE id = ?
                """, (
                    ended_at.isoformat(),
                    duration,
                    open_event["event_id"]
                ))

                connection.commit()

    finally:
        connection.close()