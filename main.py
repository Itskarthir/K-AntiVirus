# Importing the necessary libraries
import time
import cv2
import dlib
import pyttsx3
from scipy.spatial import distance
# import serial # Uncomment if you intend to use Arduino

# Initialize text-to-speech engine
audiogen = pyttsx3.init()

# Setting up camera
cap = cv2.VideoCapture(0)

# Initialize face detector and facial landmark predictor
face_detector = dlib.get_frontal_face_detector()
dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to calculate eye aspect ratio
def detect_eye(eye):
    poi_A = distance.euclidean(eye[1], eye[5])
    poi_B = distance.euclidean(eye[2], eye[4])
    poi_C = distance.euclidean(eye[0], eye[3])
    aspect_ratio_eye = (poi_A + poi_B) / (2 * poi_C)
    return aspect_ratio_eye

# Function to calculate mouth aspect ratio
def detect_mouth(mouth):
    poi_A = distance.euclidean(mouth[2], mouth[10])
    poi_B = distance.euclidean(mouth[4], mouth[8])
    poi_C = distance.euclidean(mouth[0], mouth[6])
    aspect_ratio_mouth = (poi_A + poi_B) / (2 * poi_C)
    return aspect_ratio_mouth

# Start time for drowsiness detection
start_time = None

# Main loop to process video frames
while True:
    _, frame = cap.read()
    gray_scale = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = face_detector(gray_scale)

    for face in faces:
        face_landmarks = dlib_facelandmark(gray_scale, face)
        left_eye, right_eye, mouth = [], [], []

        # Get coordinates for right eye (points 42 to 47)
        for n in range(42, 48):
            x, y = face_landmarks.part(n).x, face_landmarks.part(n).y
            right_eye.append((x, y))
            next_point = 42 if n == 47 else n + 1
            x2, y2 = face_landmarks.part(next_point).x, face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

        # Get coordinates for left eye (points 36 to 41)
        for n in range(36, 42):
            x, y = face_landmarks.part(n).x, face_landmarks.part(n).y
            left_eye.append((x, y))
            next_point = 36 if n == 41 else n + 1
            x2, y2 = face_landmarks.part(next_point).x, face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (255, 255, 0), 1)

        # Get coordinates for mouth (points 48 to 67)
        for n in range(48, 68):
            x, y = face_landmarks.part(n).x, face_landmarks.part(n).y
            mouth.append((x, y))
            next_point = 48 if n == 67 else n + 1
            x2, y2 = face_landmarks.part(next_point).x, face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (0, 0, 255), 1)

        # Calculate aspect ratios for eyes and mouth
        right_eye_ratio = detect_eye(right_eye)
        left_eye_ratio = detect_eye(left_eye)
        eye_ratio = (left_eye_ratio + right_eye_ratio) / 2
        mouth_ratio = detect_mouth(mouth)

        # Check for drowsiness (eye ratio < 0.25)
        if eye_ratio < 0.25:
            if start_time is None:
                start_time = time.time()
            elif time.time() - start_time >= 1.25:
                cv2.putText(frame, "DROWSINESS DETECTED", (50, 100),
                            cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 210), 3)
                audiogen.say("Please wake up")
                audiogen.runAndWait()
                if time.time() - start_time >= 8:
                    # Data can be sent to Arduino here, e.g., ser.write(b'off')
                    pass  # Placeholder for Arduino communication if needed

        # Check for yawning (mouth ratio > 0.5)
        elif mouth_ratio > 0.5:
            if start_time is None:
                start_time = time.time()
            elif time.time() - start_time >= 1.25:
                cv2.putText(frame, "YAWNING DETECTED", (50, 100),
                            cv2.FONT_HERSHEY_PLAIN, 2, (21, 56, 210), 3)
                audiogen.say("Please stop yawning")
                audiogen.runAndWait()
        else:
            start_time = None

    # Display the frame with detection results
    cv2.imshow("Drowsiness Detector", frame)
    key = cv2.waitKey(9)
    if key == 20:  # Exit if '20' key is pressed
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
