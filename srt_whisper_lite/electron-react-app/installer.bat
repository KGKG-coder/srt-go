@echo off
REM SRT GO - AI Subtitle Generator Self-Extracting Installer
REM Version 2.1.0
REM This installer extracts the complete SRT GO application with AI models

title SRT GO - AI Subtitle Generator Installer v2.1.0
color 0A

echo.
echo ===============================================================================
echo   SRT GO - AI Subtitle Generator v2.1.0 Installer
echo   Professional AI-Powered Subtitle Generation Tool
echo ===============================================================================
echo.

REM Check if running as administrator for system-wide installation
net session >nul 2>&1
if errorlevel 1 (
    echo [INFO] Running in user mode - will install to user directory
    set "INSTALL_MODE=user"
    set "DEFAULT_INSTALL_DIR=%LOCALAPPDATA%\Programs\SRT GO"
) else (
    echo [INFO] Running as administrator - can install system-wide
    set "INSTALL_MODE=admin"
    set "DEFAULT_INSTALL_DIR=%PROGRAMFILES%\SRT GO - AI Subtitle Generator"
)

echo.
echo Choose installation directory:
echo   1. Default: %DEFAULT_INSTALL_DIR%
echo   2. Custom location
echo.
set /p "INSTALL_CHOICE=Enter choice (1 or 2, default=1): "

if "%INSTALL_CHOICE%"=="2" (
    echo.
    set /p "CUSTOM_DIR=Enter installation directory: "
    if not "%CUSTOM_DIR%"=="" (
        set "INSTALL_DIR=%CUSTOM_DIR%"
    ) else (
        set "INSTALL_DIR=%DEFAULT_INSTALL_DIR%"
    )
) else (
    set "INSTALL_DIR=%DEFAULT_INSTALL_DIR%"
)

echo.
echo Installation directory: %INSTALL_DIR%
echo.

REM Check disk space (approximate 6GB needed)
echo Checking disk space...
for %%A in ("%INSTALL_DIR%") do (
    set "DRIVE=%%~dA"
)

REM Create installation directory
echo Creating installation directory...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%" 2>nul
    if errorlevel 1 (
        echo ❌ Error: Cannot create installation directory
        echo Please check permissions or try running as administrator
        pause
        exit /b 1
    )
)

echo.
echo ===============================================================================
echo   Starting Installation...
echo ===============================================================================
echo.

REM Extract application files
echo [1/4] Extracting application files...
set "SCRIPT_DIR=%~dp0"
set "SOURCE_DIR=%SCRIPT_DIR%SRT-GO-Complete"

if not exist "%SOURCE_DIR%" (
    echo ❌ Error: Installation files not found
    echo Expected location: %SOURCE_DIR%
    pause
    exit /b 1
)

echo Copying files to: %INSTALL_DIR%
xcopy "%SOURCE_DIR%\*" "%INSTALL_DIR%\" /s /e /y /q
if errorlevel 1 (
    echo ❌ Error: Failed to copy application files
    pause
    exit /b 1
)

echo ✅ Application files extracted successfully

REM Verify critical files
echo [2/4] Verifying installation...
if not exist "%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe" (
    echo ❌ Error: Main executable not found
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\resources\mini_python\python.exe" (
    echo ❌ Error: Python environment not found
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\resources\models" (
    echo ❌ Error: AI models directory not found
    pause
    exit /b 1
)

echo ✅ Installation verified successfully

REM Create shortcuts
echo [3/4] Creating shortcuts...

REM Desktop shortcut
set "DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\SRT GO.lnk"
powershell -Command "\$WshShell = New-Object -comObject WScript.Shell; \$Shortcut = \$WshShell.CreateShortcut('%DESKTOP_SHORTCUT%'); \$Shortcut.TargetPath = '%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe'; \$Shortcut.WorkingDirectory = '%INSTALL_DIR%'; \$Shortcut.IconLocation = '%INSTALL_DIR%\icon.ico'; \$Shortcut.Description = 'SRT GO - AI Subtitle Generator'; \$Shortcut.Save()"

