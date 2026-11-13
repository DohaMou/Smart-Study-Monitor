
import os
import sys
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import mediapipe as mp
from PIL import Image, ImageTk
import pygame

# ==========================================
# CHEMIN DU PROJET
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from detection.face_detection import detect_faces
from detection.eye_detection import detect_eyes
from detection.phone_detection import detect_phone


class SmartStudyApp:

    def __init__(self, root):

        self.root = root
        self.root.title("SMART STUDY MONITOR")
        self.root.geometry("1350x900")
        self.root.minsize(1100, 750)
        self.root.configure(bg="#211A2E")
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # CHRONOMETRE
        self.study_running = False
        self.study_start = None
        self.elapsed = 0

        # SURVEILLANCE
        self.monitoring = True
        self.closed_start = None
        self.alert_duration = 2.0

        self.eye_alerts = 0
        self.phone_detections = 0
        self.focus_score = 100

        self.previous_eye_alert = False
        self.previous_phone_alert = False

        # ALARMES SONORES : un son par type d'alerte
        self.alarm_ready = False
        self.eye_alarm_path = os.path.join(BASE_DIR, "sounds", "wake_up.mp3")
        self.phone_alarm_path = os.path.join(BASE_DIR, "sounds", "phone_alert.mp3")
        self.current_alarm = None
        # Evite les changements rapides de son si YOLO perd le téléphone
        # pendant quelques images.
        self.last_phone_alert_time = 0.0
        self.last_eye_alert_time = 0.0
        self.phone_alarm_hold = 1.0
        self.eye_alarm_hold = 0.4

        # CAMERA
        self.camera = None
        self.face_mesh = None

        # INTERFACE
        self.create_interface()

        try:
            self.initialize_models()
            self.initialize_alarm()
        except Exception as error:
            messagebox.showerror(
                "Initialization error",
                str(error)
            )
            self.close_app()
            return

        # DEMARRAGE AUTOMATIQUE DU CHRONOMETRE
        self.start_study()

        # LANCEMENT DES MISES A JOUR
        self.update_timer()
        self.update_camera()

    # ==========================================
    # INTERFACE
    # ==========================================

    def create_interface(self):

        self.sidebar = tk.Frame(
            self.root,
            bg="#191321",
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="SMART\nSTUDY",
            font=("Arial", 25, "bold"),
            fg="#A987D5",
            bg="#191321",
            justify="left"
        ).pack(pady=35, padx=20, anchor="w")

        tk.Label(
            self.sidebar,
            text="MAIN MENU",
            font=("Arial", 10, "bold"),
            fg="#B9A9CA",
            bg="#191321"
        ).pack(anchor="w", padx=22, pady=(20, 12))

        for item in ["Dashboard", "Live Camera", "Statistics"]:

            tk.Button(
                self.sidebar,
                text="   " + item,
                font=("Arial", 12),
                fg="white",
                bg="#382B49",
                activebackground="#49375D",
                activeforeground="#A987D5",
                anchor="w",
                padx=10,
                pady=15,
                relief="flat",
                cursor="hand2",
                command=lambda name=item: self.navigate(name)
            ).pack(fill="x", padx=12, pady=6)

        tk.Label(
            self.sidebar,
            text="● CAMERA ACTIVE",
            font=("Arial", 10, "bold"),
            fg="#A987D5",
            bg="#191321"
        ).pack(side="bottom", pady=30)

        # ZONE PRINCIPALE
        self.main = tk.Frame(
            self.root,
            bg="#211A2E"
        )
        self.main.pack(
            side="left",
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        header = tk.Frame(self.main, bg="#211A2E")
        header.pack(fill="x", pady=(0, 20))

        self.page_title = tk.Label(
            header,
            text="Study Dashboard",
            font=("Arial", 26, "bold"),
            fg="white",
            bg="#211A2E"
        )
        self.page_title.pack(side="left")

        self.status_label = tk.Label(
            header,
            text="● MONITORING",
            font=("Arial", 11, "bold"),
            fg="#A987D5",
            bg="#211A2E"
        )
        self.status_label.pack(side="right")

        # CONTENU
        self.content = tk.Frame(self.main, bg="#211A2E")
        self.content.pack(fill="both", expand=True)

        # CAMERA
        self.camera_panel = tk.Frame(
            self.content,
            bg="#382B49",
            highlightthickness=1,
            highlightbackground="#49375D"
        )
        self.camera_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

        tk.Label(
            self.camera_panel,
            text="LIVE CAMERA",
            font=("Arial", 13, "bold"),
            fg="#A987D5",
            bg="#382B49"
        ).pack(anchor="w", padx=15, pady=12)

        self.camera_label = tk.Label(
            self.camera_panel,
            text="Loading camera...",
            font=("Arial", 15),
            fg="white",
            bg="#191321"
        )
        self.camera_label.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        # STATISTIQUES
        self.stats_panel = tk.Frame(
            self.content,
            bg="#211A2E",
            width=270
        )
        self.stats_panel.pack(side="right", fill="y")
        self.stats_panel.pack_propagate(False)

        self.timer_value = self.create_card(
            self.stats_panel, "STUDY TIME", "00:00:00"
        )

        self.focus_value = self.create_card(
            self.stats_panel, "FOCUS SCORE", "100%"
        )

        self.eye_value = self.create_card(
            self.stats_panel, "EYE ALERTS", "0"
        )

        self.phone_value = self.create_card(
            self.stats_panel, "PHONE DETECTIONS", "0"
        )

        # BAS DE PAGE
        self.bottom = tk.Frame(self.main, bg="#211A2E")
        self.bottom.pack(fill="x", pady=15)

        self.activity_label = tk.Label(
            self.bottom,
            text="Study session running",
            font=("Arial", 11, "bold"),
            fg="#A987D5",
            bg="#211A2E"
        )
        self.activity_label.pack(side="left")

        buttons = tk.Frame(self.bottom, bg="#211A2E")
        buttons.pack(side="right")

        tk.Button(
            buttons,
            text="START STUDY",
            command=self.start_study,
            bg="#A987D5",
            fg="#211A2E",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10,
            relief="flat"
        ).pack(side="left", padx=5)

        tk.Button(
            buttons,
            text="PAUSE",
            command=self.pause_study,
            bg="#D9A66F",
            fg="#211A2E",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10,
            relief="flat"
        ).pack(side="left", padx=5)

        tk.Button(
            buttons,
            text="RESET",
            command=self.reset_study,
            bg="#E47B83",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10,
            relief="flat"
        ).pack(side="left", padx=5)

    # ==========================================
    # CARTES
    # ==========================================

    def create_card(self, parent, title, value):

        card = tk.Frame(
            parent,
            bg="#382B49",
            height=135
        )
        card.pack(fill="x", pady=8)
        card.pack_propagate(False)

        tk.Label(
            card,
            text=title,
            font=("Arial", 10, "bold"),
            fg="#B9A9CA",
            bg="#382B49"
        ).pack(pady=(20, 8))

        label = tk.Label(
            card,
            text=value,
            font=("Arial", 25, "bold"),
            fg="#A987D5",
            bg="#382B49"
        )
        label.pack()

        return label

    # ==========================================
    # NAVIGATION
    # ==========================================

    def navigate(self, page):

        if page == "Dashboard":

            self.page_title.config(text="Study Dashboard")

            self.camera_panel.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 15)
            )

            self.stats_panel.pack(side="right", fill="y")

        elif page == "Live Camera":

            self.page_title.config(text="Live Camera")

            self.stats_panel.pack_forget()

            self.camera_panel.pack(
                side="left",
                fill="both",
                expand=True,
                padx=0
            )

        elif page == "Statistics":

            self.page_title.config(text="Study Statistics")

            self.camera_panel.pack_forget()

            self.stats_panel.pack(
                side="left",
                fill="both",
                expand=True
            )

        self.activity_label.config(text=page)

    # ==========================================
    # MODELES ET CAMERA
    # ==========================================

    def initialize_models(self):

        face_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        self.face_cascade = cv2.CascadeClassifier(face_path)

        if self.face_cascade.empty():
            raise RuntimeError("Face model not found")

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.camera = cv2.VideoCapture(
            0,
            cv2.CAP_DSHOW
        )

        if not self.camera.isOpened():
            raise RuntimeError("Cannot open webcam")

    # ==========================================
    # ALARMES SONORES
    # ==========================================

    def initialize_alarm(self):
        """Vérifie les deux fichiers et initialise le lecteur audio."""
        missing = [path for path in (self.eye_alarm_path, self.phone_alarm_path)
                   if not os.path.isfile(path)]
        if missing:
            raise FileNotFoundError(
                "Fichier(s) audio introuvable(s) :\n" + "\n".join(missing)
            )

        pygame.mixer.init()
        self.alarm_ready = True

    def start_alarm(self, alarm_type):
        """Joue le son correspondant en boucle, sans le relancer à chaque image."""
        if not self.alarm_ready or not pygame.mixer.get_init():
            return

        alarm_paths = {
            "eyes": self.eye_alarm_path,
            "phone": self.phone_alarm_path,
        }
        path = alarm_paths.get(alarm_type)
        if path is None:
            return

        # Un seul flux audio est utilisé. On arrête toujours l'ancien son
        # avant de charger le nouveau.
        if self.current_alarm != alarm_type or not pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=-1)
            self.current_alarm = alarm_type

    def stop_alarm(self):
        """Arrête le son et réinitialise le type d'alerte en cours."""
        if self.alarm_ready and pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.current_alarm = None

    # ==========================================
    # CHRONOMETRE
    # ==========================================

    def start_study(self):

        if not self.study_running:

            self.study_start = time.monotonic() - self.elapsed
            self.study_running = True

            self.activity_label.config(
                text="Study session running"
            )

    def pause_study(self):

        if self.study_running:

            self.elapsed = time.monotonic() - self.study_start
            self.study_running = False

            self.activity_label.config(
                text="Study session paused"
            )

    def reset_study(self):

        self.study_running = False
        self.elapsed = 0
        self.study_start = None

        self.timer_value.config(text="00:00:00")

        self.activity_label.config(
            text="Study session reset"
        )

    def update_timer(self):

        if self.study_running:
            self.elapsed = time.monotonic() - self.study_start

        total_seconds = int(self.elapsed)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        self.timer_value.config(
            text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )

        if self.monitoring:
            self.root.after(250, self.update_timer)

    # ==========================================
    # CAMERA ET DETECTIONS
    # ==========================================

    def update_camera(self):

        if not self.monitoring:
            return

        success, frame = self.camera.read()

        if success:

            frame = cv2.flip(frame, 1)

            # Visage
            frame, face_count = detect_faces(
                frame,
                self.face_cascade
            )

            # Yeux
            frame, eye_status = detect_eyes(
                frame,
                self.face_mesh
            )

            # Telephone
            frame, phone_count = detect_phone(frame)

            # Yeux fermes
            eyes_alert = False

            if face_count == 0 or eye_status == "FACE NOT DETECTED":

                self.closed_start = None

            elif eye_status == "EYES CLOSED":

                if self.closed_start is None:
                    self.closed_start = time.monotonic()

                if time.monotonic() - self.closed_start >= self.alert_duration:
                    eyes_alert = True

            else:
                self.closed_start = None

            # Compteurs d'alertes
            if eyes_alert and not self.previous_eye_alert:
                self.eye_alerts += 1

            if phone_count > 0 and not self.previous_phone_alert:
                self.phone_detections += 1

            self.previous_eye_alert = eyes_alert
            self.previous_phone_alert = phone_count > 0

            # SON : un seul son à la fois, avec priorité au téléphone.
            # Petite temporisation pour éviter les bascules rapides lorsque
            # la détection du téléphone disparaît pendant quelques images.
            now = time.monotonic()
            if phone_count > 0:
                self.last_phone_alert_time = now
            if eyes_alert:
                self.last_eye_alert_time = now

            if now - self.last_phone_alert_time < self.phone_alarm_hold:
                desired_alarm = "phone"
            elif now - self.last_eye_alert_time < self.eye_alarm_hold:
                desired_alarm = "eyes"
            else:
                desired_alarm = None

            if desired_alarm is not None:
                self.start_alarm(desired_alarm)
            else:
                self.stop_alarm()

            # Score indicatif
            self.focus_score = max(
                0,
                100 - self.eye_alerts * 5
                - self.phone_detections * 10
            )

            self.eye_value.config(text=str(self.eye_alerts))
            self.phone_value.config(text=str(self.phone_detections))
            self.focus_value.config(text=f"{self.focus_score}%")

            # Affichage camera
            frame = cv2.resize(frame, (700, 480))

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(rgb)
            photo = ImageTk.PhotoImage(image=image)

            self.camera_label.config(
                image=photo,
                text=""
            )

            self.camera_label.image = photo

            # Statut
            if phone_count > 0:
                self.activity_label.config(text="PHONE DETECTED!")

            elif eyes_alert:
                self.activity_label.config(
                    text="EYES CLOSED - TAKE A BREAK"
                )

            elif face_count > 0:
                self.activity_label.config(
                    text="FOCUS MONITORING ACTIVE"
                )

            else:
                self.activity_label.config(
                    text="FACE NOT DETECTED"
                )

        self.root.after(80, self.update_camera)

    # ==========================================
    # FERMETURE
    # ==========================================

    def close_app(self):

        self.monitoring = False
        self.stop_alarm()

        if self.camera is not None:
            self.camera.release()

        if self.face_mesh is not None:
            self.face_mesh.close()

        if pygame.mixer.get_init():
            pygame.mixer.quit()

        self.root.destroy()


# ==========================================
# LANCEMENT
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()
    app = SmartStudyApp(root)
    root.mainloop()
