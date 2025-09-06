const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron')
const { spawn, execSync } = require('child_process')
const path = require('path')
const fs = require('fs')
const os = require('os')
const isDev = process.env.NODE_ENV === 'development'
const Store = require('electron-store')
const EnvironmentManager = require('./environment-manager')

// 增強版模組管理器
class EnhancedProcessingManager {
  constructor() {
    this.processingInstances = new Map()
    this.activeProcesses = new Map()
    this.systemInfo = this.getSystemInfo()
    this.config = {
      maxConcurrentProcesses: this.calculateOptimalConcurrency(),
      preferEnhancedBackend: true,
      cachingEnabled: true,
      resourceMonitoring: true
    }
    
    console.log('Enhanced Processing Manager initialized')
    console.log('System Info:', this.systemInfo)
    console.log('Configuration:', this.config)
  }
  
  getSystemInfo() {
    try {
      return {
        platform: os.platform(),
        arch: os.arch(),
        cpus: os.cpus().length,
        totalMemory: Math.round(os.totalmem() / 1024 / 1024 / 1024), // GB
        freeMemory: Math.round(os.freemem() / 1024 / 1024 / 1024), // GB
        nodeVersion: process.version,
        electronVersion: process.versions.electron,
        chromeVersion: process.versions.chrome
      }
    } catch (error) {
      console.error('Failed to get system info:', error)
      return { error: error.message }
    }
  }
  
  calculateOptimalConcurrency() {
    const cpuCount = os.cpus().length
    const memoryGB = os.totalmem() / 1024 / 1024 / 1024
    
    // 基於系統資源計算最佳並發數
    if (memoryGB >= 16 && cpuCount >= 8) {
      return Math.min(4, cpuCount)
    } else if (memoryGB >= 8 && cpuCount >= 4) {
      return Math.min(2, cpuCount)
    } else {
      return 1
    }
  }
  
  async selectBackend(options = {}) {
    const { files = [], settings = {}, preferEnhanced = true } = options
    
    try {
      // 檢查增強版後端是否可用
      if (preferEnhanced && this.config.preferEnhancedBackend) {
        const enhancedBackendPath = this.getEnhancedBackendPath()
        if (fs.existsSync(enhancedBackendPath)) {
          console.log('✅ Using Enhanced Backend')
          return {
            type: 'enhanced',
            path: enhancedBackendPath,
            features: ['unified_model_manager', 'advanced_cache', 'resource_monitoring']
          }
        }
      }
      
      // 降級到標準後端
      const standardBackendPath = this.getStandardBackendPath()
      if (fs.existsSync(standardBackendPath)) {
        console.log('⚠️ Falling back to Standard Backend')
        return {
          type: 'standard',
          path: standardBackendPath,
          features: ['basic_processing']
        }
      }
      
      throw new Error('No backend available')
      
    } catch (error) {
      console.error('Backend selection failed:', error)
      throw error
    }
  }
  
  getEnhancedBackendPath() {
    const isPackaged = app.isPackaged
    
    if (isPackaged) {
      const appDirectory = path.dirname(process.execPath)
      return safePath(appDirectory, 'resources', 'python', 'enhanced_electron_backend.py')
    } else {
      return safePath(__dirname, '..', 'dist', 'win-unpacked', 'resources', 'python', 'enhanced_electron_backend.py')
    }
  }
  
  getStandardBackendPath() {
    const isPackaged = app.isPackaged
    
    if (isPackaged) {
      const appDirectory = path.dirname(process.execPath)
      return safePath(appDirectory, 'resources', 'python', 'electron_backend.py')
    } else {
      return safePath(__dirname, '..', 'electron_backend.py')
    }
  }
  
  getPythonExecutablePath() {
    const isPackaged = app.isPackaged
    
    if (isPackaged) {
      const appDirectory = path.dirname(process.execPath)
      return safePath(appDirectory, 'resources', 'mini_python', 'python.exe')
    } else {
      const pythonPath = safePath(__dirname, '..', 'mini_python', 'python.exe')
      return fs.existsSync(pythonPath) ? pythonPath : 'python'
    }
  }
  
