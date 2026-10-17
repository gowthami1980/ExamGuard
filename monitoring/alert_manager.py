from datetime import datetime
from database import get_db


def create_alert(
    candidate_id,session_id,alert_type,message,severity
):
    connection =get_db()
    
    try:
        existing_alert = connection.execute("""
                                            select id from alerts where session_id=? and alert_type=? and status="open"
                                            """,(session_id,alert_type)).fetchone()
        if existing_alert:
            print("alert already exists")
            return False
        
        created_at = datetime.now().isoformat()
        
        connection.execute("""
                           insert into alerts (candidate_id, session_id,alert_type,message,severity,created_at) values (?,?,?,?,?,?)
                           """, (candidate_id, session_id, alert_type, message, severity, created_at))
        connection.commit()
        print("Alert created successfully")
        return True
    except Exception as e:
        print(f"Error creating alert: {e}")
        return False
    
# connect alert to integrity score

def create_risk_alert(candidate_id, session_id, risk_level, integrity_score):
    connection = get_db()
    
    if risk_level == "low":
        print("Risk level is low, no alert created.")
        return False
    
    if risk_level == "medium":
        return(
            create_alert(
                candidate_id=candidate_id,
                session_id=session_id,
                alert_type="Medium_Integrity_Risk",
                message=f"Integrity score is {integrity_score}, which indicates a medium risk level.",
                severity="Medium"
            )
        )
        
    if risk_level == "high":
        return(
            create_alert(
                candidate_id=candidate_id,
                session_id=session_id,
                alert_type="High_Integrity_Risk",
                message=f"Integrity score is {integrity_score}, which indicates a high risk level.",
                severity="High"
            )
        )
        