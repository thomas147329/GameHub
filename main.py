import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from urllib.request import urlopen, Request
import ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALLED_DIR = os.path.join(BASE_DIR, "installed_games")
CATALOG_URL = "https://raw.githubusercontent.com/thomas147329/GameHubfiles/main/games.json"
GAMES_BASE_URL = "https://raw.githubusercontent.com/thomas147329/GameHubfiles/main/"
GITHUB_API_BASE = "https://api.github.com/repos/thomas147329/GameHubfiles/contents/"

BG = "#171a21"
PANEL = "#20242c"
CARD = "#2a2f3a"
TEXT = "#ffffff"
MUTED = "#a9b0bb"
ACCENT = "#66c0f4"
DANGER = "#e85d5d"


def make_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


SSL_CONTEXT = make_ssl_context()


def download_bytes(url, timeout=30):
    request = Request(url, headers={"User-Agent": "GameHub/1.1"})

    try:
        with urlopen(request, timeout=timeout, context=SSL_CONTEXT) as response:
            return response.read()
    except Exception as python_error:
        try:
            result = subprocess.run(
                [
                    "curl", "--fail", "--silent", "--show-error", "--location",
                    "--max-time", str(timeout), "--user-agent", "GameHub/1.1", url
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return result.stdout
        except Exception as curl_error:
            raise RuntimeError(
                "Could not connect to GameHubfiles.\n\n"
                "Python HTTPS error:\n" + str(python_error) +
                "\n\nSystem curl error:\n" + str(curl_error)
            )


def github_directory_files(repo_path):
    """Return every file under a GameHubfiles directory recursively."""
    api_url = GITHUB_API_BASE + repo_path.strip("/")
    data = json.loads(download_bytes(api_url, timeout=30).decode("utf-8"))

    if not isinstance(data, list):
        raise RuntimeError("GitHub did not return a directory listing for " + repo_path)

    files = []
    for item in data:
        item_type = item.get("type")
        item_path = item.get("path", "")
        if item_type == "file":
            files.append(item_path)
        elif item_type == "dir":
            files.extend(github_directory_files(item_path))
    return files


class GameHub(tk.Tk):
    def __init__(self):
        super().__init__()
        super().title("GameHub")
        self.geometry("1100x700")
        self.minsize(850, 550)
        self.configure(bg=BG)

        os.makedirs(INSTALLED_DIR, exist_ok=True)
        self.search_var = tk.StringVar()
        self.games = []

        self.build_ui()
        self.load_catalog(show_errors=True)
        self.show_home()

    def load_catalog(self, show_errors=False):
        try:
            data = download_bytes(CATALOG_URL, timeout=15)
            catalog = json.loads(data.decode("utf-8"))
            if not isinstance(catalog, list):
                raise ValueError("The online game catalog must be a JSON list.")
            self.games = catalog
            return True
        except Exception as exc:
            self.games = []
            if show_errors:
                messagebox.showerror(
                    "GameHub",
                    "Could not download the game catalog.\n\n" + str(exc)
                )
            return False

    def build_ui(self):
        top = tk.Frame(self, bg=PANEL, height=64)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="GAMEHUB", bg=PANEL, fg=TEXT,
                 font=("Helvetica", 22, "bold")).pack(side="left", padx=24)

        tk.Button(top, text="HOME", command=self.show_home, bg=PANEL, fg=MUTED,
                  activebackground=PANEL, activeforeground=TEXT, bd=0,
                  font=("Helvetica", 11, "bold")).pack(side="left", padx=12)

        tk.Button(top, text="LIBRARY", command=self.show_library, bg=PANEL, fg=MUTED,
                  activebackground=PANEL, activeforeground=TEXT, bd=0,
                  font=("Helvetica", 11, "bold")).pack(side="left", padx=12)

        tk.Button(top, text="REFRESH", command=self.refresh_catalog, bg=PANEL, fg=MUTED,
                  activebackground=PANEL, activeforeground=TEXT, bd=0,
                  font=("Helvetica", 11, "bold")).pack(side="left", padx=12)

        search = tk.Entry(top, textvariable=self.search_var, width=28,
                          bg="#111318", fg=TEXT, insertbackground=TEXT,
                          relief="flat", font=("Helvetica", 11))
        search.pack(side="right", padx=24, ipady=7)
        search.bind("<KeyRelease>", lambda event: self.show_library())

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=25)

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_title(self, text):
        tk.Label(self.content, text=text, bg=BG, fg=TEXT,
                 font=("Helvetica", 28, "bold")).pack(anchor="w", pady=(0, 20))

    def refresh_catalog(self):
        self.load_catalog(show_errors=True)
        self.show_home()

    def show_home(self):
        self.clear()
        self.page_title("Welcome to GameHub")
        tk.Label(self.content, text="Games are downloaded from GameHubfiles.",
                 bg=BG, fg=MUTED, font=("Helvetica", 14)).pack(anchor="w", pady=(0, 25))
        self.game_grid(self.games)

    def show_library(self):
        self.clear()
        self.page_title("Library")
        query = self.search_var.get().lower().strip()
        games = [game for game in self.games if query in game.get("name", "").lower()] if query else self.games
        self.game_grid(games)

    def game_grid(self, games):
        grid = tk.Frame(self.content, bg=BG)
        grid.pack(fill="both", expand=True, anchor="nw")

        for i, game in enumerate(games):
            card = tk.Frame(grid, bg=CARD, width=240, height=235)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)

            tk.Label(card, text="🎮", bg=CARD, fg=TEXT,
                     font=("Helvetica", 42)).pack(pady=(18, 5))
            tk.Label(card, text=game.get("name", "Game"), bg=CARD, fg=TEXT,
                     font=("Helvetica", 16, "bold")).pack()
            tk.Label(card, text=game.get("description", ""), bg=CARD, fg=MUTED,
                     wraplength=205, font=("Helvetica", 10)).pack(pady=5)

            installed = os.path.isfile(self.local_path(game))

            if installed:
                button_frame = tk.Frame(card, bg=CARD)
                button_frame.pack(pady=7)

                tk.Button(
                    button_frame, text="PLAY", command=lambda g=game: self.launch_game(g),
                    bg=ACCENT, fg="#101820", activebackground="#8bd4ff", bd=0,
                    padx=16, pady=6, font=("Helvetica", 10, "bold")
                ).pack(side="left", padx=3)

                tk.Button(
                    button_frame, text="UNINSTALL", command=lambda g=game: self.uninstall_game(g),
                    bg=DANGER, fg=TEXT, activebackground="#ff7777", bd=0,
                    padx=10, pady=6, font=("Helvetica", 10, "bold")
                ).pack(side="left", padx=3)
            else:
                tk.Button(
                    card, text="DOWNLOAD", command=lambda g=game: self.launch_game(g),
                    bg=ACCENT, fg="#101820", activebackground="#8bd4ff", bd=0,
                    padx=18, pady=6, font=("Helvetica", 10, "bold")
                ).pack(pady=7)

        for column in range(3):
            grid.columnconfigure(column, weight=1)

        if not games:
            tk.Label(grid, text="No games found.", bg=BG, fg=MUTED,
                     font=("Helvetica", 14)).grid(row=0, column=0, pady=40)

    def local_path(self, game):
        filename = os.path.basename(game.get("file", "game.py"))
        return os.path.join(INSTALLED_DIR, filename)

    def download_game(self, game):
        remote_file = game.get("file", "")
        if not remote_file:
            raise ValueError("Game has no download file configured.")

        # Download the main Python file.
        url = GAMES_BASE_URL + remote_file
        path = self.local_path(game)
        data = download_bytes(url, timeout=30)
        with open(path, "wb") as file:
            file.write(data)

        # Optional asset folders are listed in games.json as repo-relative paths.
        # Example: "asset_dirs": ["games/Assets"] downloads the whole Assets tree
        # into installed_games/Assets, preserving Models/SFX/Textures subfolders.
        for asset_dir in game.get("asset_dirs", []):
            asset_dir = asset_dir.strip("/")
            if not asset_dir:
                continue

            repo_files = github_directory_files(asset_dir)
            prefix = asset_dir.rsplit("/", 1)[0] + "/" if "/" in asset_dir else ""
            target_root = os.path.join(INSTALLED_DIR, os.path.basename(asset_dir))

            for repo_file in repo_files:
                if prefix and not repo_file.startswith(prefix):
                    relative = os.path.basename(repo_file)
                else:
                    relative = repo_file[len(asset_dir):].lstrip("/")

                target = os.path.join(target_root, relative)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                asset_url = GAMES_BASE_URL + repo_file
                asset_data = download_bytes(asset_url, timeout=60)
                with open(target, "wb") as file:
                    file.write(asset_data)

        return path

    def launch_game(self, game):
        path = self.local_path(game)

        try:
            if not os.path.isfile(path):
                path = self.download_game(game)
                messagebox.showinfo(
                    "GameHub",
                    "Downloaded " + game.get("name", "game") + "!"
                )

            subprocess.Popen([sys.executable, path], cwd=INSTALLED_DIR)
            self.show_home()

        except Exception as exc:
            messagebox.showerror(
                "GameHub",
                "Could not download or start the game.\n\n" + str(exc)
            )

    def uninstall_game(self, game):
        path = self.local_path(game)
        name = game.get("name", "this game")

        if not os.path.isfile(path):
            self.show_home()
            return

        confirmed = messagebox.askyesno(
            "Uninstall Game",
            "Are you sure you want to uninstall " + name + "?\n\n"
            "This will remove the downloaded game from your computer."
        )

        if not confirmed:
            return

        try:
            os.remove(path)

            # Remove asset folders belonging to this game.
            for asset_dir in game.get("asset_dirs", []):
                asset_name = os.path.basename(asset_dir.strip("/"))
                asset_path = os.path.join(INSTALLED_DIR, asset_name)
                if os.path.isdir(asset_path):
                    shutil.rmtree(asset_path)

            messagebox.showinfo("GameHub", name + " has been uninstalled.")
            self.show_home()
        except Exception as exc:
            messagebox.showerror(
                "GameHub",
                "Could not uninstall the game.\n\n" + str(exc)
            )


if __name__ == "__main__":
    GameHub().mainloop()
