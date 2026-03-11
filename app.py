import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

ROOT = Path(__file__).resolve().parent
GAMES_DIR = ROOT / "games"
CUSTOM_GAMES_DIR = ROOT / "custom_games"
MANIFEST_PATH = ROOT / "games_manifest.json"
SETTINGS_PATH = ROOT / "settings.json"

DEFAULT_SETTINGS = {
    "developer_pin": "2580",
    "fullscreen": True,
}


class GameLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Game Launcher")

        self.settings = self._load_json(SETTINGS_PATH, DEFAULT_SETTINGS)
        self.manifest = self._load_json(MANIFEST_PATH, {"display_names": {}})

        GAMES_DIR.mkdir(exist_ok=True)
        CUSTOM_GAMES_DIR.mkdir(exist_ok=True)

        self.developer_mode = False
        self.games = []

        self._configure_screen_fit()
        self._build_ui()
        self.refresh_games()

    def _configure_screen_fit(self):
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        if self.settings.get("fullscreen", True):
            self.attributes("-fullscreen", True)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = tk.Frame(self, padx=12, pady=12)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        tk.Label(top, text="Games", font=("Arial", 18, "bold")).grid(row=0, column=0, sticky="w")

        self.dev_button = tk.Button(top, text="Enter Developer Mode", command=self.toggle_developer_mode)
        self.dev_button.grid(row=0, column=2, sticky="e")

        mid = tk.Frame(self, padx=12, pady=12)
        mid.grid(row=1, column=0, sticky="nsew")
        mid.columnconfigure(0, weight=1)
        mid.rowconfigure(0, weight=1)

        self.games_list = tk.Listbox(mid, font=("Arial", 14))
        self.games_list.grid(row=0, column=0, sticky="nsew")

        controls = tk.Frame(self, padx=12, pady=12)
        controls.grid(row=2, column=0, sticky="ew")

        tk.Button(controls, text="Play", command=self.play_selected, width=16).pack(side="left", padx=6)
        tk.Button(controls, text="Refresh", command=self.refresh_games, width=16).pack(side="left", padx=6)
        tk.Button(controls, text="Toggle Fullscreen", command=self.toggle_fullscreen, width=16).pack(side="left", padx=6)
        tk.Button(controls, text="Exit", command=self.destroy, width=16).pack(side="right", padx=6)

        self.dev_controls = tk.Frame(self, padx=12, pady=12)
        self.dev_controls.grid(row=3, column=0, sticky="ew")

        self.add_game_btn = tk.Button(
            self.dev_controls,
            text="Add Game Files",
            command=self.add_game_files,
            width=20,
        )
        self.open_folder_btn = tk.Button(
            self.dev_controls,
            text="Open Custom Games Folder",
            command=self.open_custom_games_folder,
            width=24,
        )
        self.rename_btn = tk.Button(
            self.dev_controls,
            text="Rename Selected Game",
            command=self.rename_selected_game,
            width=20,
        )

    def refresh_games(self):
        self.games = self._discover_games()
        self.games_list.delete(0, tk.END)
        for item in self.games:
            self.games_list.insert(tk.END, item["display_name"])

    def play_selected(self):
        index = self.games_list.curselection()
        if not index:
            messagebox.showinfo("No game selected", "Select a game first.")
            return
        game = self.games[index[0]]
        subprocess.Popen([sys.executable, str(game["path"])], cwd=str(ROOT))

    def toggle_developer_mode(self):
        if self.developer_mode:
            self.developer_mode = False
            self.dev_button.configure(text="Enter Developer Mode")
            self.add_game_btn.pack_forget()
            self.open_folder_btn.pack_forget()
            self.rename_btn.pack_forget()
            return

        pin = simpledialog.askstring(
            "Developer PIN",
            "Enter developer PIN:",
            show="*",
            parent=self,
        )

        if pin is None:
            return

        if pin != self.settings.get("developer_pin", DEFAULT_SETTINGS["developer_pin"]):
            messagebox.showerror("Incorrect PIN", "The PIN you entered is incorrect.")
            return

        self.developer_mode = True
        self.dev_button.configure(text="Exit Developer Mode")
        self.add_game_btn.pack(side="left", padx=6)
        self.open_folder_btn.pack(side="left", padx=6)
        self.rename_btn.pack(side="left", padx=6)

    def add_game_files(self):
        selected_files = filedialog.askopenfilenames(
            title="Select Python game files",
            filetypes=[("Python files", "*.py")],
            parent=self,
        )
        if not selected_files:
            return

        copied = 0
        for source in selected_files:
            src_path = Path(source)
            destination = CUSTOM_GAMES_DIR / src_path.name
            if destination.exists():
                if not messagebox.askyesno(
                    "Replace existing game?",
                    f"{src_path.name} already exists. Replace it?",
                    parent=self,
                ):
                    continue
            shutil.copy2(src_path, destination)
            copied += 1

        self.refresh_games()
        messagebox.showinfo("Games Added", f"Added {copied} game file(s).", parent=self)

    def open_custom_games_folder(self):
        folder = str(CUSTOM_GAMES_DIR)
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def rename_selected_game(self):
        index = self.games_list.curselection()
        if not index:
            messagebox.showinfo("No game selected", "Select a game to rename.")
            return

        game = self.games[index[0]]
        new_name = simpledialog.askstring("Rename Game", "New display name:", parent=self)
        if not new_name:
            return

        self.manifest.setdefault("display_names", {})[game["key"]] = new_name.strip()
        self._save_json(MANIFEST_PATH, self.manifest)
        self.refresh_games()

    def toggle_fullscreen(self):
        current = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not current)
        self.settings["fullscreen"] = not current
        self._save_json(SETTINGS_PATH, self.settings)

    def _discover_games(self):
        entries = []
        for folder in (GAMES_DIR, CUSTOM_GAMES_DIR):
            for path in sorted(folder.glob("*.py")):
                key = str(path.relative_to(ROOT))
                display_name = self.manifest.get("display_names", {}).get(key, path.stem)
                entries.append({"key": key, "path": path, "display_name": display_name})
        return entries

    @staticmethod
    def _load_json(path: Path, fallback):
        if not path.exists():
            return json.loads(json.dumps(fallback))
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return json.loads(json.dumps(fallback))

    @staticmethod
    def _save_json(path: Path, data):
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


if __name__ == "__main__":
    GameLauncher().mainloop()
