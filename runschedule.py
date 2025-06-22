import threading
import time
import subprocess
import logging
import sys
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import pystray
import io
import random
from contextlib import redirect_stdout, redirect_stderr
import win32com.client 
import tkinter as tk
from tkinter import messagebox

# ----- LOGGING CONFIG -----

name = os.path.splitext(os.path.basename(sys.argv[2]))[0] if len(sys.argv) > 1 else "scheduler"
log_folder = os.path.join(os.path.dirname(__file__), 'TaskLogs')
os.makedirs(log_folder, exist_ok=True)
log_path = os.path.join(log_folder, f'{name}Logs.log')

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info("Logging setup successful")


running = True

# ----- SCRIPT EXECUTION -----

def main_function(pythonw_path, script_path):
    with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
        try:
            result = subprocess.run(
                [pythonw_path, script_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            logging.error(f"Script failed with return code {e.returncode}")
            logging.error(f"Output: {e.output}")
            logging.error(f"Error: {e.stderr}")
        except Exception:
            logging.exception("Unexpected error running python file:")
        output = buf.getvalue()

    if output.strip():
        logging.info("Output of the script:\n" + output)

    logging.info('The python file was run successfully.')

# ----- CUSTOM SCHEDULER -----

def scheduler_loop(script_path, freq_type, pythonw_path, *args):
    global running
    next_run = datetime.now()

    while running:
        now = datetime.now()
        if now >= next_run:
            main_function(pythonw_path, script_path)

            if freq_type == "every_seconds":
                next_run = now + timedelta(seconds=int(args[0]))
                print(next_run)
            elif freq_type == "every_minutes":
                next_run = now + timedelta(minutes=int(args[0]))
            elif freq_type == "every_hours":
                next_run = now + timedelta(hours=int(args[0]))
            elif freq_type == "every_days":
                next_run = now + timedelta(days=int(args[0]))
            elif freq_type == "daily_at":
                t = datetime.strptime(args[0], "%H:%M").time()
                next_run = datetime.combine(now.date(), t)
                if now >= next_run:
                    next_run += timedelta(days=1)
            elif freq_type == "weekly_at":
                try:
                    weekday = args[0].lower()
                    time_str = args[1]
                    target_day = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(weekday)
                    t = datetime.strptime(time_str, "%H:%M").time()
                    next_run = datetime.combine(now.date(), t)
                    days_ahead = (target_day - now.weekday() + 7) % 7
                    if days_ahead == 0 and now >= next_run:
                        days_ahead = 7
                    next_run += timedelta(days=days_ahead)
                except Exception as e:
                    logging.error(f"Error in weekly_at schedule parsing: {e}")
                    return

            logging.info(f"Next run scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(1)

# ----- SYSTEM TRAY ICON -----

def on_quit(icon):
    global running
    running = False
    icon.stop()
    logging.info("Terminating task.")

# ----- ICON MENU -----

def show_details(file_path, freq_type, schedule_args, autostart_arg):
    arg1 = schedule_args[0] if len(schedule_args) > 0 else "N/A"
    arg2 = schedule_args[1] if len(schedule_args) > 1 else "N/A"

    schedule_types = {
        'every_seconds': f'Every {arg1} seconds',
        'every_minutes': f'Every {arg1} minutes',
        'every_hours':  f'Every {arg1} hours',
        'every_days':   f'Every {arg1} days',
        'daily_at':     f'Everyday at {arg1}',
        'weekly_at':    f'Every {arg1} at {arg2}'
    }

    info = (
        f"Script Path:\n{file_path}\n\n"
        f"Schedule:\n{schedule_types.get(freq_type, 'Unknown')}\n\n"
        f"Autostart:\n{'Yes' if autostart_arg else 'No'}"
    )

    root = tk.Tk()
    root.withdraw() 

    messagebox.showinfo("Task Details", info)

    root.destroy() 

# ----- CUSTOM ICON -----

def create_icon_from_filename(script_path):
    name = os.path.basename(script_path).split('.')[0]
    words = ' '.join(name.replace('_', ' ').title().split())[:4]

    bg_r, bg_g, bg_b = [random.randint(100, 255) for _ in range(3)]
    bg_color = (bg_r, bg_g, bg_b, 255)

    luminance = 0.299 * bg_r + 0.587 * bg_g + 0.114 * bg_b
    text_color = (0, 0, 0) if luminance > 160 else (255, 255, 255)

    img = Image.new('RGBA', (64, 64), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), words, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (64 - text_width) // 2
    y = (64 - text_height) // 2

    draw.text((x, y), words, font=font, fill=text_color)

    icons_path = os.path.join(os.path.dirname(__file__), 'Icons')
    os.makedirs(icons_path, exist_ok=True)

    base_icon_name = f"{name}Icon"
    icon_name = f"{base_icon_name}.ico"
    counter = 1
    while os.path.exists(os.path.join(icons_path, icon_name)):
        icon_name = f"{base_icon_name}_{counter}.ico"
        counter += 1

    output_path = os.path.join(icons_path, icon_name)
    img.save(output_path, format='ICO')
    return icon_name

# ----- ADD TASK TO STARTUP -----

def add_to_startup(pythonw_path, file_path, freq_type, schedule_args, icon_name, startup):
    startup_path = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup_path, f"{name}_Startup.lnk")

    script = os.path.abspath(__file__)
    args_string = f'"{script}" "{file_path}" {freq_type} {" ".join(schedule_args)} "{str(icon_name).strip().lower()}" {str(startup).lower()}'

    if not os.path.exists(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = pythonw_path
        shortcut.Arguments = args_string
        shortcut.WorkingDirectory = os.path.dirname(script)
        if icon_name and str(icon_name).strip().lower() not in ("random", "none"):
            icons_path = os.path.join(os.path.dirname(__file__), 'icons')
            icon_path = os.path.join(icons_path, icon_name)
            if os.path.isfile(icon_path):
                shortcut.IconLocation = icon_path
        else:
            shortcut.IconLocation = pythonw_path
        shortcut.save()
        logging.info(f"Added to startup: {shortcut_path}")

# ----- ICON DISPLAYING MAIN CODE -----

def setup_tray_icon(file_path, startup=None, icon_name=None, pythonw_path=None, freq_type=None, schedule_args=None):
    script_name = os.path.splitext(os.path.basename(file_path))[0]
    icons_path = os.path.join(os.path.dirname(__file__), 'icons')

    if icon_name and str(icon_name).strip().lower() != "none":
        menu = pystray.Menu(
            pystray.MenuItem("Details", lambda _: show_details(file_path, freq_type, schedule_args, startup)),
            pystray.MenuItem("Exit", on_quit)
        )
        icon = pystray.Icon(script_name)

        try:
            if str(icon_name).strip().lower() == "random":
                default_name = create_icon_from_filename(file_path)
                icon.icon = Image.open(os.path.join(icons_path, default_name))
            else:
                custom_icon_path = os.path.join(icons_path, icon_name)
                if os.path.isfile(custom_icon_path):
                    icon.icon = Image.open(custom_icon_path)
                else:
                    raise FileNotFoundError(f"Icon not found: {custom_icon_path}")
        except Exception as e:
            logging.error(f"Failed to load icon: {e}")
            return  # Exit early if icon loading fails

        icon.menu = menu
        icon.title = f"{script_name} Task"

        threading.Thread(target=icon.run, daemon=True).start()

    if startup and pythonw_path:
        try:
            add_to_startup(pythonw_path, file_path, freq_type, schedule_args, icon_name, startup)
        except Exception as e:
            logging.error(f"Failed to add to startup: {e}")

# ----- ENTRY POINT -----

if __name__ == "__main__":
    pythonw_path = sys.argv[1]
    script_path = sys.argv[2]
    freq_type = sys.argv[3]

    if freq_type == "weekly_at":
        schedule_args = sys.argv[4:6]
        icon_arg = sys.argv[6] if len(sys.argv) > 6 else "random"
        autostart_arg = sys.argv[7] if len(sys.argv) > 7 else "no"
    else:
        schedule_args = [sys.argv[4]]
        icon_arg = sys.argv[5] if len(sys.argv) > 5 else "random"
        autostart_arg = sys.argv[6] if len(sys.argv) > 6 else "no"

    args = schedule_args  

    if not os.path.isfile(script_path):
        print(f"Script file {script_path} not found.")
        sys.exit(1)

    thread = threading.Thread(target=scheduler_loop, args=(script_path, freq_type, pythonw_path, *args), daemon=True)
    thread.start()

    autostart = autostart_arg.lower() == "yes"

    setup_tray_icon(
        file_path=script_path,
        icon_name=icon_arg,
        startup=autostart,
        pythonw_path=pythonw_path,
        freq_type=freq_type,
        schedule_args=schedule_args
    )
