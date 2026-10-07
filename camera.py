import os
from datetime import datetime

import cv2
import numpy as np

UPLOAD_FOLDER = "static/uploads"


def save_captured_photo(image_data):
    """
    Accepts raw image bytes captured from the candidate's browser
    webcam (sent from register.html), decodes them with OpenCV,
    and stores the photo under static/uploads.

    Returns the relative photo path, or None if the image could
    not be decoded.
    """

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    image_array = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if frame is None:
        return None

    filename = f"candidate_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    photo_path = os.path.join(UPLOAD_FOLDER, filename)

    cv2.imwrite(photo_path, frame)

    return photo_path