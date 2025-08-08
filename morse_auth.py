import cv2
import mediapipe as mp
import time
import os

# === CONFIGURATION ===
STORED_PASSWORD = "...---..."  # You can change this
FOLDER_PATH = r"C:\Users\HP\OneDrive\Desktop\Morse"  # Your folder path

DOT_THRESHOLD = 0.25  # Max blink time for dot
BLINK_DISTANCE_THRESHOLD = 5
COOLDOWN_TIME = 0.8

# === INITIALIZATION ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
cap = cv2.VideoCapture(0)

input_code = ""
blink_started = False
blink_start_time = 0
last_blink_time = 0
status_message = "Blink to enter Morse code"

def open_folder():
    try:
        os.system(f'attrib -h -s "{FOLDER_PATH}"')
        os.startfile(FOLDER_PATH)
    except Exception as e:
        print(f"Failed to open folder: {e}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    ih, iw, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0]

        # Get left eye landmarks (145 = top lid, 159 = bottom lid)
        top_lid = landmarks.landmark[145]
        bottom_lid = landmarks.landmark[159]
        top_y = top_lid.y * ih
        bottom_y = bottom_lid.y * ih
        blink_distance = abs(top_y - bottom_y)

        # Draw a green circle over the left eye (landmark 145)
        eye_x = int(landmarks.landmark[145].x * iw)
        eye_y = int(landmarks.landmark[145].y * ih)
        cv2.circle(frame, (eye_x, eye_y), 15, (0, 255, 0), 2)

        now = time.time()

        if blink_distance < BLINK_DISTANCE_THRESHOLD:
            if not blink_started:
                blink_started = True
                blink_start_time = now
        elif blink_started:
            blink_duration = now - blink_start_time
            if now - last_blink_time > COOLDOWN_TIME:
                if blink_duration < DOT_THRESHOLD:
                    input_code += "."
                else:
                    input_code += "-"
                last_blink_time = now
            blink_started = False

    # Display current morse input
    cv2.putText(frame, f"Morse Input: {input_code}", (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(frame, status_message, (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)

    # Instructions
    cv2.putText(frame, "Short Blink = .   Long Blink = -", (30, ih - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 255), 1)
    cv2.putText(frame, "Press ENTER to Submit | R to Reset | Q to Quit", (30, ih - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 255), 1)

    cv2.imshow("Eye Blink Morse Auth", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("r"):
        input_code = ""
        status_message = "Reset successful. Start blinking again..."
    elif key == 13:  # Enter
        if input_code == STORED_PASSWORD:
            status_message = "✅ Access Granted"
            open_folder()
        else:
            status_message = "❌ Access Denied"
        input_code = ""

cap.release()
cv2.destroyAllWindows()
