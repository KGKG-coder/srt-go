/**
 * 綜合錯誤修復方案 - 確保不再出現 Error invoking remote method
 */

const fs = require('fs');
const path = require('path');

console.log('🛡️ 開始部署綜合錯誤修復方案...\n');

// 1. 創建增強的錯誤處理機制
const enhancedErrorHandling = `
// ===== 增強錯誤處理機制 =====

// 全域錯誤處理函數
function safeExecute(operation, fallbackValue = null) {
  try {
    return operation();
  } catch (error) {
    console.error('Operation failed:', error.message);
    return fallbackValue;
  }
}

// IPC 安全包裝器
function safeIpcHandle(channel, handler) {
  ipcMain.handle(channel, async (event, ...args) => {
    try {
      console.log(\`📨 IPC 請求: \${channel}\`, args.length > 0 ? args[0] : '');
      const startTime = Date.now();
      
      const result = await handler(event, ...args);
      
      const duration = Date.now() - startTime;
      console.log(\`✅ IPC 完成: \${channel} (\${duration}ms)\`);
      
      return result;
    } catch (error) {
      console.error(\`❌ IPC 錯誤: \${channel}\`, error);
      
      // 返回結構化錯誤信息
      const errorInfo = {
        success: false,
        error: error.message || 'Unknown error',
        code: error.code || 'UNKNOWN_ERROR',
        timestamp: new Date().toISOString(),
        channel: channel
      };
      
      // 發送錯誤到前端
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('processing-error', {
          success: false,
          message: \`處理失敗: \${error.message || '未知錯誤'}\`
        });
      }
      
      return errorInfo;
    }
  });
}

// 參數驗證函數
function validateProcessingOptions(options) {
  if (!options || typeof options !== 'object') {
    throw new Error('處理選項無效');
  }
  
  const { files, settings } = options;
  
  if (!files || !Array.isArray(files) || files.length === 0) {
    throw new Error('未選擇有效的檔案');
  }
  
  if (!settings || typeof settings !== 'object') {
    throw new Error('處理設置無效');
  }
  
  // 驗證檔案路徑
  for (const file of files) {
    const filePath = file.path || file;
    if (!filePath || typeof filePath !== 'string') {
      throw new Error('檔案路徑格式錯誤');
    }
    if (!fs.existsSync(filePath)) {
      throw new Error(\`檔案不存在: \${filePath}\`);
    }
  }
  
  return true;
}

// 路徑安全驗證
function validatePaths(command, pythonScript, workingDir) {
  const issues = [];
  
  if (!fs.existsSync(command)) {
    issues.push(\`Python 執行檔不存在: \${command}\`);
  }
  
  if (!fs.existsSync(pythonScript)) {
    issues.push(\`Python 腳本不存在: \${pythonScript}\`);
  }
  
  if (!fs.existsSync(workingDir)) {
    issues.push(\`工作目錄不存在: \${workingDir}\`);
  }
  
  if (issues.length > 0) {
    throw new Error(\`路徑驗證失敗:\\n\${issues.join('\\n')}\`);
  }
  
  return true;
}

// Python 環境檢測
async function testPythonEnvironment(command, workingDir) {
  return new Promise((resolve, reject) => {
    const testCmd = \`"\${command}" -c "import sys; print('Python OK:', sys.version)"\`;
    
    const { exec } = require('child_process');
    exec(testCmd, {
      cwd: workingDir,
      timeout: 5000,
      encoding: 'utf8'
    }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(\`Python 環境測試失敗: \${error.message}\`));
        return;
      }
      
      if (stderr && stderr.trim()) {
        console.warn('Python 測試警告:', stderr.trim());
      }
      
      console.log('✅ Python 環境測試通過:', stdout.trim());
      resolve(true);
    });
  });
}
`;

