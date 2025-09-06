@echo off
REM Create Complete SRT GO Installer Package
REM This creates a self-extracting installer with all components

echo === Creating SRT GO Complete Installer Package ===
echo.

set SOURCE_DIR=dist\SRT-GO-Portable-Working
set PACKAGE_DIR=SRT-GO-Installer-Package
set INSTALLER_NAME=SRT-GO-Complete-Installer-v2.1.0

if not exist "%SOURCE_DIR%" (
    echo Error: Portable version not found: %SOURCE_DIR%
    echo Please ensure the portable version is built first.
    pause
    exit /b 1
)

echo Creating installer package directory...
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

echo Copying portable application...
xcopy "%SOURCE_DIR%" "%PACKAGE_DIR%\SRT-GO-Complete\" /s /e /y

if errorlevel 1 (
    echo Error: Failed to copy application files
    pause
    exit /b 1
)

echo Copying installer script...
copy "installer.bat" "%PACKAGE_DIR%\"

echo Creating final installer archive...
if exist "%INSTALLER_NAME%.zip" del "%INSTALLER_NAME%.zip"

REM Create self-extracting archive with 7-Zip if available
if exist "C:\Program Files\7-Zip\7z.exe" (
    echo Creating self-extracting installer with 7-Zip...
    "C:\Program Files\7-Zip\7z.exe" a -sfx7z.sfx -mx9 "%INSTALLER_NAME%.exe" "%PACKAGE_DIR%\*"
    
    if exist "%INSTALLER_NAME%.exe" (
        echo.
        echo ✅ Self-extracting installer created: %INSTALLER_NAME%.exe
        
        for %%A in ("%INSTALLER_NAME%.exe") do (
            set SIZE=%%~zA
            set /a SIZE_MB=!SIZE!/1024/1024
            echo Installer size: !SIZE_MB! MB
        )
        
        echo.
        echo This installer includes:
        echo ✓ Complete SRT GO application
        echo ✓ Large-v3 AI model (3GB)
        echo ✓ Python environment
        echo ✓ All dependencies
        echo ✓ Automatic shortcuts and uninstaller
        
    ) else (
        echo Self-extracting creation failed, creating ZIP instead...
        goto :create_zip
    )
) else (
    echo 7-Zip not found, creating ZIP archive...
    :create_zip
    powershell -Command "& {Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath '%INSTALLER_NAME%.zip' -CompressionLevel Optimal}"
    
    if exist "%INSTALLER_NAME%.zip" (
        echo.
        echo ✅ ZIP installer created: %INSTALLER_NAME%.zip
        echo Extract and run installer.bat to install SRT GO
        
        for %%A in ("%INSTALLER_NAME%.zip") do (
            set SIZE=%%~zA
            set /a SIZE_MB=!SIZE!/1024/1024
            echo Archive size: !SIZE_MB! MB
        )
    ) else (
        echo ❌ Failed to create installer archive
        pause
        exit /b 1
    )
)

echo.
echo Cleaning up temporary files...
rmdir /s /q "%PACKAGE_DIR%"

echo.
echo === Installer Package Creation Complete ===
echo.
echo Distribution files ready:
if exist "%INSTALLER_NAME%.exe" echo - %INSTALLER_NAME%.exe (Self-extracting installer)
if exist "%INSTALLER_NAME%.zip" echo - %INSTALLER_NAME%.zip (ZIP installer)
echo.
echo Installation instructions:
echo 1. For EXE: Double-click to run installer directly
echo 2. For ZIP: Extract and run installer.bat
echo.
echo Both methods will create a complete SRT GO installation with:
echo - Professional installer interface
echo - Automatic shortcuts creation
echo - Windows Add/Remove Programs integration
echo - Uninstaller included
echo.
pause