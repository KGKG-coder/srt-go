#!/usr/bin/env node
// 環境診斷腳本 - 檢查別台電腦上的錯誤
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('=== 環境診斷腳本 ===');
console.log('當前時間:', new Date().toLocaleString());

// 基本環境信息
console.log('\n1. 基本環境信息:');
console.log('Node.js版本:', process.version);
console.log('作業系統:', process.platform);
console.log('架構:', process.arch);
console.log('當前工作目錄:', process.cwd());
console.log('__dirname:', __dirname);

// 模擬打包狀態檢查
const isPackaged = process.env.NODE_ENV === 'production' || !fs.existsSync(path.join(__dirname, '..', 'package.json'));
console.log('是否為打包狀態:', isPackaged);

// 路徑配置檢查
console.log('\n2. 路徑配置檢查:');

let resourcesPath, pythonExe, pythonScript, workingDir;

if (isPackaged) {
    // 打包版本路徑
    resourcesPath = process.resourcesPath || path.join(__dirname, '..', '..', '..');
    pythonExe = path.join(resourcesPath, 'mini_python', 'python.exe');
    pythonScript = path.join(resourcesPath, 'python', 'electron_backend.py');
    workingDir = path.join(resourcesPath, 'python');
    
    console.log('打包模式路徑:');
    console.log('  resourcesPath:', resourcesPath);
} else {
    // 開發版本路徑
    const devPythonPath = path.join(__dirname, '..', 'mini_python', 'python.exe');
    if (fs.existsSync(devPythonPath)) {
        pythonExe = devPythonPath;
        pythonScript = path.join(__dirname, '..', 'electron_backend.py');
        workingDir = path.join(__dirname, '..');
    } else {
        pythonExe = 'python';
        pythonScript = path.join(__dirname, '..', 'electron_backend.py');
        workingDir = path.join(__dirname, '..');
    }
    
    console.log('開發模式路徑:');
}

console.log('  Python執行檔:', pythonExe);
console.log('  Python腳本:', pythonScript);
console.log('  工作目錄:', workingDir);

// 文件存在性檢查
console.log('\n3. 文件存在性檢查:');

const files = [
    { name: 'Python執行檔', path: pythonExe },
    { name: 'Python腳本', path: pythonScript },
    { name: '工作目錄', path: workingDir },
];

if (isPackaged) {
    files.push(
        { name: 'simplified_subtitle_core.py', path: path.join(workingDir, 'simplified_subtitle_core.py') },
        { name: 'subtitle_formatter.py', path: path.join(workingDir, 'subtitle_formatter.py') },
        { name: 'mini_python目錄', path: path.join(resourcesPath, 'mini_python') }
    );
}

files.forEach(file => {
    const exists = fs.existsSync(file.path);
    console.log(`  ${file.name}: ${exists ? '✓ 存在' : '✗ 不存在'} (${file.path})`);
    
    if (exists && file.name.includes('目錄')) {
        try {
            const contents = fs.readdirSync(file.path);
            console.log(`    內容: ${contents.slice(0, 5).join(', ')}${contents.length > 5 ? '...' : ''}`);
        } catch (e) {
            console.log(`    無法讀取目錄內容: ${e.message}`);
        }
    }
});

// Python環境測試
console.log('\n4. Python環境測試:');

if (fs.existsSync(pythonExe)) {
    console.log('嘗試執行Python版本檢查...');
    
    const testProcess = spawn(pythonExe, ['--version'], {
        cwd: workingDir,
        stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let output = '';
    let error = '';
    
    testProcess.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    testProcess.stderr.on('data', (data) => {
        error += data.toString();
    });
    
    testProcess.on('close', (code) => {
        console.log(`Python版本檢查結果 (exit code: ${code}):`);
        console.log('  stdout:', output.trim() || 'empty');
        console.log('  stderr:', error.trim() || 'empty');
        
        // 測試模組導入
        if (code === 0 && fs.existsSync(pythonScript)) {
            console.log('\n5. 測試Python腳本執行:');
            console.log('嘗試執行electron_backend.py --help...');
            
            const scriptTest = spawn(pythonExe, [pythonScript, '--help'], {
                cwd: workingDir,
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
                console.log(`腳本測試結果 (exit code: ${code}):`);
                console.log('  stdout:', scriptOutput.trim() || 'empty');
                console.log('  stderr:', scriptError.trim() || 'empty');
                
                // 完成診斷
                console.log('\n=== 診斷完成 ===');
                console.log('如果看到錯誤，請將此輸出保存並檢查問題。');
            });
            
            scriptTest.on('error', (err) => {
                console.log('腳本執行錯誤:', err.message);
                console.log('\n=== 診斷完成 ===');
            });
        } else {
            console.log('\n=== 診斷完成 ===');
            console.log('Python版本檢查失敗或腳本文件不存在。');
        }
    });
    
    testProcess.on('error', (err) => {
        console.log('Python執行失敗:', err.message);
        console.log('\n=== 診斷完成 ===');
        console.log('無法啟動Python進程，請檢查Python安裝。');
    });
    
} else {
    console.log('Python執行檔不存在，跳過Python測試。');
    console.log('\n=== 診斷完成 ===');
}