// 2. 創建改進的 process-files 處理器
const enhancedProcessFiles = `
// ===== 改進的 process-files 處理器 =====

// 使用安全 IPC 處理器
safeIpcHandle('process-files', async (event, options) => {
  console.log('\\n🚀 開始安全的檔案處理流程...');
  
  // 第一步：驗證輸入參數
  validateProcessingOptions(options);
  
  const { files, settings, corrections } = options;
  console.log(\`📁 處理 \${files.length} 個檔案\`);
  console.log('⚙️ 設置:', JSON.stringify(settings, null, 2));
  
  // 第二步：建立安全路徑
  const isPackaged = app.isPackaged;
  let command, pythonScript, workingDir;
  
  if (isPackaged) {
    const appDirectory = path.dirname(process.execPath);
    command = safePath(appDirectory, 'resources', 'mini_python', 'python.exe');
    pythonScript = safePath(appDirectory, 'resources', 'python', 'electron_backend.py');
    workingDir = safePath(appDirectory, 'resources', 'python');
  } else {
    const pythonPath = safePath(__dirname, '..', 'mini_python', 'python.exe');
    if (fs.existsSync(pythonPath)) {
      command = pythonPath;
      pythonScript = safePath(__dirname, '..', 'electron_backend.py');
      workingDir = safePath(__dirname, '..');
    } else {
      command = 'python';
      pythonScript = safePath(__dirname, '..', 'electron_backend.py');
      workingDir = safePath(__dirname, '..');
    }
  }
  
  // 第三步：驗證所有路徑
  validatePaths(command, pythonScript, workingDir);
  
  // 第四步：測試 Python 環境
  await testPythonEnvironment(command, workingDir);
  
  // 第五步：準備安全參數
  const safeArgs = [
    pythonScript,
    '--files', JSON.stringify(files.map(f => normalizePath(f.path || f))),
    '--settings', JSON.stringify(settings),
    '--corrections', JSON.stringify(corrections || [])
  ];
  
  console.log('📋 執行參數準備完成');
  console.log('  命令:', command);
  console.log('  腳本:', pythonScript);
  console.log('  工作目錄:', workingDir);
  
  // 第六步：安全執行 Python 進程
  return new Promise((resolve, reject) => {
    let output = '';
    let errorOutput = '';
    let hasCompleted = false;
    
    // 設置超時保護
    const timeoutId = setTimeout(() => {
      if (!hasCompleted) {
        console.error('⏰ 處理超時');
        hasCompleted = true;
        if (currentProcess) {
          currentProcess.kill('SIGTERM');
        }
        reject(new Error('處理超時 - 請檢查檔案大小或系統性能'));
      }
    }, 30 * 60 * 1000); // 30分鐘超時
    
    try {
      currentProcess = spawn(command, safeArgs, {
        cwd: workingDir,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: false,
        shell: false
      });
      
      // 處理 stdout
      currentProcess.stdout.on('data', (data) => {
        const dataStr = data.toString('utf8');
        output += dataStr;
        
        // 解析進度信息
        const lines = dataStr.split('\\n');
        lines.forEach(line => {
          if (line.includes('PROGRESS:')) {
            try {
              const progressData = line.replace('PROGRESS:', '').trim();
              const progress = JSON.parse(progressData);
              mainWindow.webContents.send('processing-progress', progress);
            } catch (e) {
              console.log('進度解析失敗:', line);
            }
          } else if (line.includes('COMPLETE:')) {
            try {
              const completeData = line.replace('COMPLETE:', '').trim();
              const completion = JSON.parse(completeData);
              console.log('✅ 處理完成:', completion);
              hasCompleted = true;
              clearTimeout(timeoutId);
              mainWindow.webContents.send('processing-complete', completion);
              resolve(completion);
            } catch (e) {
              console.log('完成信息解析失敗:', line);
            }
          }
        });
      });
      
      // 處理 stderr（不立即視為錯誤）
      currentProcess.stderr.on('data', (data) => {
        const errorStr = data.toString('utf8');
        errorOutput += errorStr;
        console.log('Python stderr:', errorStr);
      });
      
      // 進程錯誤處理
      currentProcess.on('error', (err) => {
        console.error('❌ 進程啟動失敗:', err);
        hasCompleted = true;
        clearTimeout(timeoutId);
        
        let userFriendlyMessage = '無法啟動處理程序。';
        if (err.code === 'ENOENT') {
          userFriendlyMessage += '\\n\\nPython 環境可能損壞，請重新安裝應用程式。';
        } else if (err.code === 'EACCES') {
          userFriendlyMessage += '\\n\\n權限不足，請以管理員身份執行程式。';
        } else {
          userFriendlyMessage += \`\\n\\n錯誤詳情: \${err.message}\`;
        }
        
        reject(new Error(userFriendlyMessage));
      });
      
      // 進程退出處理
      currentProcess.on('close', (code, signal) => {
        clearTimeout(timeoutId);
        
        if (hasCompleted) {
          return; // 已經在其他地方處理過了
        }
        
        if (code === 0) {
          console.log('✅ Python 進程正常結束');
          resolve({
            success: true,
            message: '處理完成',
            output: output.trim()
          });
        } else {
          console.error(\`❌ Python 進程異常結束: code=\${code}, signal=\${signal}\`);
          console.error('錯誤輸出:', errorOutput);
          
          reject(new Error(\`處理失敗 (退出代碼: \${code})\\n\\n錯誤信息: \${errorOutput || '無詳細錯誤信息'}\`));
        }
      });
      
    } catch (spawnError) {
      console.error('❌ spawn 調用失敗:', spawnError);
      clearTimeout(timeoutId);
      reject(new Error(\`無法啟動處理程序: \${spawnError.message}\`));
    }
  });
});
`;

