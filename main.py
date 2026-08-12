import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_FILE = os.path.join(BASE_DIR, "games.json")

BG = "#171a21"
PANEL = "#20242c"
CARD = "#2a2f3a"
TEXT = "#ffffff"
MUTED = "#a9b0bb"
ACCENT = "#66c0f4"


class GameHub(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GameHub")
        self.geometry("1100x700")
        self.minsize(850, 550)
        self.configure(bg=BG)
        self.games = self.load_games()
        self.search_var = tk.StringVar()
        self.build_ui()
        self.show_home()

    def load_games(self):
        try:
            with open(GAMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

    def build_ui(self):
        top = tk.Frame(self, bg=PANEL, height=64)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="GAMEHUB", bg=PANEL, fg=TEXT,
                 font=("Helvetica", 22, "bold")).pack(side="left", padx=24)

        for name, command in [("HOME", self.show_home), ("LIBRARY", self.show_library)]:
            tk.Button(top, text=name, command=command, bg=PANEL, fg=MUTED,
                      activebackground=PANEL, activeforeground=TEXT,
                      bd=0, font=("Helvetica", 11, "bold")).pack(side="left", padx=12)

        search = tk.Entry(top, textvariable=self.search_var, width=28,
                          bg="#111318", fg=TEXT, insertbackground=TEXT,
                          relief="flat", font=("Helvetica", 11))
        search.pack(side="right", padx=24, ipady=7)
        search.bind("<KeyRelease>", lambda e: self.show_library())

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=25)

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def title(self, text):
        tk.Label(self.content, text=text, bg=BG, fg=TEXT,
                 font=("Helvetica", 28, "bold")).pack(anchor="w", pady=(0, 20))

    def show_home(self):
        self.clear()
        self.title("Welcome to GameHub")
        tk.Label(self.content, text="Your games. One place.", bg=BG, fg=MUTED,
                 font=("Helvetica", 14)).pack(anchor="w", pady=(0, 25))
        self.game_grid(self.games)

    def show_library(self):
        self.clear()
        self.title("Library")
        query = self.search_var.get().lower().strip()
        games = [g for g in self.games if query in g.get("name", "").lower()] if query else self.games
        self.game_grid(games)

    def game_grid(self, games):
        grid = tk.Frame(self.content, bg=BG)
        grid.pack(fill="both", expand=True, anchor="nw")
        for i, game in enumerate(games):
            card = tk.Frame(grid, bg=CARD, width=240, height=210)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            tk.Label(card, text="🎮", bg=CARD, fg=TEXT,
                     font=("Helvetica", 42)).pack(pady=(22, 5))
            tk.Label(card, text=game.get("name", "Game"), bg=CARD, fg=TEXT,
                     font=("Helvetica", 16, "bold")).pack()
            tk.Label(card, text=game.get("description", ""), bg=CARD, fg=MUTED,
                     wraplength=205, font=("Helvetica", 10)).pack(pady=6)
            tk.Button(card, text="PLAY", command=lambda g=game: self.launch_game(g),
                      bg=ACCENT, fg="#101820", activebackground="#8bd4ff",
                      bd=0, padx=18, pady=6, font=("Helvetica", 10, "bold")).pack(pady=7)

        for c in range(3):
            grid.columnconfigure(c, weight=1)

        if not games:
            tk.Label(grid, text="No games found.", bg=BG, fg=MUTED,
                     font=("Helvetica", 14)).grid(row=0, column=0, pady=40)

    def launch_game(self, game):
        path = os.path.join(BASE_DIR, game.get("file", ""))
        if not os.path.isfile(path):
            messagebox.showerror("GameHub", f"Game file not found:\n{path}")
            return
        try:
            subprocess.Popen([sys.executable, path], cwd=BASE_DIR)
        except OSError as exc:
            messagebox.showerror("GameHub", str(exc))


if __name__ == "__main__":
    GameHub().mainloop()
