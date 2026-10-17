from datetime import datetime
import hashlib

from database import get_db


def calculate_sha256(file_data):
    """
    Calculate SHA-256 hash of binary file data.
    """

    return hashlib.sha256(file_data).hexdigest()


def save_evidence(
    candidate_id,
    session_id,
    evidence_type,
    filename,
    mime_type,
    file_data
):
    """
    Save examination evidence into the database.

    The SHA-256 hash is calculated from the actual
    binary file data before storing the evidence.
    """

    connection = get_db()

    try:

        # --------------------------------------------------
        # Calculate SHA-256
        # --------------------------------------------------

        sha256_hash = calculate_sha256(file_data)

        # --------------------------------------------------
        # Current timestamp
        # --------------------------------------------------

        created_at = datetime.now().isoformat()

        # --------------------------------------------------
        # Save evidence
        # --------------------------------------------------

        connection.execute("""
            INSERT INTO evidence
            (
                candidate_id,
                session_id,
                evidence_type,
                filename,
                mime_type,
                file_data,
                sha256_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            session_id,
            evidence_type,
            filename,
            mime_type,
            file_data,
            sha256_hash,
            created_at
        ))

        connection.commit()

        print("================================")
        print("EVIDENCE SAVED")
        print("================================")
        print("Candidate ID :", candidate_id)
        print("Session ID   :", session_id)
        print("Evidence     :", evidence_type)
        print("Filename     :", filename)
        print("MIME Type    :", mime_type)
        print("SHA-256      :", sha256_hash)
        print("Created At   :", created_at)
        print("================================")

        return {
            "success": True,
            "sha256_hash": sha256_hash
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_evidence(evidence_id):
    """
    Retrieve one evidence record.
    """

    connection = get_db()

    try:

        row = connection.execute("""
            SELECT
                id,
                candidate_id,
                session_id,
                evidence_type,
                filename,
                mime_type,
                file_data,
                sha256_hash,
                created_at
            FROM evidence
            WHERE id = ?
        """, (evidence_id,)).fetchone()

        return row

    finally:
        connection.close()
        
        
def verify_evidence(evidence_id):
    connection = get_db()
    
    try:
        row = connection.execute("""
            SELECT id, file_data, sha256_hash from evidence WHERE id = ?
        """, (evidence_id,)).fetchone()
        
        if row is None:
            return {
                "success": False,
                "message": "Evidence not found"
            }
        stored_hash = row["sha256_hash"]
        calculated_hash = calculate_sha256(row["file_data"])

        if stored_hash == calculated_hash:
            return {
                "success": True,
                "message": "Evidence is valid",
                "evidence_id": row["id"],
                "stored_hash": stored_hash,
                "calculated_hash": calculated_hash
            }
        else:
            return {
                "success": False,
                "message": "Evidence is invalid",
                "evidence_id": row["id"],
                "stored_hash": stored_hash, 
                "calculated_hash": calculated_hash
            }
    finally:
        connection.close()