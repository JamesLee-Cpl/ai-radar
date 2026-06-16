@echo off
REM Scheduled-task entry: refresh prices.js + bubble.js, log to data\refresh.log
cd /d %~dp0
if not exist data mkdir data
echo. >> data\refresh.log
echo === %date% %time% === >> data\refresh.log
python fetch_prices.py >> data\refresh.log 2>&1
python bubble.py       >> data\refresh.log 2>&1