  async createProcessingSession(sessionId, options) {
    try {
      // 選擇後端
      const backend = await this.selectBackend(options)
      
      // 獲取Python執行檔路徑
      const pythonExecutable = this.getPythonExecutablePath()
      
      // 設置工作目錄
      const workingDirectory = path.dirname(backend.path)
      
      // 創建處理會話
      const session = {
        id: sessionId,
        backend: backend,
        pythonExecutable: pythonExecutable,
        workingDirectory: workingDirectory,
        options: options,
        status: 'ready',
        startTime: null,
        endTime: null,
        progress: 0,
        currentFile: null,
        results: [],
        errors: []
      }
      
      this.processingInstances.set(sessionId, session)
      
      console.log(`Processing session created: ${sessionId}`)
      console.log(`Using backend: ${backend.type} (${backend.path})`)
      console.log(`Python executable: ${pythonExecutable}`)
      console.log(`Working directory: ${workingDirectory}`)
      
      return session
      
    } catch (error) {
      console.error(`Failed to create processing session ${sessionId}:`, error)
      throw error
    }
  }
  
  async startProcessing(sessionId) {
    const session = this.processingInstances.get(sessionId)
    if (!session) {
      throw new Error(`Session ${sessionId} not found`)
    }
    
    try {
      session.status = 'starting'
      session.startTime = Date.now()
      
      // 構建命令參數
      const args = this.buildCommandArgs(session)
      
      // 驗證路徑存在性
      await this.validatePaths(session)
      
      // 啟動Python進程
      const process = spawn(session.pythonExecutable, args, {
        cwd: session.workingDirectory,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: false,
        encoding: 'utf8',
        shell: false
      })
      
      // 設置進程處理器
      this.setupProcessHandlers(sessionId, process)
      
      // 記錄活動進程
      this.activeProcesses.set(sessionId, process)
      session.status = 'running'
      
      console.log(`Processing started for session ${sessionId}`)
      
      return {
        success: true,
        sessionId: sessionId,
        backend: session.backend.type,
        pid: process.pid
      }
      
    } catch (error) {
      session.status = 'error'
      session.errors.push(error.message)
      console.error(`Failed to start processing for session ${sessionId}:`, error)
      throw error
    }
  }
  
  buildCommandArgs(session) {
    const { options } = session
    const { files, settings, corrections } = options
    
    return [
      session.backend.path,
      '--files', JSON.stringify(files.map(f => normalizePath(f.path || f))),
      '--settings', JSON.stringify(settings),
      '--corrections', JSON.stringify(corrections || [])
    ]
  }
  
  async validatePaths(session) {
    const pathsToCheck = [
      { name: 'Python executable', path: session.pythonExecutable },
      { name: 'Backend script', path: session.backend.path },
      { name: 'Working directory', path: session.workingDirectory }
    ]
    
    for (const { name, path } of pathsToCheck) {
      if (!fs.existsSync(path)) {
        throw new Error(`${name} not found: ${path}`)
      }
    }
    
    // 測試Python環境
    try {
      const testCmd = `"${session.pythonExecutable}" -c "import sys; print('Python', sys.version)"`
      const result = execSync(testCmd, {
        cwd: session.workingDirectory,
        encoding: 'utf8',
        timeout: 5000
      })
      console.log(`Python environment test passed: ${result.trim()}`)
    } catch (error) {
      throw new Error(`Python environment test failed: ${error.message}`)
    }
  }
  
  setupProcessHandlers(sessionId, process) {
    const session = this.processingInstances.get(sessionId)
    
    let outputBuffer = ''
    let errorBuffer = ''
    
    // 設置進程超時（30分鐘）
    const timeout = setTimeout(() => {
      console.log(`Processing timeout for session ${sessionId}`)
      this.stopProcessing(sessionId, 'timeout')
    }, 30 * 60 * 1000)
    
    // 處理標準輸出
    process.stdout.on('data', (data) => {
      const dataStr = data.toString('utf8')
      outputBuffer += dataStr
      
      this.parseProcessOutput(sessionId, dataStr)
    })
    
    // 處理錯誤輸出
    process.stderr.on('data', (data) => {
      const errorStr = data.toString('utf8')
      errorBuffer += errorStr
      
      // 記錄但不立即視為錯誤
      console.log(`Session ${sessionId} stderr:`, errorStr)
    })
    
    // 處理進程錯誤
    process.on('error', (error) => {
      clearTimeout(timeout)
      console.error(`Process error for session ${sessionId}:`, error)
      this.handleProcessError(sessionId, error)
    })
    
    // 處理進程關閉
    process.on('close', (code, signal) => {
      clearTimeout(timeout)
      console.log(`Process closed for session ${sessionId}, code: ${code}, signal: ${signal}`)
      this.handleProcessClose(sessionId, code, signal, outputBuffer, errorBuffer)
    })
  }
  
