@ECHO OFF
@MODE 101,50

ECHO INTALLING REQUIREMENTS && PY -3.10 -m pip install --upgrade -r requirements.txt
CLS && PY -3.10 builder.py
PAUSE && COLOR 07 && EXIT