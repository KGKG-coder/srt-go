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

function safePath(...parts) {
  return normalizePath(path.join(...parts));
}

// 配置存儲
const store = new Store()

// 全局變量
let mainWindow
let pythonEngineProcess
let engineInitialized = false

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
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false,
    backgroundColor: '#FFFFFF',
    icon: path.join(__dirname, 'icon.png'),
    webSecurity: false,
    paintWhenInitiallyHidden: false
  })

  // 窗口載入完成後顯示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    mainWindow.focus()
    
    if (isDev && process.env.NODE_ENV !== 'production') {
      mainWindow.webContents.openDevTools()
    }

    // 初始化 Python AI 引擎
    initializePythonEngine()
  })

  const startUrl = `file://${path.join(__dirname, './react-app/build/index.html')}`
  
  console.log('Loading URL:', startUrl)
  mainWindow.loadURL(startUrl)
  
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Main window loaded successfully')
    mainWindow.show()
    mainWindow.focus()
  })
  
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load main window:', errorCode, errorDescription)
  })

  mainWindow.on('closed', () => {
    mainWindow = null
    // 清理 Python 引擎進程
    if (pythonEngineProcess) {
      pythonEngineProcess.kill()
      pythonEngineProcess = null
    }
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  return mainWindow
}

// 初始化 Python AI 引擎
async function initializePythonEngine() {
  try {
    console.log('🚀 初始化 Python AI 引擎...')
    
    // 確定 Python 引擎路徑
    const enginePath = getPythonEnginePath()
    
    if (!fs.existsSync(enginePath)) {
      throw new Error(`找不到 Python AI 引擎: ${enginePath}`)
    }
    
    console.log('✅ Python AI 引擎路徑確認:', enginePath)
    
    // 測試引擎
    const testResult = await testPythonEngine(enginePath)
    if (!testResult.success) {
      throw new Error(`Python AI 引擎測試失敗: ${testResult.error}`)
    }
    
    engineInitialized = true
    console.log('✅ Python AI 引擎初始化完成')
    
    // 通知前端引擎就緒
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('engine-status', {
        initialized: true,
        message: 'AI 引擎就緒'
      })
    }
    
  } catch (error) {
    console.error('❌ Python AI 引擎初始化失敗:', error)
    engineInitialized = false
    
    // 通知前端引擎錯誤
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('engine-status', {
        initialized: false,
        error: error.message
      })
    }
    
    // 顯示錯誤對話框
    dialog.showErrorBox(
      'AI 引擎初始化失敗',
      `無法啟動 AI 處理引擎:\\n${error.message}\\n\\n請嘗試重新啟動應用程式。`
    )
  }
}

// 獲取 Python 引擎路徑
function getPythonEnginePath() {
  if (isDev) {
    // 開發環境
    return path.join(__dirname, '..', 'dist', 'srt_engine.exe')
  } else {
    // 生產環境
    const isPackaged = app.isPackaged
    if (isPackaged) {
      const appDirectory = path.dirname(process.execPath)
      return safePath(appDirectory, 'resources', 'python_engine', 'srt_engine.exe')
    } else {
      return path.join(__dirname, '..', 'dist', 'srt_engine.exe')
    }
  }
}

// 測試 Python 引擎
function testPythonEngine(enginePath) {
  return new Promise((resolve) => {
    console.log('🧪 測試 Python AI 引擎...')
    
    const testProcess = spawn(enginePath, ['--test'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: false
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
      if (code === 0) {
        console.log('✅ Python AI 引擎測試通過')
        resolve({ success: true, output })
      } else {
        console.error('❌ Python AI 引擎測試失敗:', error)
        resolve({ success: false, error: error || 'Unknown error' })
      }
    })
    
    testProcess.on('error', (err) => {
      console.error('❌ 無法啟動 Python AI 引擎:', err)
      resolve({ success: false, error: err.message })
    })
    
    // 設置超時
    setTimeout(() => {
      if (!testProcess.killed) {
        testProcess.kill()
        resolve({ success: false, error: 'Test timeout' })
      }
    }, 30000)
  })
}