  parseProcessOutput(sessionId, output) {
    const session = this.processingInstances.get(sessionId)
    if (!session) return
    
    const lines = output.split('\n')
    
    lines.forEach(line => {
      try {
        if (line.includes('PROGRESS:')) {
          const progressData = JSON.parse(line.replace('PROGRESS:', '').trim())
          this.handleProgressUpdate(sessionId, progressData)
        } else if (line.includes('COMPLETE:')) {
          const completeData = JSON.parse(line.replace('COMPLETE:', '').trim())
          this.handleProcessComplete(sessionId, completeData)
        } else if (line.includes('ERROR:')) {
          const errorData = JSON.parse(line.replace('ERROR:', '').trim())
          this.handleProcessError(sessionId, errorData)
        }
      } catch (error) {
        // 忽略解析錯誤，可能是普通日誌輸出
      }
    })
  }
  
  handleProgressUpdate(sessionId, progressData) {
    const session = this.processingInstances.get(sessionId)
    if (!session) return
    
    session.progress = progressData.percent || 0
    session.currentFile = progressData.filename || progressData.message
    
    // 發送到前端
    if (mainWindow) {
      mainWindow.webContents.send('processing-progress', {
        sessionId: sessionId,
        ...progressData
      })
    }
  }
  
  handleProcessComplete(sessionId, completeData) {
    const session = this.processingInstances.get(sessionId)
    if (!session) return
    
    session.status = 'completed'
    session.endTime = Date.now()
    session.results = completeData.results || []
    
    // 清理活動進程
    this.activeProcesses.delete(sessionId)
    
    // 發送到前端
    if (mainWindow) {
      mainWindow.webContents.send('processing-complete', {
        sessionId: sessionId,
        ...completeData,
        processingTime: session.endTime - session.startTime,
        backend: session.backend.type
      })
    }
    
    console.log(`Processing completed for session ${sessionId}`)
  }
  
  handleProcessError(sessionId, error) {
    const session = this.processingInstances.get(sessionId)
    if (!session) return
    
    session.status = 'error'
    session.endTime = Date.now()
    session.errors.push(error)
    
    // 清理活動進程
    this.activeProcesses.delete(sessionId)
    
    // 發送到前端
    if (mainWindow) {
      mainWindow.webContents.send('processing-error', {
        sessionId: sessionId,
        error: error,
        backend: session.backend.type
      })
    }
    
    console.error(`Processing error for session ${sessionId}:`, error)
  }
  
  handleProcessClose(sessionId, code, signal, output, error) {
    const session = this.processingInstances.get(sessionId)
    if (!session) return
    
    if (session.status === 'stopping') {
      // 正常停止
      session.status = 'stopped'
      session.endTime = Date.now()
    } else if (session.status !== 'completed' && session.status !== 'error') {
      // 意外關閉
      session.status = 'error'
      session.endTime = Date.now()
      session.errors.push(`Process closed unexpectedly: code ${code}, signal ${signal}`)
      
      if (mainWindow) {
        mainWindow.webContents.send('processing-error', {
          sessionId: sessionId,
          error: { message: `Process closed unexpectedly: code ${code}` },
          backend: session.backend.type
        })
      }
    }
    
    // 清理活動進程
    this.activeProcesses.delete(sessionId)
    
    console.log(`Session ${sessionId} finalized with status: ${session.status}`)
  }
  
  async stopProcessing(sessionId, reason = 'user_request') {
    const process = this.activeProcesses.get(sessionId)
    const session = this.processingInstances.get(sessionId)
    
    if (!process || !session) {
      return { success: false, message: 'Session not found or not active' }
    }
    
    try {
      session.status = 'stopping'
      
      console.log(`Stopping processing for session ${sessionId}, reason: ${reason}`)
      
      // 嘗試優雅關閉
      process.kill('SIGTERM')
      
      // 設置強制關閉超時
      const forceKillTimeout = setTimeout(() => {
        if (this.activeProcesses.has(sessionId)) {
          console.log(`Force killing process for session ${sessionId}`)
          process.kill('SIGKILL')
        }
      }, 5000)
      
      // 等待進程關閉
      await new Promise((resolve) => {
        const checkClosed = () => {
          if (!this.activeProcesses.has(sessionId)) {
            clearTimeout(forceKillTimeout)
            resolve()
          } else {
            setTimeout(checkClosed, 100)
          }
        }
        checkClosed()
      })
      
      return { success: true, message: 'Processing stopped successfully' }
      
    } catch (error) {
      console.error(`Failed to stop processing for session ${sessionId}:`, error)
      return { success: false, message: error.message }
    }
  }
  
  getSessionStatus(sessionId) {
    const session = this.processingInstances.get(sessionId)
    if (!session) {
      return null
    }
    
    return {
      id: sessionId,
      status: session.status,
      progress: session.progress,
      currentFile: session.currentFile,
      backend: session.backend.type,
      startTime: session.startTime,
      endTime: session.endTime,
      results: session.results,
      errors: session.errors
    }
  }
  
