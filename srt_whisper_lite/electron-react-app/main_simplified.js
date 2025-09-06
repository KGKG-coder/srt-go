const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')
const isDev = process.env.NODE_ENV === 'development'
const Store = require('electron-store')

// 路徑標準化函數
function normalizePath(p) {
  return p.replace(/\\/g, '/');
}

// 配置存儲
const store = new Store()

// 全局變量
let mainWindow
let pythonProcess

// 創建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false,
    backgroundColor: '#FFFFFF',
    icon: path.join(__dirname, 'icon.png'),
    webSecurity: false
  })

  // 窗口載入完成後顯示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    mainWindow.focus()
    
    if (isDev) {
      mainWindow.webContents.openDevTools()
    }
  })

  // 載入應用
  const startUrl = `file://${path.join(__dirname, './react-app/build/index.html')}`
  console.log('Loading URL:', startUrl)
  mainWindow.loadURL(startUrl)
  
  // 窗口關閉時的處理
  mainWindow.on('closed', () => {
    mainWindow = null
    if (pythonProcess) {
      pythonProcess.kill()
      pythonProcess = null
    }
  })

  return mainWindow
}

// 簡化的 Python 路徑獲取函數 - 優先使用系統 Python
function getEmbeddedPythonPath() {
  // 優先嘗試系統 Python（具備完整 AI 依賴）
  try {
    const { spawn } = require('child_process')
    const systemPython = 'python'
    
    // 測試系統 Python 是否可用
    const testResult = spawn(systemPython, ['--version'], { timeout: 5000 })
    
    console.log('優先使用系統 Python（具備完整 AI 模組）')
    return systemPython
  } catch (error) {
    console.log('系統 Python 不可用，fallback 到嵌入式 Python')
  }
  
  // Fallback 到嵌入式 Python
  const isPackaged = app.isPackaged
  let pythonPath
  
  if (isPackaged) {
    // 生產環境：使用 resources 中的嵌入式 Python
    pythonPath = path.join(process.resourcesPath, 'mini_python', 'python.exe')
  } else {
    // 開發環境：使用相對路徑的嵌入式 Python
    pythonPath = path.join(__dirname, 'mini_python', 'python.exe')
  }
  
  // 驗證路徑存在
  if (!fs.existsSync(pythonPath)) {
    console.error(`嵌入式 Python 不存在: ${pythonPath}`)
    // 嘗試備用路徑
    const alternatePath = path.join(__dirname, '..', 'mini_python', 'python.exe')
    if (fs.existsSync(alternatePath)) {
      pythonPath = alternatePath
      console.log(`使用備用路徑: ${pythonPath}`)
    } else {
      throw new Error('找不到 Python 環境（系統和嵌入式都不可用）')
    }
  }
  
  console.log(`使用嵌入式 Python: ${pythonPath}`)
  return pythonPath
}

// 簡化的 Python 腳本路徑獲取函數
function getPythonScriptPath() {
  const isPackaged = app.isPackaged
  let scriptPath
  
  if (isPackaged) {
    // 生產環境：使用 resources 中的腳本
    scriptPath = path.join(process.resourcesPath, 'python', 'electron_backend_simplified.py')
    
    // 如果簡化版不存在，使用標準版
    if (!fs.existsSync(scriptPath)) {
      scriptPath = path.join(process.resourcesPath, 'python', 'electron_backend.py')
    }
  } else {
    // 開發環境：使用相對路徑的腳本
    scriptPath = path.join(__dirname, 'python', 'electron_backend_simplified.py')
    
    // 如果簡化版不存在，使用標準版
    if (!fs.existsSync(scriptPath)) {
      scriptPath = path.join(__dirname, 'python', 'electron_backend.py')
    }
  }
  
  // 驗證路徑存在
  if (!fs.existsSync(scriptPath)) {
    throw new Error(`Python 腳本不存在: ${scriptPath}`)
  }
  
  console.log(`使用 Python 腳本: ${scriptPath}`)
  return scriptPath
}

