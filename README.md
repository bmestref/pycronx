# pycronx
A Python-powered task scheduler built as a lightweight alternative to Windows Task Scheduler, fully scriptable, cross-platform, user friendly and cron-compatible. Task scheduling, the Pythonic way. 

## Key Features
- Unlike Windows Task Scheduler, permissions are handled internally so cross-platform python files are supported (as an example, it enables to interact with Outlook without employing Azure services). <br/>
- Task manager GUI to interact directly with tasks, enabling creation or termination of an unlimited number of tasks. <br/>
- You can schedule tasks to be run from the computer startup with custom schedules (every N seconds, every N minutes, every N hours, everyday at HH:MM, weekly at  <weekday> HH:MM). <br/>
- Additionally, you will be able to pick between running the task silently or displaying an icon (automatically generated or picked by yourself) bottom-right Windows taskbar icon menu,
  from where details of the task can be consulted as well as terminated. Icons will be automatically saved to the generated ```Icons``` folder.<br/>
- Track the performance of yours tasks checking the self-generated log file of the task within the ```TaskLogs``` folder. <br/>

## Repo structure
```
pycronx/
│
├── PyCronX.bat              # Main code 
├── TaskScheduler.py         # Calls runschedule.py and setups the GUI
├── requirements.txt         # Dependencies
├── runschedule.py           # Runs the target python script
├── test.py                  # Test function
└── README.md
```

## Setup
First, clone this repo to your local machine: <br/>
```
git clone https://github.com/bmestref/pycronx.git
```
Next, create an environment to alocate the required libraries (only two libraries are required: ```Pillow``` and ```pystray```) via ```venv```: <br/>
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Or optionally via ```conda```: <br/>
```
conda create -n pycronx_env python=3.10
conda activate pycronx_env
pip install -r requirements.txt
```
If not using ```requirements.txt```, install straightforwardly these libraries: <br/>
```
pip install pillow pystray
```

## Running the App
To launch the GUI scheduler interface in case python is not installed in your local machine: <br>

### Option 1: From Python
```
<path of python.exe file from pycronx_env> TaskScheduler.py
```

### Option 2: From .bat file 
Double-click on the .bat file in case python is installed: <br/>

## Usage
1- Launch the GUI. <br/>

2 - Click "Add Task" to schedule a new Python script. <br/>

3 - Set: <br/>

  - Pythonw.exe path (can be found on your pycronx_env environment folder) <br/>
  - Script path <br/>
  - Interval/frequency schedule <br/>
  - Display icon or run silently <br/>
  - Set to run the script when computer startup <br/>
    
4 - Click "Start" to run the task. <br/>

5 - After launching, a small icon appears in the Windows taskbar tray (bottom-right) if the display icon was selected. <br/>

6 - Right-click the icon to access quick actions: <br/>

  - Open the interface <br/>
  - View scheduled tasks <br/>
  - Exit the application <br/>
    
This enables background execution with minimal UI interference. <br/>

For additional information, please see the video below. <br/>
[Demostration video](video_demostration.mp4)