  getAllSessionsStatus() {
    const sessions = []
    
    for (const [sessionId, session] of this.processingInstances) {
      sessions.push(this.getSessionStatus(sessionId))
    }
    
    return {
      sessions: sessions,
      activeCount: this.activeProcesses.size,
      systemInfo: this.systemInfo,
      config: this.config
    }
  }
  
  cleanup() {
    console.log('Cleaning up Enhanced Processing Manager')
    
    // 停止所有活動進程
    for (const [sessionId, process] of this.activeProcesses) {
      try {
        console.log(`Cleaning up session ${sessionId}`)
        process.kill('SIGTERM')
      } catch (error) {
        console.error(`Failed to cleanup session ${sessionId}:`, error)
      }
    }
    
    // 清理實例
    this.processingInstances.clear()
    this.activeProcesses.clear()
  }
}

// 路徑標準化函數
function normalizePath(p) {
  return p.replace(/\\/g, '/')
}

// 安全的路徑構建函數
function safePath(...parts) {
  return normalizePath(path.join(...parts))
}

// 配置存儲
const store = new Store()

// 全局變量
let mainWindow
let environmentManager
let enhancedProcessingManager

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
    
    // 開發模式下打開開發者工具
    if (isDev && process.env.NODE_ENV !== 'production') {
      mainWindow.webContents.openDevTools()
    }

    // 初始化增強版組件
    initializeEnhancedComponents()
  })

  // 載入應用
  const startUrl = `file://${path.join(__dirname, './react-app/build/index.html')}`
  console.log('Loading URL:', startUrl)
  
  mainWindow.loadURL(startUrl)
  
  // 監聽加載事件
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Main window loaded successfully')
    mainWindow.show()
    mainWindow.focus()
  })
  
  // 監聽加載失敗事件
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load main window:', errorCode, errorDescription)
  })

  // 窗口關閉時的處理
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 阻止新窗口打開
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  return mainWindow
}

// 初始化增強版組件
async function initializeEnhancedComponents() {
  try {
    console.log('=== Initializing Enhanced Components ===')
    
    // 初始化環境管理器
    environmentManager = new EnvironmentManager(mainWindow)
    const envCheckResult = await environmentManager.performFirstRunCheck()
    
    if (envCheckResult.cancelled) {
      app.quit()
      return
    }
    
    if (!envCheckResult.environmentReady) {
      dialog.showErrorBox(
        'Environment Setup Failed',
        'Failed to set up the required environment. Please install Python manually and restart the application.'
      )
      app.quit()
      return
    }
    
    console.log('✅ Environment check completed')
    
    // 初始化增強版處理管理器
    enhancedProcessingManager = new EnhancedProcessingManager()
    console.log('✅ Enhanced Processing Manager initialized')
    
    // 發送初始化完成事件到前端
    mainWindow.webContents.send('enhanced-backend-ready', {
      systemInfo: enhancedProcessingManager.systemInfo,
      config: enhancedProcessingManager.config
    })
    
    console.log('=== Enhanced Components Ready ===')
    
  } catch (error) {
    console.error('Enhanced components initialization failed:', error)
    dialog.showErrorBox(
      'Initialization Failed',
      `An error occurred during enhanced component setup: ${error.message}`
    )
    app.quit()
  }
}

// 應用事件處理
app.whenReady().then(() => {
  console.log('Enhanced Electron app starting...')
  
  createWindow()
  Menu.setApplicationMenu(null) // 移除菜單欄
  
  console.log('SRT GO Enhanced ready!')
})

