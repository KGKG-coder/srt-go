/**
 * 測試Python環境修復
 */

const { setupPythonEnvironment, validatePythonEnvironment, spawnEnhancedPython } = require('./fix_python_environment.js')
const path = require('path')

async function testPythonFix() {
  console.log('=== 測試Python環境修復 ===')
  
  // 設定路徑
  const pythonExePath = path.resolve('dist/SRT-GO-Enhanced-v2.0-Complete/resources/mini_python/python.exe')
  const workingDir = path.resolve('dist/SRT-GO-Enhanced-v2.0-Complete/resources/python')
  
  console.log('Python路徑:', pythonExePath)
  console.log('工作目錄:', workingDir)
  
  // 步驟1: 設定環境變數
  console.log('\n步驟1: 設定Python環境變數...')
  const envConfig = setupPythonEnvironment(pythonExePath, '', workingDir)
  
  // 步驟2: 驗證環境
  console.log('\n步驟2: 驗證Python環境...')
  const isValid = await validatePythonEnvironment(pythonExePath, envConfig)
  
  if (isValid) {
    console.log('\n✅ Python環境修復成功！')
    
    // 步驟3: 測試實際字幕處理
    console.log('\n步驟3: 測試實際electron_backend.py...')
    testElectronBackend(pythonExePath, workingDir, envConfig)
  } else {
    console.log('\n❌ Python環境修復失敗')
  }
}

function testElectronBackend(pythonExePath, workingDir, envConfig) {
  const args = [
    'electron_backend.py',
    '--help'
  ]
  
  const process = spawnEnhancedPython(pythonExePath, args, {
    cwd: workingDir,
    env: envConfig
  })
  
  let output = ''
  let error = ''
  
  process.stdout.on('data', (data) => {
    const text = data.toString()
    output += text
    console.log('📤', text.trim())
  })
  
  process.stderr.on('data', (data) => {
    const text = data.toString()
    error += text
    console.log('📤', text.trim())
  })
  
  process.on('close', (code) => {
    console.log(`\n🏁 electron_backend.py測試完成 (exit code: ${code})`)
    if (code === 0) {
      console.log('✅ electron_backend.py運行成功！')
    } else {
      console.log('❌ electron_backend.py運行失敗')
      console.log('Error output:', error)
    }
  })
  
  process.on('error', (err) => {
    console.error('❌ Python進程啟動錯誤:', err.message)
  })
}

// 執行測試
testPythonFix().catch(console.error)