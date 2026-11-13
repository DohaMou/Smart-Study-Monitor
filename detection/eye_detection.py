
import cv2
import mediapipe as mp
import math

# Points de repère autour des yeux
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]


def calculate_eye_ratio(landmarks, eye_points, width, height):

    points = []

    for index in eye_points:
        landmark = landmarks[index]

        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

    # Distances verticales
    vertical1 = math.dist(points[1], points[5])
    vertical2 = math.dist(points[2], points[4])

    # Distance horizontale
    horizontal = math.dist(points[0], points[3])

    if horizontal == 0:
        return 0

    ratio = (vertical1 + vertical2) / (2.0 * horizontal)

    return ratio


def detect_eyes(frame, face_mesh):

    height, width = frame.shape[:2]

    # Conversion BGR vers RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = face_mesh.process(rgb_frame)

    status = "FACE NOT DETECTED"
    average_ratio = None

    if results.multi_face_landmarks:

        landmarks = results.multi_face_landmarks[0].landmark

        # Calcul du ratio de chaque œil
        left_ratio = calculate_eye_ratio(
            landmarks,
            LEFT_EYE,
            width,
            height
        )

        right_ratio = calculate_eye_ratio(
            landmarks,
            RIGHT_EYE,
            width,
            height
        )

        average_ratio = (left_ratio + right_ratio) / 2

        # Seuil initial à calibrer
        threshold = 0.20

        if average_ratio < threshold:
            status = "EYES CLOSED"
        else:
            status = "EYES OPEN"

        # Afficher le ratio
        cv2.putText(
            frame,
            f"Eye ratio: {average_ratio:.2f}",
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

    # Couleur selon l'état des yeux
    if status == "EYES CLOSED":
        color = (0, 0, 255)
    elif status == "EYES OPEN":
        color = (0, 255, 0)
    else:
        color = (0, 165, 255)

    cv2.putText(
        frame,
        status,
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2
    )

    return frame, status
