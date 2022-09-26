import os
import shutil
import requests
import subprocess

from .constants import build_dir, src_dir

class setup_env:
    def __init__(self) -> None:
        self.build_dir = build_dir
        self.src_dir = src_dir

        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

        self.create_build_dir()

        self.copy_src()
        self.install_pyinstaller()
        self.install_upx()

    def create_build_dir(self) -> None:
        if not os.path.exists(self.build_dir):
            os.mkdir(self.build_dir)

    def copy_src(self) -> None:
        shutil.copytree(self.src_dir, self.build_dir + os.sep + 'src')

    def install_pyinstaller(self) -> None:
        url = 'https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v5.1.zip'

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(os.path.join(self.build_dir, 'pyinstaller.zip'), 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        shutil.unpack_archive(os.path.join(self.build_dir, 'pyinstaller.zip'), self.build_dir)
        os.rename(os.path.join(self.build_dir, 'pyinstaller-5.1'), os.path.join(self.build_dir, 'pyinstaller'))
        os.remove(os.path.join(self.build_dir, 'pyinstaller.zip'))

        subprocess.run(['pip', 'uninstall', '-y', 'pyinstaller'], cwd=self.build_dir)
        subprocess.run(['py', '-3.10', './waf', 'all', '--target-arch=64bit'], cwd=os.path.join(self.build_dir, 'pyinstaller', 'bootloader'))
        subprocess.run(['py', '-3.10', 'setup.py', 'install'], cwd=os.path.join(self.build_dir, 'pyinstaller'))

    def install_upx(self) -> None:
        url = 'https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip'

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(os.path.join(self.build_dir, 'upx.zip'), 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        shutil.unpack_archive(os.path.join(self.build_dir, 'upx.zip'), self.build_dir)
        os.rename(os.path.join(self.build_dir, 'upx-3.96-win64'), os.path.join(self.build_dir, 'upx'))
        os.remove(os.path.join(self.build_dir, 'upx.zip'))