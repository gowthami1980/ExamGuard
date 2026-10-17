
from database import get_db


def get_session_summary(candidate_id, session_id):
    """
    Retrieve the review summary for one exam session.

    Includes the official integrity score, incidents,
    alerts, evidence metadata, and stored AI report.
    """

    connection = get_db()

    try:
        # 1. Get the official integrity score
        score = connection.execute("""
            SELECT
                integrity_score,
                risk_level,
                event_penalty,
                face_presence_ratio,
                computed_at
            FROM integrity_scores
            WHERE candidate_id = ?
              AND session_id = ?
        """, (
            candidate_id,
            session_id
        )).fetchone()

        if score is None:
            return None

        # 2. Get incident history
        incidents = connection.execute("""
            SELECT
                id,
                event_type,
                description,
                severity,
                event_time,
                created_at
            FROM incident_logs
            WHERE candidate_id = ?
              AND session_id = ?
            ORDER BY event_time DESC
        """, (
            candidate_id,
            session_id
        )).fetchall()

        # 3. Get alerts
        alerts = connection.execute("""
            SELECT
                id,
                alert_type,
                message,
                severity,
                status,
                created_at
            FROM alerts
            WHERE candidate_id = ?
              AND session_id = ?
            ORDER BY created_at DESC
        """, (
            candidate_id,
            session_id
        )).fetchall()

        # 4. Get evidence metadata (not the image bytes)
        evidence = connection.execute("""
            SELECT
                id,
                evidence_type,
                filename,
                mime_type,
                sha256_hash,
                created_at
            FROM evidence
            WHERE candidate_id = ?
              AND session_id = ?
            ORDER BY created_at DESC
        """, (
            candidate_id,
            session_id
        )).fetchall()

        # 5. Get the stored AI report
        ai_report = connection.execute("""
            SELECT
                id,
                report,
                created_at
            FROM ai_reports
            WHERE candidate_id = ?
              AND session_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (
            candidate_id,
            session_id
        )).fetchone()

        return {
            "candidate_id": candidate_id,
            "session_id": session_id,
            "integrity_score": dict(score),
            "incidents": [dict(row) for row in incidents],
            "alerts": [dict(row) for row in alerts],
            "evidence": [dict(row) for row in evidence],
            "ai_report": dict(ai_report) if ai_report else None
        }

    finally:
        connection.close()