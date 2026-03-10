"""
Build the launcher into a standalone .exe (no command window needed).
Run this file from Thonny: Open build.py, then Run (F5).

Requires: pip install pyinstaller
"""
import os
import subprocess
import sys

LAUNCHER_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    os.chdir(LAUNCHER_DIR)
    print("Installing PyInstaller if needed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"], check=False)
    print("Building launcher...")
    r = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--noconsole", "--onefile", "--name", "GameLauncher",
        "main.py"
    ])
    if r.returncode != 0:
        print("Build failed.")
        return
    dist = os.path.join(LAUNCHER_DIR, "dist")
    data_dest = os.path.join(dist, "data")
    os.makedirs(data_dest, exist_ok=True)
    for name in ["games.json", "settings.json"]:
        src = os.path.join(LAUNCHER_DIR, "data", name)
        if os.path.isfile(src):
            with open(src, "r", encoding="utf-8") as f:
                content = f.read()
            with open(os.path.join(data_dest, name), "w", encoding="utf-8") as f:
                f.write(content)
    games_src = os.path.join(LAUNCHER_DIR, "games")
    games_dest = os.path.join(dist, "games")
    if os.path.isdir(games_src):
        import shutil
        if os.path.isdir(games_dest):
            shutil.rmtree(games_dest)
        shutil.copytree(games_src, games_dest)
    exe = os.path.join(dist, "GameLauncher.exe")
    if os.path.isfile(exe):
        print("Done! Run: dist\\GameLauncher.exe")
        print("Keep the dist folder (exe + data + games) together.")
    else:
        print("Build failed. Check errors above.")

if __name__ == "__main__":
    main()
