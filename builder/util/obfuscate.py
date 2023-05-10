import ast
import os

import pyobf2.lib as obf


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
            "encodeStrings.enabled": True,
            "encodeStrings.mode": "xortable",
            "floatsToComplex.enabled": True,
            "intObfuscator.enabled": True,
            "intObfuscator.mode": "decode",
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
