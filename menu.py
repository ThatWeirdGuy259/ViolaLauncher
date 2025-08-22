import tkinter as tk
from tkinter import ttk
import sys

def launch_game():
    print("Launching game...")

def open_settings():
    print("Opening settings...")

def exit_app():
    sys.exit()

# App window
root = tk.Tk()
root.title("Viola Launcher")
root.geometry("420x320")
root.configure(bg="#2a003f")  # deep purple background

# Title
title = tk.Label(
    root,
    text="Viola Launcher",
    font=("Segoe UI", 20, "bold"),
    bg="#2a003f",
    fg="white"
)
title.pack(pady=20)

# Custom style for purple buttons
style = ttk.Style()
style.configure(
    "Purple.TButton",
    font=("Segoe UI", 12, "bold"),
    padding=10,
    background="#6a0dad",
    foreground="white"
)

def make_button(text, cmd):
    btn = tk.Button(
        root,
        text=text,
        command=cmd,
        font=("Segoe UI", 12, "bold"),
        fg="white",
        bg="#8a2be2",
        activebackground="#9932cc",
        activeforeground="white",
        relief="flat",
        bd=0,
        width=18,
        height=2
    )
    btn.pack(pady=10)
    btn.config(highlightthickness=0)
    btn.configure(cursor="hand2")
    return btn

# Buttons
make_button("Launch Game", launch_game)
make_button("Settings", open_settings)
make_button("Exit", exit_app)

root.mainloop()
