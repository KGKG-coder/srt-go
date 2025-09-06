#!/usr/bin/env node
/**
 * Fix Installer Configuration
 * Updates package.json to ensure all files are included in NSIS installer
 */

const fs = require('fs');
const path = require('path');

function fixInstallerConfig() {
    console.log("=== SRT GO Installer Configuration Fix ===");
    console.log();
    
    // Read current package.json
    const packagePath = path.join(__dirname, 'package.json');
    
    if (!fs.existsSync(packagePath)) {
        console.error("❌ Error: package.json not found");
        return false;
    }
    
    let packageData;
    try {
        const packageContent = fs.readFileSync(packagePath, 'utf8');
        packageData = JSON.parse(packageContent);
    } catch (error) {
        console.error("❌ Error reading package.json:", error.message);
        return false;
    }
    
    console.log("✅ Current package.json loaded");
    console.log(`📦 Current version: ${packageData.version}`);
    
    // Backup original
    const backupPath = packagePath + '.backup';
    fs.writeFileSync(backupPath, JSON.stringify(packageData, null, 2));
    console.log(`📋 Backup created: ${backupPath}`);
    
    // Update build configuration
    packageData.build = {
        "appId": "com.srtgo.ai-subtitle-generator",
        "productName": "SRT GO - AI Subtitle Generator",
        "copyright": "Copyright © 2025 SRT GO Team",
        "directories": {
            "buildResources": "build",
            "output": "dist"
        },
        "compression": "normal", // Changed from "maximum" for faster builds
        "removePackageScripts": true,
        
        // Include all application files
        "files": [
            "main.js",
            "preload.js",
            "environment-manager.js",
            "setup_environment.bat",
            "refresh_path.bat", 
            "react-app/build/**/*",
            "icon.ico",
            "!react-app/build/static/**/*.map",
            "!react-app/build/static/**/*.txt",
            "!**/node_modules/**/test/**",
            "!**/node_modules/**/tests/**",
            "!**/node_modules/**/*.md",
            "!**/node_modules/**/README*",
            "!**/node_modules/**/LICENSE*",
            "!**/node_modules/**/CHANGELOG*",
            "!**/node_modules/**/*.d.ts",
            "!**/node_modules/**/examples/**",
            "!**/node_modules/**/docs/**"
        ],
        
        // Include Python environment and model as external resources
        "extraResources": [
            {
                "from": "dist/SRT-GO-Portable-Working/resources/python",
                "to": "resources/python",
                "filter": ["**/*"]
            },
            {
                "from": "dist/SRT-GO-Portable-Working/resources/mini_python",
                "to": "resources/mini_python", 
                "filter": ["**/*"]
            },
            {
                "from": "dist/SRT-GO-Portable-Working/resources/models",
                "to": "resources/models",
                "filter": ["**/*"]
            }
        ],
        
        // Windows specific settings
        "win": {
            "target": [
                {
                    "target": "nsis",
                    "arch": ["x64"]
                }
            ],
            "icon": "icon.ico",
            "publisherName": "SRT GO Team",
            "requestedExecutionLevel": "asInvoker",
            "artifactName": "${productName}-Setup-${version}.${ext}",
            "verifyUpdateCodeSignature": false
        },
        
        // NSIS installer configuration
        "nsis": {
            "oneClick": false,
            "allowToChangeInstallationDirectory": true,
            "allowElevation": true,
            "installerIcon": "icon.ico",
            "uninstallerIcon": "icon.ico",
            "installerHeaderIcon": "icon.ico",
            "createDesktopShortcut": true,
            "createStartMenuShortcut": true,
            "shortcutName": "SRT GO - AI Subtitle Generator",
            "differentialPackage": false,
            "packElevateHelper": false,
            "installerLanguages": ["en_US", "zh_TW", "zh_CN"],
            "language": "1033", // English as primary
            "artifactName": "${productName}-Setup-${version}.${ext}",
            "deleteAppDataOnUninstall": false,
            "include": "installer-script.nsh" // Optional custom NSIS script
        },
        
        // Ensure resources are not packed in ASAR for accessibility
        "asarUnpack": [
            "resources/mini_python/**/*",
            "resources/python/**/*",
            "resources/models/**/*"
        ]
    };
    
    // Update scripts to include proper build commands
    packageData.scripts = {
        ...packageData.scripts,
        "build:installer": "npm run react:build && electron-builder --win",
        "build:installer-dir": "npm run react:build && electron-builder --win --dir",
        "dist:nsis": "npm run react:build && electron-builder --win nsis",
        "dist:portable": "npm run react:build && electron-builder --win portable"
    };
    
    // Write updated package.json
    try {
        fs.writeFileSync(packagePath, JSON.stringify(packageData, null, 2));
        console.log("✅ package.json updated successfully");
        
        // Verify the update
        const verification = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        if (verification.build && verification.build.extraResources) {
            console.log("✅ Configuration verification passed");
            console.log(`📋 Extra resources: ${verification.build.extraResources.length} entries`);
            console.log(`📋 NSIS configuration: ${verification.build.nsis ? 'Present' : 'Missing'}`);
            
            return true;
        } else {
            console.error("❌ Configuration verification failed");
            return false;
        }
        
    } catch (error) {
        console.error("❌ Error writing package.json:", error.message);
        return false;
    }
}

