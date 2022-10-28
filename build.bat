@echo off

py -3.10 -m pip uninstall -r interferences.txt
py -3.10 -m pip install --force-reinstall -r requirements.txt

cls
cd builder

if exist build rmdir /s /q build
py -3.10 main.py

pause