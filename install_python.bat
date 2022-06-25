@ECHO OFF

ECHO DOWNLOADING PYTHON INSTALLER && curl -L -O https://www.python.org/ftp/python/3.10.5/python-3.10.5-amd64.exe
ECHO RUNNING INSTALLER && python-3.10.5-amd64.exe /quiet PrependPath=1 Include_test=0
ECHO REMOVING INSTALLER EXECUTABLE && del python-3.10.5-amd64.exe
COLOR 02 && ECHO DONE && ECHO PYTHON (3.10.5) INSTALLED && START .
PAUSE && COLOR 07 && EXIT