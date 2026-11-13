
from ultralytics import YOLO
import cv2

# Charger le modèle YOLO
model = YOLO("yolov8n.pt")


def detect_phone(frame):

    results = model.predict(
        source=frame,
        conf=0.15,
        imgsz=640,
        verbose=False
    )

    phone_count = 0

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # Vérifier le nom de la classe
            class_name = result.names[class_id]

            if class_name == "cell phone":

                phone_count += 1

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                # Rectangle rouge
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3
                )

                # Nom et confiance
                label = f"PHONE {confidence:.0%}"

                cv2.putText(
                    frame,
                    label,
                    (x1, max(y1 - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

    return frame, phone_count
