# exam submitted->calculated integrity score-> generate ai report -> vaildation ai report -> display in terminal -> return report
# exam submitted->calculated integrity score-> generate ai report -> vaildation ai report -> save in db (ai_reports) -> return report
from database import get_db
from datetime import datetime


def save_ai_report(
    candidate_id,
    session_id,
    report
):
    """
    Save an AI-generated integrity report.

    The report is associated with a specific
    candidate and examination session.
    """

    if not report:
        raise ValueError(
            "AI report cannot be empty"
        )

    connection = get_db()

    try:

        created_at = datetime.now().isoformat()

        connection.execute("""
            INSERT INTO ai_reports
            (
                candidate_id,
                session_id,
                report,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            candidate_id,
            session_id,
            report,
            created_at
        ))

        connection.commit()

        print("================================")
        print("AI REPORT SAVED")
        print("================================")
        print("Candidate ID :", candidate_id)
        print("Session ID   :", session_id)
        print("Created At   :", created_at)
        print("================================")

        return {
            "success": True,
            "candidate_id": candidate_id,
            "session_id": session_id,
            "created_at": created_at
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# if __name__ == "__main__":

#     result = save_ai_report(
#         candidate_id=1,
#         session_id="test-ai-report-session",
#         report="""
#         The candidate received an integrity score of 80
#         with a Low risk level. The observed session data
#         should be reviewed by the invigilator.
#         """
#     )

#     print("Test result:")
#     print(result)

def get_ai_report(candidate_id, session_id):
    """
    Retrieve the AI integrity report for a specific
    candidate and examination session.
    """

    connection = get_db()

    try:
        row = connection.execute("""
            SELECT
                id,
                candidate_id,
                session_id,
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

        if row is None:
            return None

        return {
            "id": row["id"],
            "candidate_id": row["candidate_id"],
            "session_id": row["session_id"],
            "report": row["report"],
            "created_at": row["created_at"]
        }

    finally:
        connection.close()