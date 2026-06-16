@echo off
REM Scheduled-task entry: refresh data then push to GitHub Pages
cd /d %~dp0
if not exist data mkdir data
echo. >> data\refresh.log
echo === %date% %time% === >> data\refresh.log
python fetch_prices.py >> data\refresh.log 2>&1
python bubble.py >> data\refresh.log 2>&1
set GIT="C:\Program Files\Git\cmd\git.exe"
%GIT% add prices.js bubble.js >> data\refresh.log 2>&1
%GIT% commit -m "auto data update %date%" >> data\refresh.log 2>&1
%GIT% push origin main >> data\refresh.log 2>&1
echo --- push done --- >> data\refresh.log
