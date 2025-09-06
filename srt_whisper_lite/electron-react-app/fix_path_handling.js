/**
 * 修復路徑處理問題 - 統一路徑格式
 */

const fs = require('fs');
const path = require('path');

// 讀取 main.js
const mainJsPath = path.join(__dirname, 'main.js');
let mainJsContent = fs.readFileSync(mainJsPath, 'utf8');

// 修復1：確保路徑使用正確的分隔符
const pathFix1 = `
// 路徑標準化函數
function normalizePath(p) {
  // 統一使用正斜線，避免 JSON 轉義問題
  return p.replace(/\\\\/g, '/');
}

// 安全的路徑構建函數
function safePath(...parts) {
  // 使用 path.join 構建，然後標準化
  return normalizePath(path.join(...parts));
}
`;

// 修復2：更新打包環境的路徑處理
const pathFix2 = `
      if (isPackaged) {
        // 打包版本：使用相對於 app.asar 的路徑
        const appDirectory = path.dirname(app.getAppPath());
        
        // 使用相對路徑概念，但構建為絕對路徑
        command = safePath(appDirectory, 'resources', 'mini_python', 'python.exe');
        pythonScript = safePath(appDirectory, 'resources', 'python', 'electron_backend.py');
        workingDir = safePath(appDirectory, 'resources', 'python');
        
        // 為 Windows 添加引號處理空格
        if (process.platform === 'win32') {
          // 如果路徑包含空格，需要加引號
          if (command.includes(' ')) {
            command = \`"\${command}"\`;
          }
        }
`;

// 修復3：更新參數傳遞，確保路徑格式正確
const pathFix3 = `
        // 構建參數時，確保文件路徑格式正確
        args = [
          pythonScript,
          '--files', JSON.stringify(files.map(f => {
            // 統一使用正斜線
            return normalizePath(f.path || f);
          })),
          '--settings', JSON.stringify(settings),
          '--corrections', JSON.stringify(corrections || [])
        ];
`;

// 創建完整的修復版 main.js
const fixedMainJs = `
const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

${pathFix1}

// ... 其餘代碼保持不變，但在處理路徑的地方使用 safePath 和 normalizePath
`;

// 創建補丁文件
const patchContent = `
// ===== 路徑處理修復補丁 =====
// 請將以下函數添加到 main.js 的開頭部分

${pathFix1}

// 然後替換打包環境的路徑處理部分：
${pathFix2}

// 以及參數構建部分：
${pathFix3}

// ===== 補丁結束 =====
`;

fs.writeFileSync(
  path.join(__dirname, 'path_fix.patch'),
  patchContent,
  'utf8'
);

// 創建測試腳本
const testScript = `
const path = require('path');

// 測試路徑處理
function testPaths() {
  const testCases = [
    'C:\\\\Program Files\\\\MyApp\\\\resources',
    'C:/Program Files/MyApp/resources',
    '/usr/local/bin/app',
    './relative/path',
    '../parent/path'
  ];
  
  console.log('路徑處理測試：');
  testCases.forEach(p => {
    console.log(\`原始: \${p}\`);
    console.log(\`標準化: \${p.replace(/\\\\\\\\/g, '/')}\`);
    console.log(\`path.join: \${path.join(p, 'test.py')}\`);
    console.log('---');
  });
}

testPaths();
`;

fs.writeFileSync(
  path.join(__dirname, 'test_paths.js'),
  testScript,
  'utf8'
);

console.log('✅ 路徑處理修復方案已創建！');
console.log('\n📝 已創建文件：');
console.log('  - path_fix.patch (修復補丁)');
console.log('  - test_paths.js (路徑測試腳本)');
console.log('\n⚠️  重要：');
console.log('  應用使用動態構建的絕對路徑，而不是硬編碼的相對路徑');
console.log('  這樣可以確保在任何安裝位置都能正常工作');
console.log('\n💡 下一步：');
console.log('  1. 應用 path_fix.patch 到 main.js');
console.log('  2. 執行 node test_paths.js 測試路徑處理');
console.log('  3. 重新打包應用程式');