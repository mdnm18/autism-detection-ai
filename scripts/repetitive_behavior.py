import cv2
import mediapipe as mp
import numpy as np
from collections import deque

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# To store motion history
motion_buffer = deque(maxlen=20)  # adjust for smoothing
repetition_count = 0

cap = cv2.VideoCapture(0)
print("Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb_frame)

    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract wrist Y positions
        left_wrist = result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

        wrist_avg_y = (left_wrist.y + right_wrist.y) / 2
        motion_buffer.append(wrist_avg_y)

        # Check for repeated up-down motion (very simple pattern detection)
        if len(motion_buffer) == motion_buffer.maxlen:
            std_dev = np.std(motion_buffer)
            if std_dev > 0.02:  # threshold for movement variance
                repetition_count += 1
                cv2.putText(frame, f"Repetitive Movement Detected!", (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show the frame
    cv2.imshow("Repetitive Behavior Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"Total repetitive motion instances detected: {repetition_count}")