// 處理字幕生成請求 - 簡化版
ipcMain.on('process-subtitles', (event, files, settings, corrections) => {
  console.log('=== 簡化版字幕處理開始 ===')
  console.log('文件數量:', files.length)
  console.log('設置:', settings)
  
  try {
    // 獲取固定的嵌入式 Python 路徑
    const pythonPath = getEmbeddedPythonPath()
    const scriptPath = getPythonScriptPath()
    const workingDir = path.dirname(scriptPath)
    
    // 準備參數
    const args = [
      scriptPath,
      '--files', JSON.stringify(files.map(f => normalizePath(f.path))),
      '--settings', JSON.stringify(settings),
      '--corrections', JSON.stringify(corrections || [])
    ]
    
    console.log('Python 路徑:', pythonPath)
    console.log('腳本路徑:', scriptPath)
    console.log('工作目錄:', workingDir)
    
    // 啟動 Python 進程
    pythonProcess = spawn(pythonPath, args, {
      cwd: workingDir,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    })
    
    // 處理輸出
    let outputBuffer = ''
    
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString('utf8')
      outputBuffer += output
      
      // 處理完整的行
      const lines = outputBuffer.split('\n')
      outputBuffer = lines.pop() // 保留最後一個不完整的行
      
      lines.forEach(line => {
        line = line.trim()
        if (!line) return
        
        console.log('Python output:', line)
        
        if (line.startsWith('PROGRESS:')) {
          try {
            const progressData = JSON.parse(line.substring(9))
            event.reply('process-progress', progressData)
          } catch (e) {
            console.error('解析進度數據失敗:', e)
          }
        } else if (line.startsWith('RESULT:')) {
          try {
            const resultData = JSON.parse(line.substring(7))
            event.reply('process-complete', resultData.data)
          } catch (e) {
            console.error('解析結果數據失敗:', e)
          }
        } else if (line.startsWith('ERROR:')) {
          try {
            const errorData = JSON.parse(line.substring(6))
            event.reply('process-error', errorData.data)
          } catch (e) {
            console.error('解析錯誤數據失敗:', e)
            event.reply('process-error', { 
              message: '處理失敗', 
              code: 'PARSE_ERROR' 
            })
          }
        }
      })
    })
    
    pythonProcess.stderr.on('data', (data) => {
      const error = data.toString('utf8')
      console.error('Python error:', error)
      
      // 忽略警告，只處理實際錯誤
      if (!error.includes('WARNING') && !error.includes('UserWarning')) {
        event.reply('process-error', { 
          message: error, 
          code: 'PYTHON_ERROR' 
        })
      }
    })
    
    pythonProcess.on('close', (code) => {
      console.log(`Python 進程退出，代碼: ${code}`)
      pythonProcess = null
      
      if (code !== 0) {
        event.reply('process-error', { 
          message: `處理失敗，退出代碼: ${code}`, 
          code: 'PROCESS_EXIT_ERROR' 
        })
      }
    })
    
    pythonProcess.on('error', (err) => {
      console.error('無法啟動 Python 進程:', err)
      event.reply('process-error', { 
        message: `無法啟動處理進程: ${err.message}`, 
        code: 'SPAWN_ERROR' 
      })
      pythonProcess = null
    })
    
  } catch (error) {
    console.error('處理請求失敗:', error)
    event.reply('process-error', { 
      message: error.message, 
      code: 'SETUP_ERROR' 
    })
  }
})

// 停止處理
ipcMain.on('stop-processing', () => {
  if (pythonProcess) {
    console.log('停止 Python 進程')
    pythonProcess.kill()
    pythonProcess = null
  }
})

// 選擇目錄
ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  })
  return result.canceled ? null : result.filePaths[0]
})

// 獲取設置
ipcMain.handle('get-settings', () => {
  return store.get('settings', {})
})

// 保存設置
ipcMain.handle('save-settings', (event, settings) => {
  store.set('settings', settings)
  return true
})

// 應用準備就緒
app.whenReady().then(() => {
  createWindow()
  
  // macOS 特殊處理
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

// 所有窗口關閉時退出（Windows & Linux）
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (pythonProcess) {
      pythonProcess.kill()
    }
    app.quit()
  }
})

// 應用退出前清理
app.on('before-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }
})

console.log('=== 簡化版 Electron 主進程啟動 ===')
console.log('使用系統 Python 優先策略（具備完整 AI 依賴）')
console.log('Fallback 到嵌入式 Python（基礎功能）')