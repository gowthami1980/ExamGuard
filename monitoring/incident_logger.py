# Incident log : an incident log records an observed event, bascially historical records
# It records what happened
# histroical evidence
# usually consist many rows

from datetime import datetime
from database import get_db

def create_incident(candidate_id, session_id, event_type,description,severity):
    connection = get_db()
    try:
        event_time = datetime.now().isoformat()
        created_at = datetime.now().isoformat()
        
        connection.execute("""
               Insert into incident_logs(candidate_id, session_id, event_type, description, severity, event_time,created_at) values (?,?,?,?,?,?,?)           
                           
        """,(candidate_id, session_id, event_type, description, severity, event_time,created_at))
        connection.commit()
        
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
        
# if __name__ == "__main__":
#     create_incident(candidate_id =3, session_id=1, event_type="tab_switch",description="candidate switched tab in browser",severity="medium")  
#     print("data created successfully")