@echo off
REM Build the launcher into a standalone .exe (no Thonny/IDE needed).
REM Requires: pip install pyinstaller

echo Installing PyInstaller if needed...
pip install pyinstaller

echo.
echo Building launcher...
pyinstaller --noconsole --onefile --name "GameLauncher" main.py

echo.
if exist "dist\GameLauncher.exe" (
    if not exist "dist\data" mkdir dist\data
    if exist "data\games.json" copy /Y data\games.json dist\data\
    if exist "data\settings.json" copy /Y data\settings.json dist\data\
    xcopy /E /I /Y games dist\games >nul 2>&1
    echo Done. Run: dist\GameLauncher.exe
    echo Copy dist\ folder anywhere; run GameLauncher.exe. Keep data\ and games\ next to the exe.
) else (
    echo Build failed. Check errors above.
)
pause
