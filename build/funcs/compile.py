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
        subprocess.run(['pyinstaller', '--onefile', '--noconsole', '--key', 'EMPRYREAN', '--upx-dir', os.path.join(self.build_dir, 'upx'), '--distpath', self.dist_dir, '--workpath', os.path.join(self.build_dir, 'build'), '--specpath', os.path.join(self.build_dir, 'spec'), os.path.join(self.build_dir, 'src', 'main.py')])

    def cleanup(self) -> None:
        shutil.rmtree(os.path.join(self.build_dir))
