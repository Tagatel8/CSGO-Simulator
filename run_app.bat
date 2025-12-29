@echo off
cd /d "%~dp0"
echo Starting CS2 Match Simulator...
echo Current directory: %cd%
echo Python version:
python --version
echo.
echo Running cs2_app.py...
python cs2_app.py
echo.
echo App finished. Press any key to close...
pause