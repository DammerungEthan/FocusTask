#!/usr/bin/env python3
"""Focus Tasks — simple, persistent per-task timers for Linux."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

APP_NAME = "Focus Tasks"
APP_DIR = Path(__file__).resolve().parent
LEGACY_DATA_FILE = APP_DIR / "data" / "tasks.json"
if sys.platform == "win32":
    USER_DATA_HOME = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
elif sys.platform == "darwin":
    USER_DATA_HOME = Path.home() / "Library" / "Application Support"
else:
    USER_DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
DATA_FILE = USER_DATA_HOME / "focus-tasks" / "tasks.json"
BG = "#111318"
PANEL = "#191c23"
PANEL2 = "#20242d"
BORDER = "#2a2f3a"
TEXT = "#f1f3f8"
MUTED = "#9299a8"
ACCENT = "#9b8cff"
GREEN = "#55d6a0"
RED = "#ff7485"


def load_tasks():
    # Migrate tasks created by the earlier in-folder version on first launch.
    source = DATA_FILE if DATA_FILE.exists() else LEGACY_DATA_FILE
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return [task for task in raw if isinstance(task, dict) and "id" in task]
    except (OSError, json.JSONDecodeError):
        pass
    return []


class FocusTasks(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("650x720")
        self.minsize(480, 500)
        self.configure(bg=BG)
        self.tasks = load_tasks()
        self.row_widgets = {}
        if LEGACY_DATA_FILE.exists() and not DATA_FILE.exists():
            self.save()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._build()
        self.render()
        self.tick()

    def _build(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=28, pady=(25, 20))
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 22))
        tk.Label(header, text="FOCUS TASKS", bg=BG, fg=ACCENT,
                 font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Un paso a la vez.", bg=BG, fg=TEXT,
                 font=("TkDefaultFont", 23, "bold")).pack(anchor="w", pady=(5, 2))
        tk.Label(header, text="Cada tarea lleva su propio temporizador.", bg=BG, fg=MUTED,
                 font=("TkDefaultFont", 10)).pack(anchor="w")

        form = tk.Frame(outer, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x", pady=(0, 18))
        inner = tk.Frame(form, bg=PANEL)
        inner.pack(fill="x", padx=14, pady=13)
        self.name_entry = tk.Entry(inner, bg=PANEL2, fg=TEXT, insertbackground=TEXT,
                                   relief="flat", font=("TkDefaultFont", 11),
                                   highlightthickness=1, highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self.name_entry.insert(0, "¿Qué necesitas hacer?")
        self.name_entry.bind("<FocusIn>", self._clear_placeholder)
        self.name_entry.bind("<Return>", lambda _e: self.add_task())
        self.name_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.minutes_entry = tk.Entry(inner, width=7, bg=PANEL2, fg=TEXT, insertbackground=TEXT,
                                      relief="flat", justify="center", font=("TkDefaultFont", 11),
                                      highlightthickness=1, highlightbackground=BORDER,
                                      highlightcolor=ACCENT)
        self.minutes_entry.insert(0, "25")
        self.minutes_entry.pack(side="left", ipady=10, padx=(0, 8))
        tk.Label(inner, text="min", bg=PANEL, fg=MUTED, font=("TkDefaultFont", 9)).pack(side="left", padx=(0, 10))
        self._button(inner, "＋  Añadir", self.add_task, ACCENT, BG).pack(side="left", ipady=8, ipadx=11)

        top = tk.Frame(outer, bg=BG)
        top.pack(fill="x", pady=(2, 9))
        tk.Label(top, text="TUS TAREAS", bg=BG, fg=MUTED,
                 font=("TkDefaultFont", 9, "bold")).pack(side="left")
        self.count_label = tk.Label(top, text="", bg=BG, fg=MUTED, font=("TkDefaultFont", 9))
        self.count_label.pack(side="right")
        self.list_frame = tk.Frame(outer, bg=BG)
        self.list_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.list_frame, bg=BG, highlightthickness=0, bd=0)
        self.scroll = tk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")
        self.rows = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))
        tk.Label(outer, text="Guardado automático en tu equipo", bg=BG, fg="#6f7684",
                 font=("TkDefaultFont", 9)).pack(anchor="w", pady=(12, 0))

    def _clear_placeholder(self, _event):
        if self.name_entry.get() == "¿Qué necesitas hacer?":
            self.name_entry.delete(0, "end")

    def _button(self, parent, text, command, bg=PANEL2, fg=TEXT):
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg, relief="flat",
                         bd=0, cursor="hand2", font=("TkDefaultFont", 9, "bold"), padx=9)

    def save(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(DATA_FILE)

    def add_task(self):
        name = self.name_entry.get().strip()
        if name == "¿Qué necesitas hacer?":
            name = ""
        if not name:
            self.name_entry.focus_set()
            return
        try:
            minutes = int(self.minutes_entry.get())
            if not 1 <= minutes <= 10080:
                raise ValueError
        except ValueError:
            messagebox.showerror("Tiempo no válido", "Escribe minutos entre 1 y 10080.", parent=self)
            self.minutes_entry.focus_set()
            return
        self.tasks.insert(0, {"id": uuid.uuid4().hex, "name": name, "duration": minutes * 60,
                              "remaining": minutes * 60, "running": False, "deadline": None,
                              "done": False})
        self.name_entry.delete(0, "end")
        self.minutes_entry.delete(0, "end")
        self.minutes_entry.insert(0, "25")
        self.save()
        self.render()
        self.name_entry.focus_set()

    def remaining(self, task, now=None):
        if task.get("running") and task.get("deadline"):
            return max(0, int(task["deadline"] - (now or time.time()) + 0.999))
        return max(0, int(task.get("remaining", task.get("duration", 0))))

    @staticmethod
    def fmt(seconds):
        return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}" if seconds >= 3600 else f"{seconds // 60:02d}:{seconds % 60:02d}"

    def render(self):
        for child in self.rows.winfo_children():
            child.destroy()
        self.row_widgets.clear()
        active = sum(not t.get("done") for t in self.tasks)
        complete = len(self.tasks) - active
        self.count_label.config(text=f"{active} pendiente{'s' if active != 1 else ''}  ·  {complete} completada{'s' if complete != 1 else ''}")
        if not self.tasks:
            empty = tk.Frame(self.rows, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            empty.pack(fill="x", pady=3)
            tk.Label(empty, text="Todavía no hay tareas", bg=PANEL, fg=TEXT,
                     font=("TkDefaultFont", 12, "bold")).pack(pady=(24, 5))
            tk.Label(empty, text="Añade una arriba y empieza cuando quieras.", bg=PANEL, fg=MUTED,
                     font=("TkDefaultFont", 9)).pack(pady=(0, 24))
            return
        for task in self.tasks:
            card = tk.Frame(self.rows, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
            card.pack(fill="x", pady=4)
            content = tk.Frame(card, bg=PANEL)
            content.pack(fill="x", padx=13, pady=11)
            done_var = tk.BooleanVar(value=bool(task.get("done")))
            cb = tk.Checkbutton(content, variable=done_var, command=lambda t=task, v=done_var: self.toggle_done(t, v),
                                bg=PANEL, activebackground=PANEL, selectcolor=PANEL2,
                                fg=GREEN, activeforeground=GREEN, cursor="hand2", bd=0)
            cb.pack(side="left", padx=(0, 8))
            label = tk.Label(content, text=task["name"], bg=PANEL,
                             fg=MUTED if task.get("done") else TEXT,
                             font=("TkDefaultFont", 11, "overstrike" if task.get("done") else "normal"),
                             anchor="w")
            label.pack(side="left", fill="x", expand=True)
            time_label = tk.Label(content, text=self.fmt(self.remaining(task)), bg=PANEL,
                                  fg=GREEN if task.get("running") else MUTED,
                                  font=("TkFixedFont", 15, "bold"))
            time_label.pack(side="left", padx=(8, 12))
            controls = tk.Frame(content, bg=PANEL)
            controls.pack(side="left")
            if not task.get("done"):
                is_running = bool(task.get("running"))
                self._button(controls, "Pausa" if is_running else "Iniciar",
                             lambda t=task: self.toggle_timer(t), ACCENT if not is_running else PANEL2,
                             BG if not is_running else TEXT).pack(side="left", padx=2, ipady=6)
                self._button(controls, "↺", lambda t=task: self.reset_timer(t), PANEL2, MUTED).pack(side="left", padx=2, ipady=6)
            self._button(controls, "×", lambda t=task: self.delete_task(t), PANEL2, RED).pack(side="left", padx=(2, 0), ipady=6)
            self.row_widgets[task["id"]] = (time_label, card)

    def toggle_timer(self, task):
        if task.get("running"):
            task["remaining"] = self.remaining(task)
            task["running"] = False
            task["deadline"] = None
        else:
            if self.remaining(task) <= 0:
                task["remaining"] = task.get("duration", 0)
            task["running"] = True
            task["deadline"] = time.time() + self.remaining(task)
        self.save()
        self.render()

    def reset_timer(self, task):
        task["running"] = False
        task["deadline"] = None
        task["remaining"] = task.get("duration", 0)
        self.save()
        self.render()

    def toggle_done(self, task, variable):
        task["done"] = variable.get()
        task["running"] = False
        task["deadline"] = None
        self.save()
        self.render()

    def delete_task(self, task):
        self.tasks = [item for item in self.tasks if item["id"] != task["id"]]
        self.save()
        self.render()

    def tick(self):
        now = time.time()
        changed = False
        for task in self.tasks:
            if task.get("running") and self.remaining(task, now) <= 0:
                task["running"] = False
                task["deadline"] = None
                task["remaining"] = 0
                task["_just_expired"] = True
                changed = True
            entry = self.row_widgets.get(task["id"])
            if entry:
                entry[0].config(text=self.fmt(self.remaining(task, now)),
                                fg=GREEN if task.get("running") else MUTED)
        if changed:
            self.save()
            self.render()
            self.alert_expired([task["name"] for task in self.tasks
                                if not task.get("running") and task.get("remaining") == 0
                                and task.pop("_just_expired", False)])
        self.after(250, self.tick)

    def alert_expired(self, task_names):
        if not task_names:
            return
        # Try a system sound when available; the visible dialog is the reliable fallback.
        sound = Path("/usr/share/sounds/freedesktop/stereo/complete.oga")
        player = shutil.which("paplay")
        if player and sound.is_file():
            try:
                subprocess.Popen([player, str(sound)], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
            except OSError:
                pass
        else:
            self.bell()
        self.lift()
        self.attributes("-topmost", True)
        self.after(1500, lambda: self.attributes("-topmost", False))
        names = "\n".join(f"• {name}" for name in task_names)
        messagebox.showinfo("Temporizador terminado", f"Se acabó el tiempo para:\n\n{names}", parent=self)

    def close(self):
        now = time.time()
        for task in self.tasks:
            if task.get("running"):
                task["remaining"] = self.remaining(task, now)
        self.save()
        self.destroy()


if __name__ == "__main__":
    FocusTasks().mainloop()