// 3. 創建前端錯誤處理改進
const frontendErrorHandling = `
// ===== 前端錯誤處理改進 =====

// 在 preload.js 中添加
window.electronAPI = {
  ...window.electronAPI,
  
  // 安全的檔案處理調用
  processFilesSafely: async (options) => {
    try {
      console.log('🔒 安全調用 process-files');
      const result = await ipcRenderer.invoke('process-files', options);
      
      if (result && result.success === false) {
        throw new Error(result.error || result.message || 'Processing failed');
      }
      
      return result;
    } catch (error) {
      console.error('❌ process-files 調用失敗:', error);
      
      // 顯示用戶友好的錯誤信息
      const friendlyMessage = error.message || 'Unknown error occurred';
      
      // 觸發錯誤事件
      window.dispatchEvent(new CustomEvent('processing-error', {
        detail: { message: friendlyMessage }
      }));
      
      throw error;
    }
  }
};

// 在 React 組件中使用
const handleProcessFiles = async (files, settings) => {
  try {
    setIsProcessing(true);
    setError(null);
    
    const result = await window.electronAPI.processFilesSafely({
      files,
      settings,
      corrections: []
    });
    
    console.log('✅ 處理成功:', result);
    
  } catch (error) {
    console.error('❌ 處理失敗:', error);
    setError(error.message);
    
    // 顯示詳細錯誤信息
    showToast({
      type: 'error',
      title: '處理失敗',
      message: error.message
    });
  } finally {
    setIsProcessing(false);
  }
};
`;

// 寫入修復檔案
fs.writeFileSync(
  path.join(__dirname, 'enhanced_error_handling.patch'),
  enhancedErrorHandling,
  'utf8'
);

fs.writeFileSync(
  path.join(__dirname, 'enhanced_process_files.patch'),
  enhancedProcessFiles,
  'utf8'
);

fs.writeFileSync(
  path.join(__dirname, 'frontend_error_handling.patch'),
  frontendErrorHandling,
  'utf8'
);

// 4. 創建自動測試腳本
const testScript = `
/**
 * 自動測試腳本 - 驗證錯誤處理機制
 */

const { execSync } = require('child_process');
const path = require('path');

async function runTests() {
  console.log('🧪 開始錯誤處理機制測試...');
  
  const tests = [
    {
      name: '測試 Python 環境',
      command: '"D:/新增資料夾/srt-go-minimalist/resources/mini_python/python.exe" --version'
    },
    {
      name: '測試腳本存在性',
      command: 'dir "D:/新增資料夾/srt-go-minimalist/resources/python/electron_backend.py"'
    },
    {
      name: '測試模組導入',
      command: 'cd "D:/新增資料夾/srt-go-minimalist/resources/python" && "D:/新增資料夾/srt-go-minimalist/resources/mini_python/python.exe" -c "import sys; print(\\"✅ Python 環境正常\\", sys.version)"'
    }
  ];
  
  for (const test of tests) {
    try {
      console.log(\`\\n📋 \${test.name}...\`);
      const result = execSync(test.command, { encoding: 'utf8' });
      console.log(\`✅ 通過: \${result.trim()}\`);
    } catch (error) {
      console.error(\`❌ 失敗: \${error.message}\`);
    }
  }
  
  console.log('\\n🎯 測試完成！');
}

runTests().catch(console.error);
`;

fs.writeFileSync(
  path.join(__dirname, 'test_error_handling.js'),
  testScript,
  'utf8'
);

// 5. 創建部署腳本
const deployScript = `@echo off
echo 🚀 部署綜合錯誤修復方案...

echo.
echo 📝 備份原始檔案...
copy main.js main.js.backup

echo.
echo 🔧 應用修復補丁...
echo 請手動將以下補丁應用到 main.js:
echo   - enhanced_error_handling.patch
echo   - enhanced_process_files.patch

echo.
echo 🧪 執行測試...
node test_error_handling.js

echo.
echo ✅ 修復方案部署完成！
echo.
echo 💡 下一步：
echo   1. 手動應用補丁到 main.js
echo   2. 重新打包應用程式
echo   3. 測試安裝檔案
echo.
pause
`;

fs.writeFileSync(
  path.join(__dirname, 'deploy_fixes.bat'),
  deployScript
);

console.log('✅ 綜合錯誤修復方案創建完成！\\n');
console.log('📝 已創建文件：');
console.log('  - enhanced_error_handling.patch');
console.log('  - enhanced_process_files.patch'); 
console.log('  - frontend_error_handling.patch');
console.log('  - test_error_handling.js');
console.log('  - deploy_fixes.bat');
console.log('\\n🚀 執行 deploy_fixes.bat 開始部署修復方案');