function createInstallerScript() {
    /**
     * Create optional NSIS installer script for custom installation behavior
     */
    const scriptContent = `; SRT GO Custom NSIS Installer Script
; Additional installer customizations

!define PRODUCT_NAME "SRT GO - AI Subtitle Generator"
!define PRODUCT_VERSION "2.1.0"

; Custom installer messages
LangString WELCOME_TEXT \${LANG_ENGLISH} "Welcome to SRT GO - AI Subtitle Generator Setup. This will install a powerful AI-powered subtitle generation tool on your computer."
LangString WELCOME_TEXT \${LANG_SIMPCHINESE} "欢迎使用 SRT GO - AI 字幕生成工具安装程序。这将在您的计算机上安装强大的AI字幕生成工具。"
LangString WELCOME_TEXT \${LANG_TRADCHINESE} "歡迎使用 SRT GO - AI 字幕生成工具安裝程式。這將在您的電腦上安裝強大的AI字幕生成工具。"

; Custom installation directory validation
Function .onVerifyInstDir
  ; Ensure installation directory has enough space (minimum 6GB)
  \${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntOp $0 $0 / 1024  ; Convert to MB
  IntOp $0 $0 / 1024  ; Convert to GB
  
  ; Check available space (approximate 6GB needed)
  \${DriveSpace} "$INSTDIR" "/D=F /S=M" $3
  IntOp $3 $3 / 1024  ; Convert to GB
  
  IntCmp $3 6 space_ok space_ok space_error
  
  space_error:
    MessageBox MB_OK|MB_ICONSTOP "Insufficient disk space. At least 6GB free space required for SRT GO installation."
    Abort
    
  space_ok:
    ; Continue with installation
FunctionEnd

; Post-installation actions
Function .onInstSuccess
  MessageBox MB_YESNO|MB_ICONQUESTION "SRT GO has been successfully installed. Would you like to launch it now?" IDNO end
    Exec "$INSTDIR\\SRT GO - AI Subtitle Generator.exe"
  end:
FunctionEnd`;

    const scriptPath = path.join(__dirname, 'installer-script.nsh');
    fs.writeFileSync(scriptPath, scriptContent, 'utf8');
    console.log(`✅ Custom NSIS script created: ${scriptPath}`);
}

function main() {
    const success = fixInstallerConfig();
    
    if (success) {
        console.log();
        console.log("🎉 Installer configuration fix completed!");
        console.log();
        console.log("📋 Next steps:");
        console.log("1. Run: npm run build:installer");
        console.log("2. Test the generated installer");
        console.log("3. Verify all components are included");
        
        // Create optional NSIS script
        createInstallerScript();
        
        console.log();
        console.log("🎯 New build commands available:");
        console.log("- npm run build:installer (full installer)");
        console.log("- npm run build:installer-dir (directory build for testing)");
        console.log("- npm run dist:nsis (NSIS only)");
        console.log("- npm run dist:portable (portable version)");
        
    } else {
        console.log();
        console.log("❌ Configuration fix failed");
        console.log("Please check the error messages above");
    }
    
    return success;
}

// Run the fix
if (require.main === module) {
    main();
}

module.exports = { fixInstallerConfig, createInstallerScript };