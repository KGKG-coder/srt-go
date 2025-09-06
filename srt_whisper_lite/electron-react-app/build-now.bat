@echo off
echo Building SRT GO Electron App...

set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=

echo Cleaning cache...
if exist "%APPDATA%\electron-builder\Cache" rd /s /q "%APPDATA%\electron-builder\Cache" 2>nul

echo Starting build...
npx electron-builder --win portable --publish=never

echo.
if exist "dist\*.exe" (
    echo SUCCESS! 
    echo Check: %cd%\dist\
    dir dist\*.exe
) else (
    echo FAILED! Check errors above.
)

pause