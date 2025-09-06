@echo off
title SRT GO Electron Build

echo ========================================
echo  SRT GO Electron Simple Build
echo ========================================

:: Set environment to skip signing
set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
set CSC_LINK=

echo [1/3] Cleaning cache...
if exist "%APPDATA%\electron-builder\Cache" rd /s /q "%APPDATA%\electron-builder\Cache" 2>nul
if exist "dist" rd /s /q "dist" 2>nul

echo [2/3] Building React app if needed...
cd react-app
if not exist "build" npm run build
cd ..

echo [3/3] Packaging Electron app...
npx electron-builder --win portable --publish=never

echo.
if exist "dist\*.exe" (
    echo SUCCESS! Check the dist folder for your app.
    echo Location: %cd%\dist\
    for %%f in (dist\*.exe) do echo File: %%f
) else (
    echo FAILED! Check error messages above.
)

pause