// 所有窗口關閉時退出應用
app.on('window-all-closed', () => {
  if (enhancedProcessingManager) {
    enhancedProcessingManager.cleanup()
  }
  
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// macOS 重新激活應用時創建窗口
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// 應用退出前清理
app.on('before-quit', () => {
  if (enhancedProcessingManager) {
    enhancedProcessingManager.cleanup()
  }
})

// ===== 增強版 IPC 處理 =====

// 基本應用 API
ipcMain.handle('get-app-version', () => app.getVersion())
ipcMain.handle('get-user-data-path', () => app.getPath('userData'))
ipcMain.handle('show-open-dialog', async (event, options) => dialog.showOpenDialog(mainWindow, options))
ipcMain.handle('show-save-dialog', async (event, options) => dialog.showSaveDialog(mainWindow, options))
ipcMain.handle('show-message-box', async (event, options) => dialog.showMessageBox(mainWindow, options))

// 存儲配置
ipcMain.handle('store-get', (event, key) => store.get(key))
ipcMain.handle('store-set', (event, key, value) => store.set(key, value))
ipcMain.handle('store-delete', (event, key) => store.delete(key))

// 文件選擇
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

// ===== 增強版處理 API =====

// 開始處理文件（增強版）
ipcMain.handle('enhanced-process-files', async (event, options) => {
  console.log('=== Enhanced Process Files START ===')
  
  try {
    if (!enhancedProcessingManager) {
      throw new Error('Enhanced Processing Manager not initialized')
    }
    
    // 創建會話ID
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    // 創建處理會話
    const session = await enhancedProcessingManager.createProcessingSession(sessionId, options)
    
    // 開始處理
    const result = await enhancedProcessingManager.startProcessing(sessionId)
    
    console.log('Enhanced processing started:', result)
    return { success: true, sessionId: sessionId, ...result }
    
  } catch (error) {
    console.error('Enhanced processing failed:', error)
    return { success: false, error: error.message }
  }
})

// 停止處理（增強版）
ipcMain.handle('enhanced-stop-processing', async (event, sessionId) => {
  console.log('=== Enhanced Stop Processing ===', sessionId)
  
  try {
    if (!enhancedProcessingManager) {
      throw new Error('Enhanced Processing Manager not initialized')
    }
    
    const result = await enhancedProcessingManager.stopProcessing(sessionId)
    console.log('Enhanced processing stopped:', result)
    return result
    
  } catch (error) {
    console.error('Enhanced stop processing failed:', error)
    return { success: false, error: error.message }
  }
})

// 獲取會話狀態
ipcMain.handle('get-session-status', async (event, sessionId) => {
  try {
    if (!enhancedProcessingManager) {
      return null
    }
    
    return enhancedProcessingManager.getSessionStatus(sessionId)
    
  } catch (error) {
    console.error('Get session status failed:', error)
    return null
  }
})

// 獲取所有會話狀態
ipcMain.handle('get-all-sessions-status', async () => {
  try {
    if (!enhancedProcessingManager) {
      return { sessions: [], activeCount: 0 }
    }
    
    return enhancedProcessingManager.getAllSessionsStatus()
    
  } catch (error) {
    console.error('Get all sessions status failed:', error)
    return { sessions: [], activeCount: 0, error: error.message }
  }
})

// 獲取系統信息
ipcMain.handle('get-system-info', async () => {
  try {
    if (!enhancedProcessingManager) {
      return { error: 'Enhanced Processing Manager not available' }
    }
    
    return enhancedProcessingManager.systemInfo
    
  } catch (error) {
    console.error('Get system info failed:', error)
    return { error: error.message }
  }
})

// ===== 向後兼容的傳統 API =====

// 傳統處理文件（降級支持）
ipcMain.handle('process-files', async (event, options) => {
  console.log('=== Legacy Process Files (Fallback) ===')
  
  try {
    // 如果增強版可用，使用增強版
    if (enhancedProcessingManager) {
      console.log('Redirecting to enhanced processing...')
      return await ipcMain.handle('enhanced-process-files')(event, options)
    }
    
    // 降級到原始實現
    console.log('Using legacy processing implementation...')
    return await legacyProcessFiles(options)
    
  } catch (error) {
    console.error('Legacy process files failed:', error)
    return { success: false, error: error.message }
  }
})

// 傳統停止處理（降級支持）
ipcMain.handle('pause-processing', async () => {
  console.log('=== Legacy Stop Processing (Fallback) ===')
  
  try {
    if (enhancedProcessingManager) {
      // 停止所有活動會話
      const status = enhancedProcessingManager.getAllSessionsStatus()
      const activeSessionIds = status.sessions
        .filter(s => s.status === 'running')
        .map(s => s.id)
      
      for (const sessionId of activeSessionIds) {
        await enhancedProcessingManager.stopProcessing(sessionId)
      }
      
      return { success: true, message: '所有處理已停止' }
    }
    
    // 降級實現
    return { success: true, message: '處理已停止' }
    
  } catch (error) {
    console.error('Legacy pause processing failed:', error)
    return { success: true, message: '處理已停止', warning: error.message }
  }
})

// 傳統處理實現（降級用）
async function legacyProcessFiles(options) {
  // 這裡可以實現原始的處理邏輯作為降級選項
  // 目前暫時返回錯誤，實際應用中可以實現完整的降級邏輯
  throw new Error('Legacy processing not implemented - please use enhanced backend')
}

// 處理未捕獲的異常
process.on('uncaughtException', (error) => {
  console.error('未捕獲的異常:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('未處理的 Promise 拒絕:', reason)
})