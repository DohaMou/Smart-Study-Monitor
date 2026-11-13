


# Initialiser la webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Erreur : webcam inaccessible")
    exit()

print("Smart Study Monitor - Camera active")

while True:
    success, frame = camera.read()

    if not success:
        print("Erreur de lecture")
        break

    # Afficher le titre
    cv2.putText(
        frame,
        "SMART STUDY MONITOR",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow("Smart Study Monitor", frame)

    # Appuyer sur Q pour quitter
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
