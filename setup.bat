@echo off
pip install -r requirements.txt

(
echo @echo off
echo py main.py
) > Start.bat

echo Btw from now on you just gotta run the Start.bat
start Start.bat
pause