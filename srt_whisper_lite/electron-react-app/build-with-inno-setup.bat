@echo off
REM Build SRT GO with Inno Setup (handles large files better than NSIS)

echo === Building SRT GO with Inno Setup ===
echo.

REM Check if Inno Setup is installed
set "INNO_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_COMPILER%" (
    echo Error: Inno Setup 6 not found
    echo Please download and install Inno Setup 6 from:
    echo https://jrsoftware.org/isinfo.php
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo Found Inno Setup compiler: %INNO_COMPILER%
echo.

REM Check if portable version exists
if not exist "dist\SRT-GO-Portable-Working" (
    echo Error: Portable version not found
    echo Please ensure dist\SRT-GO-Portable-Working exists
    pause
    exit /b 1
)

echo Building installer with Inno Setup...
echo This may take 10-15 minutes for large AI model files...
echo.

REM Create output directory
if not exist "installer_output" mkdir "installer_output"

REM Compile with Inno Setup
"%INNO_COMPILER%" "SRT-GO-InnoSetup.iss"

if errorlevel 1 (
    echo.
    echo ❌ Inno Setup build failed
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ✅ Inno Setup build completed successfully!
echo.

REM Check output file
for %%f in (installer_output\SRT-GO-Complete-Setup-*.exe) do (
    echo Generated installer: %%f
    for %%A in ("%%f") do (
        set SIZE=%%~zA
        set /a SIZE_MB=!SIZE!/1024/1024
        echo Installer size: !SIZE_MB! MB
    )
)

echo.
echo === Build Summary ===
echo Technology: Inno Setup (better large file support)
echo Features: Complete offline installation
echo AI Model: Large-v3 (highest accuracy)
echo Target: Windows 10/11 (64-bit)
echo.
echo The installer is ready for distribution!
echo.
pause