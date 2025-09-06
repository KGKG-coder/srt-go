/**
 * 修復運行時錯誤 - 增強錯誤處理和診斷
 */

const fs = require('fs');
const path = require('path');

// 創建診斷腳本
const diagnosticScript = `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""診斷腳本 - 檢查Python環境和依賴"""

import sys
import json
import os

def check_environment():
    """檢查Python環境"""
    result = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "python_path": sys.path[:3],
        "working_dir": os.getcwd(),
        "encoding": sys.stdout.encoding
    }
    
    # 檢查必要模組
    modules_to_check = [
        'simplified_subtitle_core',
        'subtitle_formatter',
        'audio_processor',
        'semantic_processor',
        'config_manager'
    ]
    
    result["modules"] = {}
    for module in modules_to_check:
        try:
            __import__(module)
            result["modules"][module] = "✓ OK"
        except ImportError as e:
            result["modules"][module] = f"✗ Error: {str(e)}"
    
    # 檢查依賴套件
    packages = [
        'faster_whisper',
        'numpy',
        'av'
    ]
    
    result["packages"] = {}
    for package in packages:
        try:
            __import__(package)
            result["packages"][package] = "✓ Installed"
        except ImportError:
            result["packages"][package] = "✗ Not installed"
    
    return result

if __name__ == "__main__":
    try:
        result = check_environment()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "type": type(e).__name__
        }, ensure_ascii=False))
        sys.exit(1)
`;

// 創建修復後的 main.js 片段
const mainJsFix = `
      // 增強錯誤處理 - 在 spawn 之前添加更詳細的診斷
      console.log('\\n=== 詳細診斷信息 ===');
      console.log('Command exists:', fs.existsSync(command));
      console.log('Script exists:', fs.existsSync(pythonScript));
      console.log('Working dir exists:', fs.existsSync(workingDir));
      
      // 先執行診斷腳本
      const diagScript = path.join(workingDir, 'diagnostic.py');
      if (!fs.existsSync(diagScript)) {
        // 創建診斷腳本
        fs.writeFileSync(diagScript, \`${diagnosticScript.replace(/`/g, '\\`')}\`, 'utf8');
      }
      
      // 執行診斷
      const { execSync } = require('child_process');
      try {
        const diagResult = execSync(\`"\${command}" "\${diagScript}"\`, {
          cwd: workingDir,
          encoding: 'utf8',
          timeout: 5000
        });
        console.log('Python診斷結果:', diagResult);
      } catch (diagError) {
        console.error('Python診斷失敗:', diagError.message);
        console.error('錯誤輸出:', diagError.stderr?.toString());
        
        // 發送更詳細的錯誤信息
        const detailedError = \`無法執行Python環境診斷：\\n\\n\` +
          \`錯誤類型: \${diagError.code || 'UNKNOWN'}\\n\` +
          \`錯誤信息: \${diagError.message}\\n\\n\` +
          \`可能的原因：\\n\` +
          \`1. Python環境損壞或不完整\\n\` +
          \`2. 防毒軟體阻擋執行\\n\` +
          \`3. 權限不足\\n\\n\` +
          \`建議解決方案：\\n\` +
          \`1. 以管理員身份重新執行程式\\n\` +
          \`2. 將程式加入防毒軟體白名單\\n\` +
          \`3. 重新安裝應用程式\`;
        
        mainWindow.webContents.send('processing-error', { 
          success: false, 
          message: detailedError 
        });
        return reject({ success: false, error: detailedError });
      }
`;

// 寫入診斷腳本
fs.writeFileSync(
  path.join(__dirname, '..', 'diagnostic.py'),
  diagnosticScript,
  'utf8'
);

// 創建安裝依賴腳本
const installDeps = `@echo off
echo 安裝必要依賴...
cd /d "%~dp0"

:: 找到 mini_python
set PYTHON_EXE=mini_python\\python.exe
if not exist "%PYTHON_EXE%" (
    echo 錯誤：找不到 Python 環境
    pause
    exit /b 1
)

echo 使用 Python: %PYTHON_EXE%

:: 安裝基本依賴
echo 安裝 faster-whisper...
"%PYTHON_EXE%" -m pip install faster-whisper --no-deps --quiet

echo 安裝 numpy...
"%PYTHON_EXE%" -m pip install numpy --quiet

echo 安裝 av...
"%PYTHON_EXE%" -m pip install av --quiet

echo 安裝 soundfile...
"%PYTHON_EXE%" -m pip install soundfile --quiet

echo.
echo ✅ 依賴安裝完成！
pause
`;

fs.writeFileSync(
  path.join(__dirname, '..', 'install_dependencies.bat'),
  installDeps
);

console.log('✅ 運行時錯誤修復文件已創建！');
console.log('\n📝 已創建文件：');
console.log('  - diagnostic.py (診斷腳本)');
console.log('  - install_dependencies.bat (依賴安裝腳本)');
console.log('\n💡 建議：');
console.log('  1. 在目標電腦上執行 install_dependencies.bat');
console.log('  2. 手動將 main.js 修改片段加入到錯誤處理部分');
console.log('  3. 重新打包應用程式');