@echo off

WHERE git
if %ERRORLEVEL% NEQ 0 (
    echo --
    echo Please install Git:
    echo https://git-scm.com/downloads/win
    echo --
    pause
) 

if not exist anisette-v3-server\ (
    git clone https://github.com/Dadoum/anisette-v3-server
)

cd .\App
start winLaunch.vbs