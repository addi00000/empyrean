@echo off

@echo off

python --version 2>&1 | findstr " 3.11" >nul
if %errorlevel% == 0 (
    echo YOU HAVE PYTHON 3.11 INSTALLED. NOTE THIS CAN LEAD TO ERRORS. PLEASE INSTALL PYTHON VERSION 3.10.8
    timeout -T 5 >nul
    exit
)

py -3.10 -m pip uninstall -r interferences.txt
py -3.10 -m pip install --force-reinstall -r requirements.txt

cls

if exist build rmdir /s /q build
py -3.10 builder.py

pause
