import os
import shutil


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
        src_dir = os.path.join(os.getcwd(), 'src')
        shutil.copytree(src_dir, os.path.join(self.build_dir, 'src'))
