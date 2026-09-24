from datetime import datetime

from database import get_db


def log_face_state(
    candidate_id,
    session_id,
    current_state
):

    connection = get_db()

    now = datetime.now().isoformat()


    # Get previous open event
    previous = connection.execute("""
        SELECT *
        FROM face_events
        WHERE candidate_id = ?
        AND session_id = ?
        AND ended_at IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (
        candidate_id,
        session_id
    )).fetchone()


    # First event
    if not previous:

        connection.execute("""
            INSERT INTO face_events
            (
                candidate_id,
                session_id,
                event_type,
                started_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            candidate_id,
            session_id,
            current_state,
            now
        ))


    else:

        # Same state → do nothing
        if previous["event_type"] == current_state:

            connection.close()

            return


        # State changed
        started_at = datetime.fromisoformat(
            previous["started_at"]
        )

        ended_at = datetime.fromisoformat(now)

        duration = (
            ended_at - started_at
        ).total_seconds()


        # Close previous event
        connection.execute("""
            UPDATE face_events

            SET
                ended_at = ?,
                duration_seconds = ?

            WHERE id = ?
        """, (
            now,
            duration,
            previous["id"]
        ))


        # Start new event
        connection.execute("""
            INSERT INTO face_events
            (
                candidate_id,
                session_id,
                event_type,
                started_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            candidate_id,
            session_id,
            current_state,
            now
        ))


    connection.commit()

    connection.close()