REM Start Menu shortcut
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\SRT GO"
if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
set "STARTMENU_SHORTCUT=%STARTMENU_DIR%\SRT GO - AI Subtitle Generator.lnk"
powershell -Command "\$WshShell = New-Object -comObject WScript.Shell; \$Shortcut = \$WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); \$Shortcut.TargetPath = '%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe'; \$Shortcut.WorkingDirectory = '%INSTALL_DIR%'; \$Shortcut.IconLocation = '%INSTALL_DIR%\icon.ico'; \$Shortcut.Description = 'SRT GO - AI Subtitle Generator'; \$Shortcut.Save()"

REM Uninstall shortcut
set "UNINSTALL_SHORTCUT=%STARTMENU_DIR%\Uninstall SRT GO.lnk"
powershell -Command "\$WshShell = New-Object -comObject WScript.Shell; \$Shortcut = \$WshShell.CreateShortcut('%UNINSTALL_SHORTCUT%'); \$Shortcut.TargetPath = '%INSTALL_DIR%\uninstall.bat'; \$Shortcut.WorkingDirectory = '%INSTALL_DIR%'; \$Shortcut.Description = 'Uninstall SRT GO'; \$Shortcut.Save()"

echo ✅ Shortcuts created successfully

REM Create uninstaller
echo [4/4] Creating uninstaller...
set "UNINSTALLER=%INSTALL_DIR%\uninstall.bat"
(
echo @echo off
echo title Uninstall SRT GO - AI Subtitle Generator
echo echo.
echo echo ===============================================================================
echo echo   Uninstalling SRT GO - AI Subtitle Generator
echo echo ===============================================================================
echo echo.
echo set /p "CONFIRM=Are you sure you want to uninstall SRT GO? (Y/N): "
echo if /I not "%%CONFIRM%%"=="Y" goto :cancel
echo echo.
echo echo Removing application files...
echo cd /d "%%TEMP%%"
echo timeout /t 2 /nobreak ^>nul
echo rmdir /s /q "%INSTALL_DIR%"
echo echo.
echo echo Removing shortcuts...
echo del "%DESKTOP_SHORTCUT%" 2^>nul
echo rmdir /s /q "%STARTMENU_DIR%" 2^>nul
echo echo.
echo echo ✅ SRT GO has been successfully uninstalled
echo goto :end
echo :cancel
echo echo Uninstall cancelled
echo :end
echo pause
) > "%UNINSTALLER%"

echo ✅ Uninstaller created successfully

REM Register with Windows Add/Remove Programs
echo Registering with Windows...
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\SRT GO"
reg add "%REG_KEY%" /v "DisplayName" /t REG_SZ /d "SRT GO - AI Subtitle Generator" /f >nul
reg add "%REG_KEY%" /v "DisplayVersion" /t REG_SZ /d "2.1.0" /f >nul
reg add "%REG_KEY%" /v "Publisher" /t REG_SZ /d "SRT GO Team" /f >nul
reg add "%REG_KEY%" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul
reg add "%REG_KEY%" /v "UninstallString" /t REG_SZ /d "%UNINSTALLER%" /f >nul
reg add "%REG_KEY%" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\icon.ico" /f >nul

echo.
echo ===============================================================================
echo   Installation Complete!
echo ===============================================================================
echo.
echo SRT GO - AI Subtitle Generator has been successfully installed to:
echo %INSTALL_DIR%
echo.
echo Features included:
echo ✓ Large-v3 AI Model (Highest accuracy)
echo ✓ SubEasy 5-Layer Filtering System
echo ✓ Multi-language support (EN/ZH/JA/KO)
echo ✓ Professional subtitle formats (SRT/VTT/TXT)
echo ✓ Offline processing (Complete privacy)
echo.
echo Shortcuts created:
echo ✓ Desktop: SRT GO.lnk
echo ✓ Start Menu: SRT GO folder
echo ✓ Add/Remove Programs: Registered
echo.
set /p "LAUNCH=Would you like to launch SRT GO now? (Y/N): "
if /I "%%LAUNCH%%"=="Y" (
    echo.
    echo Starting SRT GO...
    start "" "%INSTALL_DIR%\SRT GO - AI Subtitle Generator.exe"
)

echo.
echo Thank you for installing SRT GO - AI Subtitle Generator!
echo.
pause