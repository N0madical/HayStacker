@echo off
setlocal enabledelayedexpansion

echo Welcome to HayStacker^^!

@REM ### Check if WSL is installed. It is needed to run linux commands on windows. Install it if not
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    call:wslNotInstalled
) 

wsl -l -q | findstr "U.b.u.n.t.u" >nul 2>nul
if %errorlevel% equ 0 (
    echo Ubuntu is installed in WSL. Launching!
) else (
    echo ---
    echo Ubuntu is not installed in WSL.
    call:wslNotInstalled
)

@REM if not exist .\FindMyIntegration\reports.db (
@REM     sqlite3 .\FindMyIntegration\reports.db "CREATE TABLE reports (id_short TEXT, timestamp INTEGER, datePublished TEXT, lat INTEGER, lon INTEGER, link TEXT, statusCode INTEGER, conf INTEGER)"
@REM )

@REM ### Start the program
cd .\App
start winLaunch.vbs

exit 0

@rem ### What to do if WSL is not installed or improperly configured
:wslNotInstalled
echo ---
echo WSL ^(Windows Subsystem for Linux^) Ubuntu is necessary for this project
echo It allows Linux commands and programs to run on Windows
echo This is necessary for the script that communicates with Apple's servers
echo ---
set /p name=Install? ^(y/n^):

if /i "!name!" == "y" (
    echo Installing WSL...
    wsl --install -d Ubuntu
    if !ERRORLEVEL! NEQ 0 (
        echo ---
        echo Administrator access is required or something else has gone wrong :(
        echo Right click this .bat file and click 'run as admininstrator'
        echo ---
        pause
        exit 126
    ) 
) else (
        echo HayStacker dependency install declined...
        pause
        exit 0
)
goto:eof

endlocal