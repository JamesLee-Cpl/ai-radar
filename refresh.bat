@echo off
REM Scheduled-task entry: refresh prices.js + bubble.js, then push to GitHub Pages.
REM Logs to data\refresh.log
cd /d %~dp0
if not exist data mkdir data
echo. >> data\refresh.log
echo === %date% %time% === >> data\refresh.log

REM 1) regenerate data
python fetch_prices.py >> data\refresh.log 2>&1
python bubble.py       >> data\refresh.log 2>&1

REM 2) publish to GitHub Pages (credential stored by Git Credential Manager)
set GIT="C:\Program Files\Git\cmd\git.exe"
%GIT% add prices.js bubble.js >> data\refresh.log 2>&1
%GIT% commit -m "auto: 数据更新 %date% %time%" >> data\refresh.log 2>&1
%GIT% push origin main >> data\refresh.log 2>&1
echo --- push done --- >> data\refresh.log
