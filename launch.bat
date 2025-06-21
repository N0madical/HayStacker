@echo off

WHERE sqlite3
if %ERRORLEVEL% NEQ 0 (
    echo --
    echo Please install SQlite database management:
    echo https://sqlite.org/download.html
    echo Direct download for x64 windows: https://sqlite.org/2025/sqlite-dll-win-x64-3500100.zip
    echo --
    pause
) 

if not exist .\reports.db (
    sqlite3 reports.db "CREATE TABLE reports (id_short TEXT, timestamp INTEGER, datePublished TEXT, lat INTEGER, lon INTEGER, link TEXT, statusCode INTEGER, conf INTEGER)"
)

cd .\App
start winLaunch.vbs