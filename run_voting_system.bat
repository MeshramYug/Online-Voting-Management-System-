@echo off
title Online Voting System for Students - SVPCET Nagpur
color 0b

echo ======================================================================
echo    ST. VINCENT PALLOTTI COLLEGE OF ENGINEERING & TECHNOLOGY, NAGPUR
echo    DEPARTMENT OF ARTIFICIAL INTELLIGENCE
echo    ONLINE VOTING SYSTEM FOR STUDENTS - SEPM MINI PROJECT
echo    Student: Yug Meshram (UID: 24001027) ^| Guide: Dr. Vikas Bhowate
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Verifying SQLite Database and SEPM Data Models...
python database.py

echo.
echo [2/3] Launching Web Browser at http://127.0.0.1:5000 ...
start http://127.0.0.1:5000

echo.
echo [3/3] Starting Local Application Server (Flask)...
echo Press CTRL+C at any time in this window to stop the server.
echo ======================================================================
echo.

python server.py

pause

