#!/usr/bin/env node
/**
 * 最終應用程式完整測試腳本
 * 驗證所有路徑配置和功能是否正常
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('=== SRT GO 最終版本測試 ===');
console.log('時間:', new Date().toLocaleString());

// 測試win-unpacked版本
const winUnpackedPath = path.join(__dirname, 'dist', 'win-unpacked');
const exePath = path.join(winUnpackedPath, 'SRT GO - AI 字幕生成工具.exe');

console.log('\n1. 檢查構建輸出:');
console.log('win-unpacked路徑:', winUnpackedPath);
console.log('執行檔存在:', fs.existsSync(exePath) ? '✅' : '❌');

if (fs.existsSync(winUnpackedPath)) {
  console.log('\n2. 檢查資源文件結構:');
  
  const requiredFiles = [
    'resources/mini_python/python.exe',
    'resources/python/electron_backend.py', 
    'resources/python/simplified_subtitle_core.py',
    'resources/python/subtitle_formatter.py',
    'resources/app.asar'
  ];
  
  requiredFiles.forEach(file => {
    const fullPath = path.join(winUnpackedPath, file);
    const exists = fs.existsSync(fullPath);
    console.log(`  ${file}: ${exists ? '✅存在' : '❌缺失'}`);
    
    if (exists && file.endsWith('python.exe')) {
      const stats = fs.statSync(fullPath);
      console.log(`    大小: ${(stats.size / 1024 / 1024).toFixed(1)}MB`);
    }
  });
  
  console.log('\n3. 檢查Python環境:');
  const pythonExe = path.join(winUnpackedPath, 'resources', 'mini_python', 'python.exe');
  
  if (fs.existsSync(pythonExe)) {
    console.log('測試Python版本...');
    
    const pythonTest = spawn(pythonExe, ['--version'], {
      cwd: winUnpackedPath,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let output = '';
    let error = '';
    
    pythonTest.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    pythonTest.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    pythonTest.on('close', (code) => {
      if (code === 0) {
        console.log(`✅ Python版本: ${output.trim() || error.trim()}`);
        
        // 測試electron_backend.py
        console.log('\n4. 測試Python後端腳本:');
        const backendScript = path.join(winUnpackedPath, 'resources', 'python', 'electron_backend.py');
        
        const scriptTest = spawn(pythonExe, [backendScript, '--help'], {
          cwd: path.join(winUnpackedPath, 'resources', 'python'),
          stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let scriptOutput = '';
        let scriptError = '';
        
        scriptTest.stdout.on('data', (data) => {
          scriptOutput += data.toString();
        });
        
        scriptTest.stderr.on('data', (data) => {
          scriptError += data.toString();
        });
        
        scriptTest.on('close', (code) => {
          if (code === 0) {
            console.log('✅ Python後端腳本正常');
            console.log('幫助輸出:', scriptOutput.substring(0, 200) + '...');
          } else {
            console.log('❌ Python後端腳本測試失敗');
            console.log('錯誤:', scriptError);
          }
          
          finishTest();
        });
        
        scriptTest.on('error', (err) => {
          console.log('❌ 無法執行Python腳本:', err.message);
          finishTest();
        });
        
      } else {
        console.log('❌ Python版本測試失敗, exit code:', code);
        console.log('錯誤:', error);
        finishTest();
      }
    });
    
    pythonTest.on('error', (err) => {
      console.log('❌ 無法啟動Python:', err.message);
      finishTest();
    });
    
  } else {
    console.log('❌ Python執行檔不存在');
    finishTest();
  }
} else {
  console.log('❌ win-unpacked目錄不存在，請先執行npm run build');
  finishTest();
}

function finishTest() {
  console.log('\n=== 測試完成 ===');
  
  // 檢查NSIS安裝器
  const installerPath = path.join(__dirname, 'dist', 'SRT GO - AI 字幕生成工具-2.0.0-Setup.exe');
  console.log('\n5. 檢查安裝器:');
  console.log('安裝器存在:', fs.existsSync(installerPath) ? '✅' : '❌');
  
  if (fs.existsSync(installerPath)) {
    const stats = fs.statSync(installerPath);
    console.log(`安裝器大小: ${(stats.size / 1024 / 1024).toFixed(1)}MB`);
  }
  
  console.log('\n📋 測試摘要:');
  console.log('- 如果所有項目都是 ✅，表示應用程式準備就緒');
  console.log('- 如果有 ❌ 項目，請檢查相關配置或重新構建');
  console.log('- 安裝器可以部署到其他電腦進行測試');
}