@echo off
REM RNGP Patcher Build Script
REM This script builds a standalone executable that requires no installation

echo ========================================
echo RNGP Patcher - Build Script
echo ========================================
echo.

REM Check if Python is installed - try multiple commands
set PYTHON_CMD=
echo Checking for Python installation...

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_found
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    goto :python_found
)

REM If we get here, Python wasn't found
echo ERROR: Python is not installed or not in PATH
echo.
echo The build script requires Python to be installed and in your PATH.
echo.
echo Common solutions:
echo 1. Install Python from python.org (recommended)
echo    - Download from: https://python.org/downloads/
echo    - During installation, make sure to check "Add Python to PATH"
echo 2. If Python is installed but not in PATH:
echo    - Add Python directory to your system PATH environment variable
echo    - Common Python locations:
echo      C:\Python313\
echo      C:\Users\[username]\AppData\Local\Programs\Python\Python313\
echo      C:\Users\[username]\AppData\Local\Microsoft\WindowsApps\
echo 3. Verify Python installation:
echo    - Open a NEW command prompt
echo    - Run: python --version
echo    - If this fails, Python is not properly installed or in PATH
echo.
pause
exit /b 1

:python_found
echo Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo [1/5] Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Converting logo to ICO format...
%PYTHON_CMD% convert_logo.py
if errorlevel 1 (
    echo WARNING: Could not convert logo to ICO (will use PNG only)
)

echo.
echo [3/5] Cleaning old build files...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "RNGP_Patcher.exe" del /f "RNGP_Patcher.exe"

echo.
echo [4/5] Building standalone executable...
echo This may take a few minutes...
%PYTHON_CMD% -m PyInstaller rngp_patcher.spec --clean
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Finalizing...
if exist "dist\RNGP_Patcher.exe" (
    copy /y "dist\RNGP_Patcher.exe" "RNGP_Patcher.exe"
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo The executable is ready: RNGP_Patcher.exe
    echo.
    echo You can distribute this single file to your players.
    echo They don't need to install Python or any dependencies!
    echo.
) else (
    echo ERROR: Executable not found in dist folder
    pause
    exit /b 1
)

echo Cleaning up build files...
rmdir /s /q "build"
rmdir /s /q "dist"

echo.
echo Done! Press any key to exit...
pause >nul
