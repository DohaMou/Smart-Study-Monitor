
import cv2
import mediapipe as mp
import time
import winsound
import threading

from detection.face_detection import detect_faces
from detection.eye_detection import detect_eyes
from detection.phone_detection import detect_phone


# ==========================================
# 1. CHARGEMENT DU MODELE VISAGE
# ==========================================

face_path = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

face_cascade = cv2.CascadeClassifier(face_path)

if face_cascade.empty():
    raise RuntimeError("Face detection model not found")


# ==========================================
# 2. INITIALISATION MEDIAPIPE
# ==========================================

face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ==========================================
# 3. INITIALISATION YOLO
# ==========================================

print("Loading YOLO model...")


# Le modèle est chargé dans phone_detection.py
print("YOLO READY!")


# ==========================================
# 4. OUVERTURE CAMERA
# ==========================================

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    face_mesh.close()
    raise RuntimeError("Camera unavailable")


print("SMART STUDY MONITOR STARTED")


# ==========================================
# 5. VARIABLES DE SURVEILLANCE
# ==========================================

closed_start_time = None

alert_duration = 2.0

alarm_active = threading.Event()

alarm_thread = None


# ==========================================
# 6. SYSTEME D'ALARME CONTINUE
# ==========================================

def continuous_alarm():

    while alarm_active.is_set():

        winsound.Beep(1200, 150)

        time.sleep(0.05)


def start_alarm():

    global alarm_thread

    if not alarm_active.is_set():

        alarm_active.set()

        alarm_thread = threading.Thread(
            target=continuous_alarm,
            daemon=True
        )

        alarm_thread.start()


def stop_alarm():

    alarm_active.clear()


# ==========================================
# 7. BOUCLE PRINCIPALE
# ==========================================

try:

    while True:

        success, frame = camera.read()

        if not success:
            print("Camera error")
            break

        frame = cv2.flip(frame, 1)


        # ==================================
        # 8. DETECTION VISAGE
        # ==================================

        frame, face_count = detect_faces(
            frame,
            face_cascade
        )


        # ==================================
        # 9. DETECTION YEUX
        # ==================================

        frame, eye_status = detect_eyes(
            frame,
            face_mesh
        )


        # ==================================
        # 10. DETECTION TELEPHONE
        # ==================================

        frame, phone_count = detect_phone(frame)


        # ==================================
        # 11. ALERTE YEUX FERMES
        # ==================================

        eyes_alert = False

        if face_count == 0 or eye_status == "FACE NOT DETECTED":

            closed_start_time = None

        elif eye_status == "EYES CLOSED":

            if closed_start_time is None:
                closed_start_time = time.time()

            elapsed_time = time.time() - closed_start_time

            if elapsed_time >= alert_duration:

                eyes_alert = True

                cv2.putText(
                    frame,
                    "WAKE UP! TAKE A BREAK!",
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    3
                )

        else:

            closed_start_time = None


        # ==================================
        # 12. ALERTE TELEPHONE
        # ==================================

        phone_alert = phone_count > 0

        if phone_alert:

            cv2.putText(
                frame,
                "PHONE DETECTED - STAY FOCUSED!",
                (20, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )


        # ==================================
        # 13. GESTION DES ALARMES
        # ==================================

        # Une seule alarme continue pour les deux alertes
        if eyes_alert or phone_alert:

            start_alarm()

        else:

            stop_alarm()


        # ==================================
        # 14. AFFICHAGE DES INFORMATIONS
        # ==================================

        cv2.putText(
            frame,
            f"Faces: {face_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Phones: {phone_count}",
            (20, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )


        if closed_start_time is not None:

            elapsed_time = time.time() - closed_start_time

            cv2.putText(
                frame,
                f"Closed: {elapsed_time:.1f}s",
                (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )


        # ==================================
        # 15. AFFICHAGE CAMERA
        # ==================================

        cv2.imshow(
            "SMART STUDY MONITOR",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# ==========================================
# 16. FERMETURE PROPRE
# ==========================================

finally:

    stop_alarm()

    camera.release()

    face_mesh.close()

    cv2.destroyAllWindows()

    print("SMART STUDY MONITOR STOPPED")
