cd /D "%~dp0"
pyinstaller --onefile avec_console.py --version-file=version.txt
pause