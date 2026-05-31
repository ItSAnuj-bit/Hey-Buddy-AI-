import speech_recognition as sr 
import pyttsx3
import webbrowser
import os
import json
import threading
import tkinter as tk
import time
import datetime
import subprocess
import pyautogui
import screen_brightness_control as sbc

# ----------- SELENIUM -----------
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ================= MEMORY =================

MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

memory = load_memory()

# ================= APP PATH DATABASE =================

APP_PATHS = {

    "chrome":
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",

    "edge":
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

    "vscode":
    r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",

    "notepad":
    "notepad.exe",

    "calculator":
    "calc.exe",

    "cmd":
    "cmd.exe",

    "paint":
    "mspaint.exe",
}

# ================= CHAT + ANIMATION =================

def add_chat(sender, text):

    if "chat_box" not in globals():
        return

    chat_box.config(state=tk.NORMAL)

    if sender == "user":
        chat_box.insert(tk.END, f"\n🧑 You: {text}\n")
    else:
        chat_box.insert(tk.END, f"\n🤖 Buddy: {text}\n")

    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)


circle_size = 40
animation_running = False

def animate_circle():

    global circle_size

    if animation_running:

        canvas.delete("all")

        circle_size += 3

        if circle_size > 80:
            circle_size = 40

        x0 = 400 - circle_size
        y0 = 200 - circle_size
        x1 = 400 + circle_size
        y1 = 200 + circle_size

        canvas.create_oval(
            x0, y0, x1, y1,
            outline="cyan",
            width=3
        )

        root.after(60, animate_circle)


def start_animation():

    global animation_running

    animation_running = True

    if "status_label" in globals():
        status_label.config(text="🎤 Listening...")

    animate_circle()


def stop_animation():

    global animation_running

    animation_running = False

    if "canvas" in globals():
        canvas.delete("all")

    if "status_label" in globals():
        status_label.config(text="Ready")

# ================= VOICE =================

engine = pyttsx3.init()
engine.setProperty('rate', 170)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):

    status_label.config(text=f"Assistant: {text}")

    add_chat("assistant", text)

    print("Assistant:", text)

    engine.say(text)
    engine.runAndWait()

# ================= FAST LISTEN =================

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8

def take_command():

    with sr.Microphone() as source:

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        start_animation()

        try:

            audio = recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=6
            )

        except:
            stop_animation()
            return ""

    try:

        query = recognizer.recognize_google(
            audio,
            language='en-IN'
        )

        stop_animation()

        add_chat("user", query)

        print("You:", query)

        return query.lower()

    except sr.UnknownValueError:
        stop_animation()
        return ""

    except sr.RequestError:

        stop_animation()

        speak("Internet problem")

        return ""

# ================= OPEN APP =================

def open_app(name):

    speak(f"Opening app {name}")

    name = name.lower()

    if name in APP_PATHS:

        path = os.path.expandvars(
            APP_PATHS[name]
        )

        try:
            os.startfile(path)
            return
        except:
            speak("Application failed to open")
            return

    try:
        subprocess.Popen(name)
        return
    except:
        speak("Application not found")

# ================= OPEN FOLDER =================

def open_folder(name):

    speak(f"Opening folder {name}")

    user_path = os.path.expanduser("~")

    for root_dir, dirs, files in os.walk(user_path):

        for folder in dirs:

            if name.lower() in folder.lower():

                os.startfile(
                    os.path.join(root_dir, folder)
                )

                return

    speak("Folder not found")

# ================= FULL PC SEARCH =================

def open_from_search(name):

    speak(f"Searching {name}")

    drives = ["C:\\", "D:\\", "E:\\"]

    for drive in drives:

        if not os.path.exists(drive):
            continue

        for root_dir, dirs, files in os.walk(drive):

            for folder in dirs:

                if name.lower() in folder.lower():

                    os.startfile(
                        os.path.join(root_dir, folder)
                    )

                    return

            for file in files:

                if name.lower() in file.lower():

                    os.startfile(
                        os.path.join(root_dir, file)
                    )

                    return

    speak("Not found")

# ================= SCREENSHOT =================

def take_screenshot():

    filename = f"screenshot_{int(time.time())}.png"

    pyautogui.screenshot().save(filename)

    speak("Screenshot saved")

# ================= BRIGHTNESS =================

def increase_brightness():

    current = sbc.get_brightness()[0]

    sbc.set_brightness(
        min(current + 10, 100)
    )

    speak("Brightness increased")

def decrease_brightness():

    current = sbc.get_brightness()[0]

    sbc.set_brightness(
        max(current - 10, 0)
    )

    speak("Brightness decreased")

# ================= TRAIN =================

