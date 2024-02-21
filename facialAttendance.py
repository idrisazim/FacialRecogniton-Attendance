import cv2
import face_recognition
import os
import pickle
from datetime import datetime

# Function to load face encodings from a file
def load_encodings():
    if os.path.exists('encodings.pickle'):
        with open('encodings.pickle', 'rb') as f:
            encodings = pickle.load(f)
        return encodings
    else:
        return {}

# Function to save face encodings to a file
def save_encodings(encodings):
    with open('encodings.pickle', 'wb') as f:
        pickle.dump(encodings, f)

# Load existing face encodings
face_encodings = load_encodings()

# Set to store names of faces for which attendance has been logged
attendance_logged_faces = set()

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # Set height
while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # Find face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    current_face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding, face_location in zip(current_face_encodings, face_locations):
        # Check if the face is already known
        matches = face_recognition.compare_faces(list(face_encodings.values()), face_encoding)
        name = "Unknown"

        # If a match is found, use the name of the known face
        if True in matches:
            first_match_index = matches.index(True)
            name = list(face_encodings.keys())[first_match_index]
        else:
            # If the face is unknown, prompt the user to enter a name
            name = input("Enter the name for this face: ")
            face_encodings[name] = face_encoding
            save_encodings(face_encodings)

        # Draw a rectangle around the face and display the name
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Log attendance if the face is not in the set
        if name not in attendance_logged_faces:
            with open('attendance.txt', 'a') as log_file:
                log_file.write(f"{name}\n")
            attendance_logged_faces.add(name)

    # Display the frame with face detection
    cv2.imshow('Face Recognition', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()
