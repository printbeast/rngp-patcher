@echo off
REM RNGP Patcher Build Script
REM This script builds a standalone executable that requires no installation

echo ========================================
echo RNGP Patcher - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Converting logo to ICO format...
python convert_logo.py
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
python -m PyInstaller rngp_patcher.spec --clean
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
