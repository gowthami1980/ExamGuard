
import cv2
import numpy as np
from datetime import datetime
from database import get_db

#Load face detector 
face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_face(image_data):
    #covert bytes into numpy array 
    image_array = np.frombuffer(image_data,dtype= np.uint8)

    image = cv2.imdecode(image_array,cv2.IMREAD_COLOR)
    if image is None:
        return False, None
    
    #convert image to grayscale
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #detect faces
    faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(60, 60)
)
     #draw rectangle around faces

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return True, image

    return False , image

def close_open_face_event(
    candidate_id,
    session_id
):

    connection = get_db()

    try:

        row = connection.execute("""
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

        # No open face event
        if not row:
            return

        ended_at = datetime.now()

        started_at = datetime.fromisoformat(
            row["started_at"]
        )

        duration = (
            ended_at - started_at
        ).total_seconds()

        connection.execute("""
            UPDATE face_events
            SET
                ended_at = ?,
                duration_seconds = ?
            WHERE id = ?
        """, (
            ended_at.isoformat(),
            duration,
            row["id"]
        ))

        connection.commit()

    finally:
        connection.close()