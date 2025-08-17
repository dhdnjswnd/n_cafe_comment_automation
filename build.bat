@echo off
echo Cleaning up previous build directories...
if exist "build" ( rmdir /s /q build )
if exist "dist" ( rmdir /s /q dist )
echo.
echo Running PyInstaller to build the EXE...
pyinstaller -n=PearlAuto --icon=app_icon.ico --onefile --windowed --add-data "app_icon.ico;." gui.py
echo.
echo Build complete! The new EXE is in the 'dist' folder.
pause