// 調用 Python 引擎處理檔案
function callPythonEngine(config) {
  return new Promise((resolve, reject) => {
    if (!engineInitialized) {
      reject(new Error('AI 引擎未初始化'))
      return
    }
    
    const enginePath = getPythonEnginePath()
    const configJson = JSON.stringify(config)
    
    console.log('🎯 調用 Python AI 引擎處理檔案...')
    console.log('配置:', config)
    
    const processArgs = ['--process', configJson]
    if (config.settings?.enable_gpu !== false) {
      processArgs.push('--enable-gpu')
    }
    
    pythonEngineProcess = spawn(enginePath, processArgs, {
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: false
    })
    
    let output = ''
    let hasCompleted = false
    
    // 處理 stdout
    pythonEngineProcess.stdout.on('data', (data) => {
      const dataStr = data.toString('utf8')
      output += dataStr
      console.log('Python Engine Output:', dataStr)
      
      // 解析輸出
      const lines = dataStr.split('\\n')
      lines.forEach(line => {
        if (line.includes('PROGRESS:')) {
          try {
            const progressData = JSON.parse(line.replace('PROGRESS:', '').trim())
            mainWindow.webContents.send('processing-progress', progressData)
          } catch (e) {
            console.log('Progress parse error:', e)
          }
        } else if (line.includes('COMPLETE:')) {
          try {
            const completeData = JSON.parse(line.replace('COMPLETE:', '').trim())
            console.log('Processing complete:', completeData)
            mainWindow.webContents.send('processing-complete', completeData)
            hasCompleted = true
            resolve(completeData)
          } catch (e) {
            console.log('Complete parse error:', e)
          }
        } else if (line.includes('ERROR:')) {
          try {
            const errorData = JSON.parse(line.replace('ERROR:', '').trim())
            console.log('Processing error:', errorData)
            mainWindow.webContents.send('processing-error', errorData)
            hasCompleted = true
            reject(new Error(errorData.error || 'Processing failed'))
          } catch (e) {
            console.log('Error parse error:', e)
          }
        }
      })
    })
    
    // 處理 stderr
    pythonEngineProcess.stderr.on('data', (data) => {
      const errorStr = data.toString('utf8')
      console.log('Python Engine Error:', errorStr)
    })
    
    // 處理進程錯誤
    pythonEngineProcess.on('error', (err) => {
      console.error('Python Engine Process Error:', err)
      if (!hasCompleted) {
        mainWindow.webContents.send('processing-error', {
          success: false,
          message: `AI 引擎錯誤: ${err.message}`
        })
        reject(err)
      }
    })
    
    // 處理進程關閉
    pythonEngineProcess.on('close', (code) => {
      console.log('Python Engine Process closed with code:', code)
      
      if (!hasCompleted) {
        if (code === 0) {
          resolve({ success: true, output })
        } else {
          reject(new Error(`AI 引擎異常退出 (code: ${code})`))
        }
      }
      
      pythonEngineProcess = null
    })
    
    // 設置處理超時 (30分鐘)
    setTimeout(() => {
      if (pythonEngineProcess && !hasCompleted) {
        console.error('Processing timeout - killing Python engine')
        pythonEngineProcess.kill()
        reject(new Error('處理超時'))
      }
    }, 30 * 60 * 1000)
  })
}

// 應用事件處理
app.whenReady().then(() => {
  console.log('SRT GO 雙層架構應用啟動...')
  
  createWindow()
  Menu.setApplicationMenu(null)
  
  console.log('SRT GO Dual Architecture ready!')
})

app.on('window-all-closed', () => {
  if (pythonEngineProcess) {
    pythonEngineProcess.kill()
  }
  
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('before-quit', () => {
  if (pythonEngineProcess) {
    pythonEngineProcess.kill()
  }
})

// IPC 處理
ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

ipcMain.handle('get-user-data-path', () => {
  return app.getPath('userData')
})

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options)
  return result
})

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options)
  return result
})

ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options)
  return result
})

// 存儲配置
ipcMain.handle('store-get', (event, key) => {
  return store.get(key)
})

ipcMain.handle('store-set', (event, key, value) => {
  return store.set(key, value)
})

ipcMain.handle('store-delete', (event, key) => {
  return store.delete(key)
})

// 檔案選擇
ipcMain.handle('select-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '選擇音頻或視頻文件',
    filters: [
      { name: '所有支援格式', extensions: ['mp4', 'avi', 'mov', 'mkv', 'webm', 'mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg'] },
      { name: '視頻文件', extensions: ['mp4', 'avi', 'mov', 'mkv', 'webm'] },
      { name: '音頻文件', extensions: ['mp3', 'wav', 'm4a', 'flac', 'aac', 'ogg'] },
      { name: '所有文件', extensions: ['*'] }
    ],
    properties: ['openFile', 'multiSelections']
  })
  
  return result.canceled ? [] : result.filePaths
})

// 選擇輸出目錄
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: '選擇字幕輸出目錄',
    properties: ['openDirectory']
  })
  
  return result.canceled ? null : result.filePaths[0]
})

// 主要的檔案處理 IPC - 使用雙層架構
ipcMain.handle('process-files', async (event, options) => {
  console.log('=== 雙層架構檔案處理開始 ===')
  
  try {
    // 驗證輸入
    if (!options || !options.files || !options.settings) {
      throw new Error('無效的處理選項')
    }
    
    // 調用 Python AI 引擎
    const result = await callPythonEngine(options)
    
    console.log('=== 雙層架構檔案處理完成 ===')
    return { success: true, result }
    
  } catch (error) {
    console.error('=== 雙層架構檔案處理失敗 ===', error)
    
    // 發送錯誤到前端
    const errorInfo = {
      success: false,
      message: error.message || '處理失敗',
      timestamp: new Date().toISOString()
    }
    
    mainWindow.webContents.send('processing-error', errorInfo)
    return errorInfo
  }
})

// 引擎狀態檢查
ipcMain.handle('get-engine-status', () => {
  return {
    initialized: engineInitialized,
    enginePath: getPythonEnginePath(),
    engineExists: fs.existsSync(getPythonEnginePath())
  }
})

// 處理未捕獲的異常
process.on('uncaughtException', (error) => {
  console.error('未捕獲的異常:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('未處理的 Promise 拒絕:', reason)
})