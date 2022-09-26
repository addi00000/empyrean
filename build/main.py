import os
import shutil

from funcs.compile import *
from funcs.config import *
from funcs.constants import *
from funcs.obfuscate import *
from funcs.setup_env import *


def main() -> None:
    setup_env()
    config_parse()
    obfuscate(os.path.join(build_dir, 'src'))
    compile()

    shutil.rmtree(os.path.join(build_dir))


if __name__ == '__main__':
    main()
