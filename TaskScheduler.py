import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import subprocess
import uuid
import json
import os

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def refresh_list():
    for i in task_list.get_children():
        task_list.delete(i)
    for tid, info in tasks.items():
        task_list.insert("", "end", iid=tid, values=(
            info.get("script", ""),
            info.get("schedule", ""),
            info.get("args", ""),
            info.get("pid", ""),
            info.get("autostart", "no")
        ))

def start_task():
    # Select pythonw.exe - must exist and be a file
    while True:
        pyw_path = filedialog.askopenfilename(title="Select pythonw.exe")
        if not pyw_path:
            return  # User cancelled
        if os.path.isfile(pyw_path) and os.path.basename(pyw_path).lower() == "pythonw.exe":
            break
        messagebox.showerror("Invalid Input", "Please select a valid pythonw.exe file.")

    # Select .py script - must exist and be a .py file
    while True:
        script_path = filedialog.askopenfilename(title="Select your .py script", filetypes=[("Python", "*.py")])
        if not script_path:
            return  # User cancelled
        if os.path.isfile(script_path) and script_path.lower().endswith(".py"):
            break
        messagebox.showerror("Invalid Input", "Please select a valid Python (.py) script.")

    # Schedule type validation - must be one of expected values
    valid_schedule_types = {"every_seconds", "every_minutes", "every_hours", "every_days", "daily_at", "weekly_at"}
    while True:
        schedule_type = simpledialog.askstring("Schedule", "Enter schedule type (e.g. every_seconds, daily_at, weekly_at):")
        if schedule_type is None:
            return  # User cancelled
        schedule_type = schedule_type.strip().lower()
        if schedule_type in valid_schedule_types:
            break
        messagebox.showerror("Invalid Input", f"Schedule type must be one of: {', '.join(valid_schedule_types)}")

    # Schedule args validation - basic validation depending on schedule_type
    while True:
        schedule_args = simpledialog.askstring("Args", "Enter schedule args (e.g. 60 or monday 09:00):")
        if schedule_args is None:
            return  # User cancelled
        schedule_args = schedule_args.strip()
        if schedule_type == "weekly_at":
            parts = schedule_args.split()
            if len(parts) == 2 and parts[0].lower() in \
                    ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                # Check time format HH:MM
                try:
                    from datetime import datetime
                    datetime.strptime(parts[1], "%H:%M")
                    break
                except ValueError:
                    pass
        else:
            # For other types, check it's a positive integer or valid time format if daily_at
            if schedule_type in {"every_seconds", "every_minutes", "every_hours", "every_days"}:
                if schedule_args.isdigit() and int(schedule_args) > 0:
                    break
            elif schedule_type == "daily_at":
                try:
                    from datetime import datetime
                    datetime.strptime(schedule_args, "%H:%M")
                    break
                except ValueError:
                    pass
        messagebox.showerror("Invalid Input", "Schedule args invalid for the selected schedule type.")

    # Icon option input - accept random icon, valid path, or 'none'
    while True:
        icon_option = simpledialog.askstring(
            "Icon Option",
            "Icon behavior:\n- Enter path to .ico file\n- Type 'random' to generate a random icon\n- Type 'none' to run in background"
        )
        if str(icon_option).lower() == "random" or str(icon_option) == "none":
            break
        elif os.path.isfile(icon_option) and icon_option.lower().endswith(".ico"):
            break
        else:
            messagebox.showerror("Invalid Input", "Please enter a valid .ico file path, type 'random' or 'none'.")
    
    icon_option = str(icon_option.strip().strip("'\""))
    icon_path = icon_option.lower()
    auto_start = messagebox.askyesno("Autostart", "Run at startup?")

    scheduler_path = os.path.join(os.path.dirname(__file__), "runschedule.py")
    args = [pyw_path, scheduler_path, pyw_path, script_path, schedule_type]

    if schedule_type == "weekly_at":
        day, time = schedule_args.split()
        args.extend([day, time])
    else:
        args.append(schedule_args)

    args.append(icon_path)
    args.append("yes" if auto_start else "no")
    autostart = args[-1]
    process = subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "pid": process.pid,
        "script": script_path,
        "schedule": schedule_type,
        "args": schedule_args,
        "autostart": autostart
    }
    save_tasks(tasks)
    refresh_list()

def get_selected_task_id():
    selected = task_list.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a task first.")
        return None
    return selected[0] 

def terminate_task(task_id):
    global tasks
    if task_id not in tasks:
        return

    task = tasks[task_id]
    pid = task.get("pid")
    autostart = str(task.get("autostart", "no")).lower() == "yes"
    script_path = task.get("script")
    name = os.path.splitext(os.path.basename(script_path))[0]

    try:
        import psutil
        proc = psutil.Process(pid)
        proc.terminate()
    except Exception as e:
        print(f"Failed to terminate process {pid}: {e}")

    # Remove autostart shortcut if enabled
    if autostart:
        startup_path = os.path.join(
            os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        )
        shortcut_path = os.path.join(startup_path, f"{name}_autostart.bat")

        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
                print(f"Removed startup shortcut: {shortcut_path}")
            except Exception as e:
                print(f"Failed to remove startup shortcut: {e}")

    # Remove from tasks dictionary and save if you want
    tasks.pop(task_id, None)
    save_tasks(tasks)
    refresh_list()

def terminate_selected_task():
    task_id = get_selected_task_id()
    if task_id:
        terminate_task(task_id)

# GUI Setup
root = tk.Tk()
root.title("PyCronX")

task_frame = ttk.Frame(root)
task_frame.pack(fill="both", expand=True)

columns = ("Script", "Schedule", "Args", "PID", "AutoStart")
task_list = ttk.Treeview(task_frame, columns=columns, show="headings")
for col in columns:
    task_list.heading(col, text=col)
task_list.pack(fill="both", expand=True, padx=5, pady=5)

btn_frame = ttk.Frame(root)
btn_frame.pack(fill="x", padx=5, pady=5)

ttk.Button(btn_frame, text="New Task", command=start_task).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Terminate Task", command=terminate_selected_task).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Refresh", command=refresh_list).pack(side="right", padx=5)

tasks = load_tasks()
refresh_list()

root.mainloop()
