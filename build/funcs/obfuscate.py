import base64
import zlib
import re
import os

def obfuscate(dir: str) -> None:
    def obfuscate_one(data: str) -> str:
        def shellcode(data: str) -> str:
            return '\\x' + '\\x'.join([hex(ord(c))[2:] for c in data])

        def sep_imports(data: str) -> list:
            lines = data.split('\n')
            imports = []
            for line in lines:
                if line.startswith('from ') or line.startswith('import '):
                    imports.append(line)
            return imports

        def extract_strings(data: str) -> list:
            regex = r'(?<!\\)"(.*?)(?<!\\)"' + '|' + r"(?<!\\)'(.*?)(?<!\\)'"
            return re.findall(regex, data)

        imports = '; '.join(sep_imports(data))

        import_alias = '__import__("builtins").__dict__["__import__"]'
        code = f'__import__("builtins").__dict__["exec"](__import__("base64").b64decode(__import__("zlib").decompress(__import__("base64").__dict__["b64decode"]("{base64.b64encode(zlib.compress(base64.b64encode(data.encode()))).decode()}"))).decode())'.replace('__import__', import_alias)
        code = re.sub(r'(?<!\\)"(.*?)(?<!\\)"', lambda m: f'"{shellcode(m.group(1))}"', code)

        out = f'{imports}\n{code}'

        return out

    paths = walk_dir(dir)

    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()

        data = obfuscate_one(data)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)

def walk_dir(path: str, ext: str = '.py') -> list:
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if file.endswith(ext):
                files.append(os.path.join(path, file))
        else:
            files += walk_dir(os.path.join(path, file), ext)
    return files  