def get_input(prompt):

    while True:

        speak(prompt)

        cmd = take_command()

        if cmd:
            return cmd

def train():

    speak("Training mode")

    cmd = get_input("What should I learn")

    reply = get_input("What should I reply")

    memory[cmd] = reply

    save_memory(memory)

    speak("Learned")

# ================= MEMORY RUN =================

def run_memory(query):

    for key in memory:

        if key in query:

            speak(memory[key])

            return True

    return False

# ================= SCHEDULE =================

def schedule_task():

    speak("Tell month")
    month = take_command()

    speak("Tell date")
    day = take_command()

    speak("Tell task")
    task = take_command()

    try:

        months = {
            "january":1,"february":2,
            "march":3,"april":4,
            "may":5,"june":6,
            "july":7,"august":8,
            "september":9,
            "october":10,
            "november":11,
            "december":12
        }

        month_num = months.get(month)

        day_num = int(
            ''.join(filter(str.isdigit, day))
        )

        year = datetime.datetime.now().year

        date_obj = datetime.date(
            year,
            month_num,
            day_num
        )

        if "schedule" not in memory:
            memory["schedule"] = []

        memory["schedule"].append({
            "date": str(date_obj),
            "task": task
        })

        save_memory(memory)

        speak("Task scheduled")

        webbrowser.open(
            "https://calendar.google.com"
        )

    except:

        speak("Invalid date")

# ================= YOUTUBE =================

def play_youtube(song):

    speak(f"Playing {song}")

    driver = webdriver.Edge()

    driver.get("https://www.youtube.com")

    time.sleep(2)

    search = driver.find_element(
        By.NAME,
        "search_query"
    )

    search.send_keys(song)

    search.send_keys(Keys.RETURN)

    time.sleep(3)

    videos = driver.find_elements(
        By.ID,
        "video-title"
    )

    if videos:
        videos[0].click()

# ================= MAIN =================

running = False

def assistant_loop():

    global running

    speak("Say Hey Buddy")

    while running:

        query = take_command()

        if "hey buddy" in query:

            speak("Yes")

            while True:

                query = take_command()

                if "stop" in query:

                    speak("Sleeping")

                    break

                elif "change" in query:
                    train()

                elif run_memory(query):
                    continue

                elif "open app" in query:

                    name = query.replace(
                        "open app",
                        ""
                    ).strip()

                    open_app(name)

                elif "open folder" in query:

                    name = query.replace(
                        "open folder",
                        ""
                    ).strip()

                    open_folder(name)

                elif "take screenshot" in query:
                    take_screenshot()

                elif "increase brightness" in query:
                    increase_brightness()

                elif "decrease brightness" in query:
                    decrease_brightness()

                elif "schedule task" in query:
                    schedule_task()

                elif "play" in query:

                    song = query.replace(
                        "play",
                        ""
                    ).strip()

                    if song:
                        play_youtube(song)

                elif "search" in query:

                    text = query.replace(
                        "search",
                        ""
                    ).strip()

                    if text:

                        webbrowser.open(
                            f"https://www.google.com/search?q={text}"
                        )

                elif "open" in query:

                    name = query.replace(
                        "open",
                        ""
                    ).strip()

                    open_from_search(name)

                elif "time" in query:

                    speak(time.strftime("%H:%M"))

                elif "exit" in query:

                    speak("Bye")

                    os._exit(0)

# ================= GUI =================

def start():

    global running

    running = True

    threading.Thread(
        target=assistant_loop,
        daemon=True
    ).start()

def stop():

    global running

    running = False

    speak("Stopped")

root = tk.Tk()

root.title("Buddy AI ULTIMATE PRO")

root.attributes("-fullscreen", True)

root.bind(
    "<Escape>",
    lambda e: root.attributes(
        "-fullscreen",
        False
    )
)

root.configure(bg="black")

canvas = tk.Canvas(
    root,
    width=800,
    height=400,
    bg="black",
    highlightthickness=0
)

canvas.pack(pady=10)

chat_box = tk.Text(
    root,
    height=18,
    width=100,
    bg="black",
    fg="cyan",
    font=("Consolas", 12),
    state=tk.DISABLED
)

chat_box.pack(pady=10)

status_label = tk.Label(
    root,
    text="Ready",
    fg="cyan",
    bg="black",
    font=("Arial", 14)
)

status_label.pack()

button_frame = tk.Frame(root, bg="black")

button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Start",
    width=12,
    command=start
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text="Stop",
    width=12,
    command=stop
).pack(side=tk.LEFT, padx=10)

tk.Button(
    button_frame,
    text="Exit",
    width=12,
    command=root.destroy
).pack(side=tk.LEFT, padx=10)

root.mainloop()