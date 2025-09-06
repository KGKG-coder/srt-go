const path = require('path');
const fs = require('fs');

// 測試路徑函數
function normalizePath(p) {
  return p.replace(/\\/g, '/');
}

// 測試嵌入式 Python 路徑檢測
function getEmbeddedPythonPath() {
  const pythonPath = path.join(__dirname, 'mini_python', 'python.exe');
  
  if (fs.existsSync(pythonPath)) {
    console.log('[OK] 找到嵌入式 Python:', pythonPath);
    return pythonPath;
  } else {
    console.log('[錯誤] 嵌入式 Python 不存在:', pythonPath);
    return null;
  }
}

// 測試 Python 腳本路徑檢測
function getPythonScriptPath() {
  const scriptPath = path.join(__dirname, 'python', 'test_backend_minimal.py');
  
  if (fs.existsSync(scriptPath)) {
    console.log('[OK] 找到測試腳本:', scriptPath);
    return scriptPath;
  } else {
    console.log('[錯誤] 測試腳本不存在:', scriptPath);
    return null;
  }
}

// 測試 main_simplified.js 路徑
function testMainSimplified() {
  const mainPath = path.join(__dirname, 'main_simplified.js');
  
  if (fs.existsSync(mainPath)) {
    console.log('[OK] 找到 main_simplified.js:', mainPath);
    
    // 讀取檔案內容檢查關鍵函數
    const content = fs.readFileSync(mainPath, 'utf8');
    
    if (content.includes('getEmbeddedPythonPath')) {
      console.log('[OK] 包含 getEmbeddedPythonPath 函數');
    } else {
      console.log('[警告] 缺少 getEmbeddedPythonPath 函數');
    }
    
    if (content.includes('getPythonScriptPath')) {
      console.log('[OK] 包含 getPythonScriptPath 函數');
    } else {
      console.log('[警告] 缺少 getPythonScriptPath 函數');
    }
    
    return true;
  } else {
    console.log('[錯誤] main_simplified.js 不存在:', mainPath);
    return false;
  }
}

// 主測試函數
function main() {
  console.log('=== main_simplified.js 路徑測試 ===');
  console.log('當前目錄:', __dirname);
  console.log('Node.js 版本:', process.version);
  console.log();
  
  const pythonPath = getEmbeddedPythonPath();
  const scriptPath = getPythonScriptPath();
  const mainExists = testMainSimplified();
  
  console.log();
  console.log('=== 測試結果 ===');
  
  if (pythonPath && scriptPath && mainExists) {
    console.log('[成功] 所有路徑和文件都正確');
    return true;
  } else {
    console.log('[失敗] 部分路徑或文件有問題');
    return false;
  }
}

// 執行測試
const success = main();
process.exit(success ? 0 : 1);