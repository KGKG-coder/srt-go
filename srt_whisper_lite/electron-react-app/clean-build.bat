@echo off
echo Cleaning and building without icons...

set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
set ELECTRON_BUILDER_ALLOW_UNRESOLVED_DEPENDENCIES=true

echo Removing problematic icon files...
if exist "icon.ico" del /f "icon.ico"
if exist "icon.png" del /f "icon.png"
if exist "logo.png" del /f "logo.png"

echo Cleaning cache...
if exist dist rd /s /q dist 2>nul
if exist "%APPDATA%\electron-builder\Cache" rd /s /q "%APPDATA%\electron-builder\Cache" 2>nul

echo Building React app...
cd react-app
if not exist "build" npm run build
cd ..

echo Creating NSIS installer...
npx electron-builder --win nsis --publish=never

if exist "dist\*.exe" (
    echo SUCCESS! Installer created.
    dir dist\*.exe
) else (
    echo FAILED! Check errors above.
)

pause