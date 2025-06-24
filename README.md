# PyCronX
A Python-powered task scheduler — lightweight, cross-platform, and cron-compatible — offering a Pythonic alternative to Windows Task Scheduler. With a user-friendly interface and advanced control features, PyCronX simplifies script scheduling without the complexity of system-level permissions. <br/>

## 🔧 Key Features
Cross-platform scripting: Unlike Windows Task Scheduler, PyCronX handles permissions internally, enabling the scheduling of Python scripts across platforms (including scripts that interact with Outlook without requiring Azure services). <br/>

- **Graphical Task Manager**: Launch a GUI to manage, create, or terminate an unlimited number of scheduled Python tasks.
- **Flexible Scheduling Options**:
  - Run tasks at computer startup
  - Repeat every N seconds, minutes, or hours
  - Run daily at a specific time (HH:MM)
  - Schedule weekly runs on specific weekdays at chosen times
- **System Tray Integration**: Optionally show a custom or auto-generated icon in the Windows taskbar (bottom-right corner). Right-click this icon to:
- **View task details**
- **Terminate a task**
- **Open the GUI interface**
- **Auto-generated Logs**: Monitor the performance and output of each task via auto-created log files in the TaskLogs/ directory.
- **Custom Icon Management**: All icons are stored in the auto-created Icons/ folder for future use.

## 📁 Repository Structure
```
pycronx/
│
├── PyCronX.bat              # Launches the GUI via BAT file
├── TaskScheduler.py         # Main GUI interface
├── runschedule.py           # Executes the scheduled tasks
├── test.py                  # Sample script to schedule
├── requirements.txt         # Required dependencies
└── README.md
```

## 🚀 Installation
### 1. Clone the Repository
```
git clone https://github.com/bmestref/pycronx.git
cd pycronx
```

### 2. Create Environment and Install Dependencies
- **Option A**: Using venv
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
- **Option B**: Using conda
```
conda create -n pycronx_env python=3.10
conda activate pycronx_env
pip install -r requirements.txt
```

- **Option C**: Manual Installation
```
pip install pillow pystray
```

## ▶️ Running the App
- **Option 1**: Launch from Python
```
<full-path-to-pythonw.exe> TaskScheduler.py
```
For example: <br/>
```
C:\Users\YourUser\.conda\envs\pycronx_env\pythonw.exe TaskScheduler.py
```
- **Option 2**: Launch from BAT file (if Python is installed and added to PATH)
Just double-click the PyCronX.bat file. <br/>

Note: pythonw.exe is used to avoid opening a terminal window alongside the GUI. <br/>

## 🧠 How to Use
- Launch the GUI using the BAT file or direct command.
- Click “Add Task” to create a new scheduled script.
- Configure:
  - Path to pythonw.exe
  - Path to your target script
  - Desired schedule (startup, periodic, daily, weekly)
  - Icon display settings (show/hide icon)
  - Enable startup execution
- Click “Start” to schedule the task.

If the task is set to show an icon, you'll find it in the system tray. <br/>

- Right-click the tray icon to:
  - Open the interface
  - View active tasks
  - Terminate or exit the task

## 📂 Logs and Icons
Logs for each task are saved in the TaskLogs/ folder. <br/>
Icons are stored in the Icons/ folder — you can choose your own or let the system generate them automatically. <br/>

## 🎥 Demo Video
For a complete walkthrough and example use cases, please watch the video below: <br/>
[Demostration Video](video_demostration.mp4)

