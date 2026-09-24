
import cv2
import numpy as np

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
    faces=face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
     #draw rectangle around faces

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return True, image

    return False , image