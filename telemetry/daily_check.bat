@echo off
REM Daily Shadow Mode Drift Check
REM Schedule with Windows Task Scheduler

cd /d %~dp0..
python telemetry\analyze_shadow_drift.py > telemetry\daily_report.txt 2>&1

REM Append timestamp
echo. >> telemetry\daily_report.txt
echo Report generated: %date% %time% >> telemetry\daily_report.txt
