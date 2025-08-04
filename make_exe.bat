:: Quick EXE Creation Commands
@echo off
echo 🚀 Doc-Scanner EXE Creator
echo ========================

echo.
echo Choose your method:
echo 1. PyInstaller (Command Line)
echo 2. auto-py-to-exe (GUI)
echo.

set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Running PyInstaller method...
    python create_exe.py
) else if "%choice%"=="2" (
    echo Running GUI method...
    python create_exe_gui.py
) else (
    echo Invalid choice. Running PyInstaller method...
    python create_exe.py
)

pause
