import os
import shutil
import subprocess

import requests

from .constants import build_dir, dist_dir


class compile:
    def __init__(self) -> None:
        self.build_dir = build_dir
        self.dist_dir = dist_dir

        self.compile()

    def compile(self) -> None:
        # Remove --standalone to lower file size, may cause issues
        # also might need to add some more flags
        # fucking install the C caching shit
        subprocess.run(['py', '-m', 'nuitka', '--standalone', '--onefile', '--remove-output', '--windows-disable-console', 'main.py'])

    def cleanup(self) -> None:
        shutil.rmtree(os.path.join(self.build_dir))
