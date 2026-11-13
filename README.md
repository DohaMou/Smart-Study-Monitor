# 🎓 Smart Study Monitor

### An AI-Powered Study Monitoring Application

##  About the Project

Smart Study Monitor is a Python-based application designed to help students improve their study habits, reduce distractions, and maintain better concentration during study sessions.

The application uses computer vision and artificial intelligence techniques to monitor certain visual indicators through a webcam and provide audio alerts when distractions are detected.

The main goal is to create a smarter and more productive study environment.

## Key Features

- **Face Detection:** Detects the user's face using OpenCV.
- **Eye Monitoring:** Monitors eye status using MediaPipe Face Mesh and detects prolonged eye closure.
- **Phone Detection:** Uses YOLO object detection to identify mobile phones.
- **Smart Audio Alerts:** Plays different sounds depending on the detected situation:
  - Wake Up alert when prolonged eye closure is detected.
  - Phone Alert when a mobile phone is detected.
- **Study Timer:** Tracks study session duration with start, pause, and reset controls.
- **Statistics Dashboard:** Displays study time, eye alerts, phone detections, and an indicative focus score.
- **Graphical User Interface:** Provides an interactive desktop application built with Tkinter.

##  Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Face detection and webcam processing |
| MediaPipe | Facial landmark and eye monitoring |
| YOLOv8 | Phone object detection |
| Tkinter | Graphical user interface |
| Pygame | Audio alert management |
| Pillow | Camera image display |

##  How It Works

1. The application activates the webcam.
2. It detects the user's face.
3. It monitors eye status and estimates prolonged eye closure.
4. YOLO detects whether a mobile phone is visible.
5. Audio alerts are triggered according to the detected situation.
6. The dashboard updates the study timer and statistics.

##  Project Structure

```text
Smart-Study-Monitor/
│
├── dashboard/
│   ├── app.py
│   └── __init__.py
│
├── detection/
│   ├── face_detection.py
│   ├── eye_detection.py
│   ├── phone_detection.py
│   └── __init__.py
│
├── sounds/
│   ├── wake_up.mp3
│   └── phone_alert.mp3
│
├── utils/
├── yolov8n.pt
├── requirements.txt
├── main.py
└── test_camera.py
```

##  Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/DohaMou/Smart-Study-Monitor.git
```

### 2. Navigate to the project folder

```bash
cd Smart-Study-Monitor
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment (Windows)

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python dashboard/app.py
```

## Project Objectives

- Encourage better study habits.
- Reduce distractions caused by mobile phone usage.
- Provide visual monitoring and audio feedback.
- Track study session duration.
- Explore practical applications of computer vision and AI.

## Future Improvements

- Detailed study-session history.
- Daily and weekly productivity reports.
- Improved phone detection accuracy.
- Customizable alert settings.
- More advanced statistics and visualizations.

## Author

**Doha Mou**

GitHub: [@DohaMou](https://github.com/DohaMou)

---

*Smart Study Monitor — Study smarter, stay focused, and improve your productivity.*