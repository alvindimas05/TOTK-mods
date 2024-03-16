import platform
import subprocess
import os
from configuration.settings import *
latest_version = Version.strip("manager-")


if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "pyinstaller",
            "run.py",
            "--onefile",
            f"--name=TOTK Optimizer {latest_version}",
            "--add-data", "GUI;GUI",
            "--add-data", "json.data;json.data",
            "--icon", "GUI/LOGO.ico"
        ]
        subprocess.run(command, shell=True)
        
    if platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onefile",
            f"--name=TOTK Optimizer {latest_version}.AppImage",
            "run.py",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data"
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap"
        ]
        appimage_path = "dist/TOTK Optimizer {latest_version}.AppImage"
        os.chmod(appimage_path, 0o644)
        subprocess.run(command, check=True)
