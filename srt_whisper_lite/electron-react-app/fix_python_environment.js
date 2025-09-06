/**
 * Python環境修復模組 - 解決error code 3221225781
 * 此模組將完全解決Python啟動問題並提供強化的環境變數設定
 */

const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

/**
 * 設定完整的Python執行環境
 * @param {string} pythonExePath - Python執行檔路徑
 * @param {string} pythonScriptPath - Python腳本路徑 
 * @param {string} workingDirectory - 工作目錄
 * @returns {Object} 環境變數配置
 */
function setupPythonEnvironment(pythonExePath, pythonScriptPath, workingDirectory) {
  console.log('🔧 設定增強Python環境...')
  
  // 獲取Python根目錄
  const pythonDir = path.dirname(pythonExePath)
  const pythonLibDir = path.join(pythonDir, 'Lib')
  const pythonSitePackagesDir = path.join(pythonLibDir, 'site-packages')
  
  // 構建PYTHONPATH (包含所有必要路徑)
  const pythonPaths = [
    workingDirectory,           // Python腳本目錄
    pythonLibDir,              // Python標準庫
    pythonSitePackagesDir,     // 第三方套件
    pythonDir,                 // Python根目錄
    path.join(pythonDir, 'DLLs') // Python DLL目錄
  ].filter(p => fs.existsSync(p)) // 只包含存在的路徑
  
  // 構建PATH環境變數
  const currentPath = process.env.PATH || ''
  const enhancedPath = [
    pythonDir,                 // Python執行檔目錄
    path.join(pythonDir, 'Scripts'), // Python腳本目錄
    path.dirname(process.execPath),  // Electron應用目錄
    currentPath
  ].join(path.delimiter)
  
  // 完整的環境變數配置
  const envConfig = {
    ...process.env,
    // Python基本配置
    PYTHONHOME: pythonDir,
    PYTHONPATH: pythonPaths.join(path.delimiter),
    PATH: enhancedPath,
    
    // Python執行選項
    PYTHONIOENCODING: 'utf-8',
    PYTHONUNBUFFERED: '1',
    PYTHONDONTWRITEBYTECODE: '1',
    
    // 確保不使用系統Python
    PYTHONNOUSERSITE: '1',
    PYTHONPLATLIBDIR: pythonLibDir,
    
    // Windows特定設定
    SystemRoot: process.env.SystemRoot,
    TEMP: process.env.TEMP,
    TMP: process.env.TMP,
    
    // CUDA支援(如果需要)
    CUDA_VISIBLE_DEVICES: process.env.CUDA_VISIBLE_DEVICES || '0'
  }
  
  console.log('✅ Python環境變數配置完成:')
  console.log('  PYTHONHOME:', envConfig.PYTHONHOME)
  console.log('  PYTHONPATH:', envConfig.PYTHONPATH.split(path.delimiter).slice(0, 3).join(', ') + '...')
  console.log('  PATH前綴:', envConfig.PATH.split(path.delimiter).slice(0, 3).join(', ') + '...')
  
  return envConfig
}

/**
 * 執行Python環境完整性檢查
 * @param {string} pythonExePath - Python執行檔路徑
 * @param {Object} envConfig - 環境變數配置
 * @returns {Promise<boolean>} 檢查結果
 */
function validatePythonEnvironment(pythonExePath, envConfig) {
  return new Promise((resolve) => {
    console.log('🔍 執行Python環境完整性檢查...')
    
    // 基本Python測試
    const testProcess = spawn(pythonExePath, ['-c', 'import sys; print(f"Python {sys.version}")'], {
      env: envConfig,
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true
    })
    
    let output = ''
    let error = ''
    
    testProcess.stdout.on('data', (data) => {
      output += data.toString()
    })
    
    testProcess.stderr.on('data', (data) => {
      error += data.toString()
    })
    
    testProcess.on('close', (code) => {
      if (code === 0 && output.includes('Python')) {
        console.log('✅ Python基本測試通過:', output.trim())
        
        // 進階模組測試
        testAdvancedModules(pythonExePath, envConfig).then(resolve)
      } else {
        console.error('❌ Python基本測試失敗:')
        console.error('  Exit Code:', code)
        console.error('  Output:', output)
        console.error('  Error:', error)
        resolve(false)
      }
    })
    
    testProcess.on('error', (err) => {
      console.error('❌ Python進程啟動失敗:', err.message)
      resolve(false)
    })
  })
}

/**
 * 測試進階模組載入
 * @param {string} pythonExePath - Python執行檔路徑
 * @param {Object} envConfig - 環境變數配置
 * @returns {Promise<boolean>} 測試結果
 */
function testAdvancedModules(pythonExePath, envConfig) {
  return new Promise((resolve) => {
    const testScript = `
import sys
try:
    import numpy
    print("✅ NumPy載入成功")
except ImportError as e:
    print(f"❌ NumPy載入失敗: {e}")

try:
    import faster_whisper
    print("✅ Faster-Whisper載入成功")
except ImportError as e:
    print(f"❌ Faster-Whisper載入失敗: {e}")

try:
    import torch
    print("✅ PyTorch載入成功")
except ImportError as e:
    print(f"❌ PyTorch載入失敗: {e}")

print("🎯 模組測試完成")
`
    
    const testProcess = spawn(pythonExePath, ['-c', testScript], {
      env: envConfig,
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
      timeout: 30000  // 30秒超時
    })
    
    let output = ''
    
    testProcess.stdout.on('data', (data) => {
      output += data.toString()
    })
    
    testProcess.stderr.on('data', (data) => {
      output += data.toString()
    })
    
    testProcess.on('close', (code) => {
      console.log('📊 進階模組測試結果:')
      output.split('\n').forEach(line => {
        if (line.trim()) console.log('  ', line.trim())
      })
      
      const success = code === 0 && output.includes('✅ NumPy載入成功')
      resolve(success)
    })
    
    testProcess.on('error', (err) => {
      console.error('❌ 進階模組測試失敗:', err.message)
      resolve(false)
    })
  })
}

/**
 * 增強的Python進程啟動器
 * @param {string} pythonExePath - Python執行檔路徑
 * @param {string[]} args - Python參數
 * @param {Object} options - 啟動選項
 * @returns {ChildProcess} Python進程
 */
function spawnEnhancedPython(pythonExePath, args, options = {}) {
  const { cwd, env } = options
  
  // 準備增強的環境變數
  const enhancedEnv = env || setupPythonEnvironment(pythonExePath, args[0], cwd)
  
  // Python啟動參數優化
  const pythonArgs = [
    '-I',  // 隔離模式，避免用戶site-packages干擾
    '-s',  // 不自動導入site模組
    '-B',  // 不生成.pyc文件
    '-u',  // 無緩衝輸出
    ...args
  ]
  
  console.log('🚀 啟動增強Python進程:')
  console.log('  執行檔:', pythonExePath)
  console.log('  參數:', pythonArgs.slice(0, 6).join(' ') + (pythonArgs.length > 6 ? '...' : ''))
  console.log('  工作目錄:', cwd)
  
  return spawn(pythonExePath, pythonArgs, {
    cwd: cwd,
    env: enhancedEnv,
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: false,  // 可以看到Python進程窗口(除錯用)
    shell: false,        // 直接執行，不透過shell
    detached: false      // 與父進程綁定
  })
}

module.exports = {
  setupPythonEnvironment,
  validatePythonEnvironment,
  spawnEnhancedPython
}