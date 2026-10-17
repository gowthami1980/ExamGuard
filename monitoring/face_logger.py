from datetime import datetime

from database import get_db
from monitoring import event_detector

# In-memory tracker of the currently-open (not yet ended) face-absent
# interval per exam session. Keyed by (candidate_id, session_id).
#
#   { (candidate_id, session_id): {"event_id": int, "started_at": datetime} }
#
# A single Flask dev process is enough for one exam session; if this
# ever runs behind multiple workers, this could be moved into the DB
# (e.g. "open" rows with ended_at IS NULL) instead.
_open_absences = {}


def log_face_state(candidate_id, session_id, current_state):
    """
    Called on every webcam frame check (~every 2s from exam.html).

    - On the *first* frame where a face goes missing, opens a new
      face_events row with started_at.
    - While the face stays missing, checks the rule engine so a
      continuous absence longer than the threshold gets flagged
      even before it ends.
    - On the frame where the face reappears, closes the open row
      with ended_at + duration_seconds.
    """

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

            # How long has the candidate's face been missing so far?
            started_at = _open_absences[key]["started_at"]
            ongoing_seconds = (datetime.now() - started_at).total_seconds()

            event_detector.check_face_absence(
                connection, candidate_id, session_id, ongoing_seconds
            )

        else:  # "face_detected"

            if key in _open_absences:
                open_event = _open_absences.pop(key)
                ended_at = datetime.now()
                duration = (ended_at - open_event["started_at"]).total_seconds()

                connection.execute("""
                    UPDATE face_events
                    SET ended_at = ?, duration_seconds = ?
                    WHERE id = ?
                """, (ended_at.isoformat(), duration, open_event["event_id"]))

                connection.commit()

    finally:
        connection.close()