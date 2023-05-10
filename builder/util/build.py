import os
import shutil
import subprocess
import zipfile

import requests


class Build:
    """
    The Build class downloads and installs the necessary packages and
    then builds the source code
    """

    def __init__(self) -> None:
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.dist_dir = os.path.join(self.build_dir, '..', 'dist')

    def get_pyinstaller(self) -> None:
        """
        Downloads pyinstaller package
        """
        url = 'https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v5.1.zip'

        with requests.get(url, stream=True) as r:
            with open(os.path.join(self.build_dir, 'pyinstaller.zip'), 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        with zipfile.ZipFile(os.path.join(self.build_dir, 'pyinstaller.zip'), 'r') as zip_ref:
            zip_ref.extractall(self.build_dir)

        # install pyinstaller
        # cd build/pyinstaller-5.1 && pip install . -U
        subprocess.run([
            'pip',
            'install',
            '.',
            '-U'
        ], cwd=os.path.join(self.build_dir, 'pyinstaller-5.1'), shell=True, check=True)

    def get_upx(self) -> None:
        """
        Downloads UPX package
        """
        url = 'https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip'

        with requests.get(url, stream=True) as r:
            with open(os.path.join(self.build_dir, 'upx.zip'), 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        with zipfile.ZipFile(os.path.join(self.build_dir, 'upx.zip'), 'r') as zip_ref:
            zip_ref.extractall(self.build_dir)

    def build(self) -> None:
        """
        Builds the source code using pyinstaller and UPX
        """
        subprocess.run([
            'pyinstaller',
            '--onefile',
            '--noconsole',
            '--clean',
            '--distpath', f'{self.dist_dir}',
            '--workpath', f'{self.build_dir}/work',
            '--specpath', f'{self.build_dir}/spec',
            '--upx-dir', f'{self.build_dir}/upx-3.96-win64',
            f'{self.build_dir}/src/main.py'
        ], shell=True, check=True)
