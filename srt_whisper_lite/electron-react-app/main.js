const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron')
const { spawn, execSync } = require('child_process')
const path = require('path')
const fs = require('fs')
const isDev = process.env.NODE_ENV === 'development'
const Store = require('electron-store')
const EnvironmentManager = require('./environment-manager')

// 路徑標準化函數
function normalizePath(p) {
  // 統一使用正斜線，避免 JSON 轉義問題
  return p.replace(/\\/g, '/');
}

// 安全的路徑構建函數
function safePath(...parts) {
  // 使用 path.join 構建，然後標準化
  return normalizePath(path.join(...parts));
}

// 配置存儲
const store = new Store()

// 全局變量
let mainWindow
let pythonProcess
let environmentManager

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
    backgroundColor: '#FFFFFF', // 極簡風格純白背景
    icon: path.join(__dirname, 'icon.png'),
    webSecurity: false, // 減少安全檢查以加快加載
    paintWhenInitiallyHidden: false // 防止隱藏時繪製
  })

  // 窗口載入完成後顯示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    mainWindow.focus()  // 確保窗口獲得焦點
    
    // 開發模式下打開開發者工具
    if (isDev && process.env.NODE_ENV !== 'production') {
      mainWindow.webContents.openDevTools()
    }

    // 初始化環境管理器並進行首次運行檢查
    environmentManager = new EnvironmentManager(mainWindow)
    performEnvironmentCheck()
  })

  // 載入應用 - 直接使用構建後的文件
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

// 創建菜單
function createMenu() {
  const template = [
    {
      label: 'SRT GO',
      submenu: [
        {
          label: '關於 SRT GO',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '關於 SRT GO',
              message: 'SRT GO Minimalist v2.0',
              detail: '極簡風格AI字幕生成工具\n採用Electron + React + Tailwind技術',
              buttons: ['確定']
            })
          }
        },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideothers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: '編輯',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectall' }
      ]
    },
    {
      label: '視圖',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: '窗口',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

// 環境檢查函數
async function performEnvironmentCheck() {
  try {
    const checkResult = await environmentManager.performFirstRunCheck()
    
    if (checkResult.cancelled) {
      app.quit()
      return
    }
    
    if (!checkResult.environmentReady) {
      dialog.showErrorBox(
        'Environment Setup Failed',
        'Failed to set up the required environment. Please install Python manually and restart the application.'
      )
      app.quit()
      return
    }
    
    console.log('Environment check completed:', checkResult)
    
    // 環境準備就緒，初始化 Python 服務
    startPythonService()
    
  } catch (error) {
    console.error('Environment check failed:', error)
    dialog.showErrorBox(
      'Environment Check Failed',
      `An error occurred during environment setup: ${error.message}`
    )
    app.quit()
  }
}

// 啟動Python字幕處理服務
function startPythonService() {
  const pythonScript = path.join(__dirname, '..', 'simplified_subtitle_core.py')
  
  // 不啟動獨立的Python服務，而是通過IPC調用
  console.log('Python service integration ready')
}

// 確保首次運行標記存在
function ensureFirstRunFlag() {
  const flagDir = path.join(app.getPath('userData'), 'runtime')
  const flagPath = path.join(flagDir, 'first-run-complete.flag')
  
  try {
    if (!fs.existsSync(flagDir)) {
      fs.mkdirSync(flagDir, { recursive: true })
    }
    if (!fs.existsSync(flagPath)) {
      fs.writeFileSync(flagPath, new Date().toISOString())
      console.log(`First-run flag created at: ${flagPath}`)
    } else {
      console.log(`First-run flag exists at: ${flagPath}`)
    }
  } catch (error) {
    console.warn('Failed to create first-run flag:', error.message)
  }
}

// 應用事件處理
app.whenReady().then(() => {
  console.log('Electron app starting...')
  
  // 確保首次運行標記存在
  ensureFirstRunFlag()
  
  createWindow()
  // 移除菜單欄 - 創建乾淨的界面
  Menu.setApplicationMenu(null)
  startPythonService()
  
  console.log('SRT GO Minimalist ready!')
})

// 所有窗口關閉時退出應用
app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill()
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
  if (pythonProcess) {
    pythonProcess.kill()
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

// 暫停標誌
let isPaused = false;
let currentProcess = null;

// 停止處理
ipcMain.handle('pause-processing', async () => {
  try {
    console.log('=== 停止處理請求 ===');
    isPaused = true;
    
    if (currentProcess) {
      console.log('終止當前Python進程...');
      
      // 強制終止進程
      currentProcess.kill('SIGTERM');
      
      // 給進程一些時間優雅關閉，如果不行就強制殺掉
      await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (currentProcess) {
            currentProcess.kill('SIGKILL');
          }
          resolve();
        }, 2000);
        
        currentProcess.once('close', () => {
          clearTimeout(timeout);
          resolve();
        });
      });
      
      currentProcess = null;
      console.log('Python進程已終止');
    }
    
    console.log('停止處理完成');
    return { success: true, message: '處理已停止' };
  } catch (error) {
    console.error('停止處理時發生錯誤:', error);
    // 即使出現錯誤，也返回成功，因為功能上已經停止
    return { success: true, message: '處理已停止', warning: error.message };
  }
});

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
      throw new Error(`檔案不存在: ${filePath}`);
    }
  }
  
  return true;
}

// 增強的字幕處理
ipcMain.handle('process-files', async (event, options) => {
  console.log('=== IPC process-files START (Enhanced) ===');
  isPaused = false;
  
  // 🔒 第一步：嚴格驗證輸入
  try {
    validateProcessingOptions(options);
    console.log('✅ 參數驗證通過');
  } catch (validationError) {
    console.error('❌ 參數驗證失敗:', validationError.message);
    mainWindow.webContents.send('processing-error', {
      success: false,
      message: validationError.message
    });
    return { success: false, error: validationError.message };
  }
  
  return new Promise((resolve, reject) => {
    try {
      const { files, settings, corrections } = options
      console.log('Processing files:', files.length)
      console.log('Settings:', settings)

      // 設定路徑和命令
      const isPackaged = app.isPackaged;
      const fs = require('fs');
      let command, pythonScript, workingDir, args;
      
      // 🔧 修復關鍵問題：正確檢測執行環境
      // 當從node_modules/electron/dist執行時，app.isPackaged=false但實際是分發版本
      const isActuallyPackaged = isPackaged || process.execPath.includes('node_modules');
      
      // 🧠 Smart Python Environment Selector
      // 優先級：系統Python (兼容性最佳) > 嵌入式Python (便攜性) > 降級方案
      const smartPythonSelector = () => {
        console.log('=== Smart Python Environment Selection ===');
        
        // 候選Python環境列表
        const pythonCandidates = [];
        
        // 1. 系統Python環境 (最高優先級 - 完整依賴庫)
        // 修正：使用動態路徑而不是硬編碼用戶路徑
        const userProfile = process.env.USERPROFILE || process.env.HOME;
        const systemPaths = [
          "python", // 全域PATH中的Python
          "python3",
          "python.exe",
          path.join(userProfile, "AppData", "Local", "Programs", "Python", "Python313", "python.exe"),
          path.join(userProfile, "AppData", "Local", "Programs", "Python", "Python311", "python.exe"),
          path.join(userProfile, "AppData", "Local", "Programs", "Python", "Python312", "python.exe"),
          "C:\\Python313\\python.exe", // 系統級安裝
          "C:\\Python311\\python.exe",
          "C:\\Python312\\python.exe"
        ];
        
        systemPaths.forEach(pythonPath => {
          try {
            if (pythonPath === "python" || pythonPath === "python3" || pythonPath === "python.exe" || fs.existsSync(pythonPath)) {
              pythonCandidates.push({
                path: pythonPath,
                type: 'system',
                priority: 10,
                name: pythonPath.includes('313') ? 'Python 3.13 (System)' : 
                      pythonPath.includes('311') ? 'Python 3.11 (System)' : 
                      pythonPath.includes('312') ? 'Python 3.12 (System)' :
                      'Python (Global)'
              });
            }
          } catch (error) {
            // 忽略路徑檢查錯誤，繼續下一個
            console.log(`跳過無效Python路徑: ${pythonPath}`);
          }
        });
        
        // 2. 嵌入式Python環境 (降級選項 - 便攜性) - 修正相對路徑
        const embeddedPythonPaths = [];
        
        if (isActuallyPackaged) {
          // 打包模式：相對於執行檔的路徑
          const appDirectory = path.dirname(process.execPath);
          embeddedPythonPaths.push(
            safePath(appDirectory, 'resources', 'resources', 'mini_python', 'python.exe'),
            safePath(appDirectory, 'resources', 'mini_python', 'python.exe'),
            safePath(appDirectory, 'mini_python', 'python.exe')
          );
        } else {
          // 開發模式：相對於腳本目錄的路徑
          embeddedPythonPaths.push(
            safePath(__dirname, 'mini_python', 'python.exe'),
            safePath(__dirname, '..', 'mini_python', 'python.exe'),
            safePath(__dirname, 'resources', 'resources', 'mini_python', 'python.exe')
          );
        }
        
        embeddedPythonPaths.forEach(embeddedPath => {
          try {
            if (fs.existsSync(embeddedPath)) {
              pythonCandidates.push({
                path: embeddedPath,
                type: 'embedded',
                priority: 5,
                name: isActuallyPackaged ? 'Embedded Python 3.11' : 'Embedded Python 3.11 (Dev)'
              });
            }
          } catch (error) {
            console.log(`跳過無效嵌入式Python路徑: ${embeddedPath}`);
          }
        });
        
        // 測試每個候選環境的AI模組可用性
        const testPythonEnvironment = (candidate) => {
          try {
            console.log(`Testing ${candidate.name}: ${candidate.path}`);
            
            // 使用同步執行快速測試
            const { execSync } = require('child_process');
            const testCommand = `"${candidate.path}" -c "import numpy, faster_whisper; print('AI_READY')"`;
            const result = execSync(testCommand, { 
              timeout: 5000, 
              encoding: 'utf8',
              stdio: 'pipe'
            });
            
            if (result.includes('AI_READY')) {
              console.log(`✅ ${candidate.name}: AI modules available`);
              return true;
            }
          } catch (error) {
            console.log(`❌ ${candidate.name}: AI modules missing or incompatible`);
            console.log(`  Error: ${error.message.substring(0, 100)}...`);
          }
          return false;
        };
        
        // 按優先級排序並測試
        pythonCandidates.sort((a, b) => b.priority - a.priority);
        
        console.log('Testing Python environments in priority order:');
        for (const candidate of pythonCandidates) {
          if (testPythonEnvironment(candidate)) {
            console.log(`🎯 Selected: ${candidate.name}`);
            return candidate;
          }
        }
        
        // 如果所有環境都不可用，返回最高優先級的候選者，並啟用降級模式
        console.log('⚠️ No fully compatible Python environment found');
        console.log('🔄 Falling back to best available option with degraded functionality');
        
        if (pythonCandidates.length > 0) {
          const fallback = pythonCandidates[0];
          console.log(`🔧 Fallback: ${fallback.name} (AI functionality may be limited)`);
          return { ...fallback, degraded: true };
        }
        
        // 最終降級：返回null，讓系統使用原有邏輯
        console.log('❌ No Python environment available');
        return null;
      };
      
      // 執行智能Python選擇
      const selectedPython = smartPythonSelector();
      
      console.log('=== 執行環境檢測 ===');
      console.log('app.isPackaged:', isPackaged);
      console.log('process.execPath:', process.execPath);
      console.log('實際打包狀態 (isActuallyPackaged):', isActuallyPackaged);
      console.log('__dirname:', __dirname);
      
      // 🎯 Smart Python Environment Integration
      if (selectedPython) {
        console.log('=== Using Smart Python Selection ===');
        command = selectedPython.path;
        
        // 根據Python類型選擇腳本路徑策略
        if (selectedPython.type === 'system') {
          // 系統Python：使用應用內的腳本
          if (isActuallyPackaged) {
            const appDirectory = path.dirname(process.execPath);
            const enhancedScript = safePath(appDirectory, 'resources', 'resources', 'python', 'enhanced_electron_backend.py');
            const standardScript = safePath(appDirectory, 'resources', 'resources', 'python', 'electron_backend.py');
            pythonScript = fs.existsSync(enhancedScript) ? enhancedScript : standardScript;
            workingDir = safePath(appDirectory, 'resources', 'resources', 'python');
          } else {
            const enhancedScript = safePath(__dirname, 'python', 'enhanced_electron_backend.py');
            const standardScript = safePath(__dirname, 'python', 'electron_backend.py');
            pythonScript = fs.existsSync(enhancedScript) ? enhancedScript : standardScript;
            workingDir = path.dirname(pythonScript);
          }
        } else if (selectedPython.type === 'embedded') {
          // 嵌入式Python：使用相對於Python執行檔的腳本
          const pythonDir = path.dirname(selectedPython.path);
          const resourcesDir = path.join(pythonDir, '..', 'python');
          const enhancedScript = safePath(resourcesDir, 'enhanced_electron_backend.py');
          const standardScript = safePath(resourcesDir, 'electron_backend.py');
          pythonScript = fs.existsSync(enhancedScript) ? enhancedScript : standardScript;
          workingDir = resourcesDir;
        }
        
        console.log('Smart selection results:');
        console.log('  Python executable:', command);
        console.log('  Python script:', pythonScript);
        console.log('  Working directory:', workingDir);
        console.log('  Environment type:', selectedPython.type);
        console.log('  Degraded mode:', selectedPython.degraded || false);
        
        // 如果是降級模式，添加特殊參數
        if (selectedPython.degraded) {
          settings.degradedMode = true;
          console.log('⚠️ Running in degraded mode - some AI features may be limited');
        }
        
        args = [
          pythonScript,
          '--files', JSON.stringify(files.map(f => normalizePath(f.path))),
          '--settings', JSON.stringify(settings),
          '--corrections', JSON.stringify(corrections || [])
        ];
        
      } else {
        // 備用邏輯：當智能選擇失敗時的回退方案
        console.log('=== FALLBACK: Using legacy selection logic ===');
        
        // 🚨 修正：使用動態路徑而非硬編碼路徑
        const userProfile = process.env.USERPROFILE || process.env.HOME;
        const systemPython313 = path.join(userProfile, "AppData", "Local", "Programs", "Python", "Python313", "python.exe");
        const systemPython311 = path.join(userProfile, "AppData", "Local", "Programs", "Python", "Python311", "python.exe");
        
        let forceSystemPython = null;
        if (fs.existsSync(systemPython313)) {
          // 測試 Python 3.13 AI 模組
          try {
            const { execSync } = require('child_process');
            execSync(`"${systemPython313}" -c "import numpy, faster_whisper; print('AI_READY')"`, { timeout: 5000 });
            forceSystemPython = systemPython313;
            console.log('✅ FORCE: Using System Python 3.13 with full AI capabilities');
          } catch (error) {
            console.log('❌ System Python 3.13 AI test failed');
          }
        }
        
        if (!forceSystemPython && fs.existsSync(systemPython311)) {
          // 測試 Python 3.11 AI 模組
          try {
            const { execSync } = require('child_process');
            execSync(`"${systemPython311}" -c "import numpy, faster_whisper; print('AI_READY')"`, { timeout: 5000 });
            forceSystemPython = systemPython311;
            console.log('✅ FORCE: Using System Python 3.11 with AI capabilities');
          } catch (error) {
            console.log('❌ System Python 3.11 AI test failed');
          }
        }
        
        if (forceSystemPython && isActuallyPackaged) {
          // 強制使用系統 Python
          command = forceSystemPython;
          const appDirectory = path.dirname(process.execPath);
          
          const enhancedScript = safePath(appDirectory, 'resources', 'resources', 'python', 'enhanced_electron_backend.py');
          const standardScript = safePath(appDirectory, 'resources', 'resources', 'python', 'electron_backend.py');
          pythonScript = fs.existsSync(enhancedScript) ? enhancedScript : standardScript;
          workingDir = safePath(appDirectory, 'resources', 'resources', 'python');
          
          console.log('FORCED System Python Configuration:');
          console.log('  Python executable:', command);
          console.log('  Python script:', pythonScript);
          console.log('  Working directory:', workingDir);
          
          args = [
            pythonScript,
            '--files', JSON.stringify(files.map(f => normalizePath(f.path))),
            '--settings', JSON.stringify(settings),
            '--corrections', JSON.stringify(corrections || [])
          ];
        } else {
          // 備用：使用嵌入式 Python （但會失敗）
          const appDirectory = path.dirname(process.execPath);
        
          console.log('=== 簡化路徑解析 ===');
        console.log('應用程式根目錄 (appDirectory):', appDirectory);
        console.log('process.resourcesPath:', process.resourcesPath);
        
        // Electron 標準打包結構：
        // [安裝目錄]/
        //   └── SRT GO - AI 字幕生成工具.exe
        //   └── resources/
        //       ├── app.asar
        //       ├── mini_python/python.exe
        //       └── python/electron_backend.py
        
        console.log('應用程式目錄:', appDirectory);
        
        // 使用安全路徑構建，避免路徑問題 - 修正雙層resources結構
        command = safePath(appDirectory, 'resources', 'resources', 'mini_python', 'python.exe');
        
        // 優先嘗試使用增強版後端
        const enhancedScript = safePath(appDirectory, 'resources', 'resources', 'python', 'enhanced_electron_backend.py');
        const standardScript = safePath(appDirectory, 'resources', 'resources', 'python', 'electron_backend.py');
        
        pythonScript = fs.existsSync(enhancedScript) ? enhancedScript : standardScript;
        workingDir = safePath(appDirectory, 'resources', 'resources', 'python');
        
        console.log('選擇的後端腳本:', pythonScript.includes('enhanced') ? '增強版' : '標準版');
        
        // Windows 特殊處理：如果路徑包含空格，需要加引號
        if (process.platform === 'win32' && command.includes(' ')) {
          // 注意：spawn 不需要引號，但記錄用於診斷
          console.log('路徑包含空格，spawn 會自動處理');
        }
        
        console.log('計算的路徑結構:');
        console.log('  Python執行檔:', command);
        console.log('  Python腳本:', pythonScript);
        console.log('  工作目錄:', workingDir);
        
        // 簡單驗證（只記錄，不中斷）
        console.log('路徑存在性檢查:');
        console.log('  Python執行檔:', fs.existsSync(command) ? '✅存在' : '❌不存在');
        console.log('  Python腳本:', fs.existsSync(pythonScript) ? '✅存在' : '❌不存在');
        console.log('  工作目錄:', fs.existsSync(workingDir) ? '✅存在' : '❌不存在');
        
        args = [
          pythonScript,
          '--files', JSON.stringify(files.map(f => normalizePath(f.path))),
          '--settings', JSON.stringify(settings),
          '--corrections', JSON.stringify(corrections || [])
        ];
        }
      }
      
      if (!isActuallyPackaged) {
        // 開發版本：修正路徑解析邏輯
        console.log('=== 開發模式路徑診斷 ===');
        console.log('__dirname:', __dirname);
        console.log('app.getAppPath():', app.getAppPath());
        
        // 嘗試多個可能的mini_python路徑
        const possiblePythonPaths = [
          safePath(__dirname, 'mini_python', 'python.exe'),           // 同目錄下
          safePath(__dirname, '..', 'mini_python', 'python.exe'),     // 上一級目錄 
          safePath(app.getAppPath(), 'mini_python', 'python.exe'),    // app路徑下
          safePath(app.getAppPath(), '..', 'mini_python', 'python.exe') // app上級路徑
        ];
        
        let pythonPath = null;
        for (const testPath of possiblePythonPaths) {
          console.log('Testing Python path:', testPath, '-> exists:', fs.existsSync(testPath));
          if (fs.existsSync(testPath)) {
            pythonPath = testPath;
            break;
          }
        }
        
        if (pythonPath) {
          // 使用找到的 mini_python
          command = pythonPath;
          console.log('✅ 找到mini_python:', command);
          
          // 尋找Python後端腳本
          const basePath = path.dirname(pythonPath);  // mini_python的上級目錄
          const possibleScripts = [
            safePath(basePath, 'python', 'enhanced_electron_backend.py'),
            safePath(basePath, 'python', 'electron_backend.py'),
            safePath(basePath, 'enhanced_electron_backend.py'),
            safePath(basePath, 'electron_backend.py')
          ];
          
          pythonScript = null;
          for (const testScript of possibleScripts) {
            console.log('Testing script path:', testScript, '-> exists:', fs.existsSync(testScript));
            if (fs.existsSync(testScript)) {
              pythonScript = testScript;
              break;
            }
          }
          
          if (!pythonScript) {
            console.error('❌ 無法找到Python後端腳本');
            pythonScript = safePath(basePath, 'python', 'electron_backend.py');  // 使用預設路徑
          }
          
          workingDir = path.dirname(pythonScript);
          
        } else {
          // 最終回退：嘗試系統 Python + 當前目錄腳本
          console.log('❌ mini_python不存在或不可用，回退到系統Python');
          command = 'python';
          
          // 對於打包版本，仍然使用resources目錄的腳本
          const possibleScripts = [
            safePath(__dirname, 'resources', 'resources', 'python', 'electron_backend.py'),  // 打包版本位置
            safePath(__dirname, 'python', 'electron_backend.py'),               // 開發版本位置
            safePath(__dirname, '..', 'python', 'electron_backend.py'),         // 上級目錄
            safePath(__dirname, 'electron_backend.py')                          // 同目錄
          ];
          
          pythonScript = null;
          for (const testScript of possibleScripts) {
            console.log('Testing fallback script path:', testScript, '-> exists:', fs.existsSync(testScript));
            if (fs.existsSync(testScript)) {
              pythonScript = testScript;
              break;
            }
          }
          
          if (!pythonScript) {
            console.error('❌ 無法找到任何Python後端腳本');
            // 根據目錄結構智能選擇預設路徑
            if (fs.existsSync(safePath(__dirname, 'resources'))) {
              pythonScript = safePath(__dirname, 'resources', 'resources', 'python', 'electron_backend.py');
            } else {
              pythonScript = safePath(__dirname, 'python', 'electron_backend.py');
            }
            console.log('Using default script path:', pythonScript);
          }
          
          workingDir = path.dirname(pythonScript);
        }
        
        console.log('開發模式後端腳本:', pythonScript.includes('enhanced') ? '增強版' : '標準版');
        
        console.log('Development mode - Python executable:', command);
        console.log('Python script:', pythonScript);
        console.log('Working directory:', workingDir);
        
        args = [
          pythonScript,
          '--files', JSON.stringify(files.map(f => f.path)),
          '--settings', JSON.stringify(settings),
          '--corrections', JSON.stringify(corrections || [])
        ];
      }
      
      console.log('Command:', command)
      console.log('Working Directory:', workingDir)
      
      // 最終文件存在性檢查（動態路徑解析後）
      
      if (!fs.existsSync(command)) {
        console.error('=== 完整診斷信息 ===');
        console.error('最終檢查失敗 - Python執行檔不存在');
        console.error('選擇的路徑:', command);
        console.error('當前安裝環境信息:');
        console.error('  process.execPath:', process.execPath);
        console.error('  process.resourcesPath:', process.resourcesPath);  
        console.error('  app.getAppPath():', app.getAppPath());
        console.error('  __dirname:', __dirname);
        console.error('  isPackaged:', isPackaged);
        
        // 生成用戶友好的錯誤訊息
        const installPath = path.dirname(process.execPath);
        const errorMsg = `應用程式文件不完整，無法找到 Python 執行環境。\n\n` +
                        `安裝位置: ${installPath}\n` +
                        `預期Python路徑: ${command}\n\n` +
                        `請嘗試：\n` +
                        `1. 重新安裝應用程式\n` +
                        `2. 確保安裝過程完成且未被中斷\n` +
                        `3. 檢查防毒軟體是否阻止了文件安裝`;
                        
        console.error('發送錯誤訊息到前端:', errorMsg);
        mainWindow.webContents.send('processing-error', { success: false, message: errorMsg });
        return reject({ success: false, error: errorMsg });
      }
      
      if (!fs.existsSync(pythonScript)) {
        const installPath = path.dirname(process.execPath);
        const errorMsg = `應用程式文件不完整，無法找到處理腳本。\n\n` +
                        `安裝位置: ${installPath}\n` +
                        `預期腳本路徑: ${pythonScript}\n\n` +
                        `請重新安裝應用程式以修復此問題。`;
                        
        console.error('Python腳本不存在:', pythonScript);
        console.error('發送錯誤訊息到前端:', errorMsg);
        mainWindow.webContents.send('processing-error', { success: false, message: errorMsg });
        return reject({ success: false, error: errorMsg });
      }
      
      // 增強診斷：執行簡單的 Python 檢查
      console.log('\n🔍 執行 Python 環境診斷...');
      try {
        const diagCmd = `"${command}" -c "import sys; print(f'Python {sys.version}')"`;
        const diagResult = execSync(diagCmd, {
          cwd: workingDir,
          encoding: 'utf8',
          timeout: 5000
        });
        console.log('✅ Python 環境正常:', diagResult.trim());
      } catch (diagError) {
        console.error('⚠️ Python 環境診斷失敗:', diagError.message);
        // 不中斷，繼續嘗試執行
      }
      
      // 檢查通過，記錄成功信息
      console.log('\n✅ 所有文件檢查通過，準備啟動Python進程');
      console.log('最終確認的路徑:');
      console.log('  Python執行檔:', command);
      console.log('  Python腳本:', pythonScript); 
      console.log('  工作目錄:', workingDir);
      console.log('  參數:', args.map(arg => arg.length > 100 ? arg.substring(0, 100) + '...' : arg));
      
      // 啟動Python進程
      currentProcess = spawn(command, args, {
        cwd: workingDir,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: false,
        encoding: 'utf8',
        shell: false  // 不使用 shell，直接執行
      })
      
      const subtitleProcess = currentProcess;
      let output = '';
      let error = '';
      let hasCompleted = false;
      let lastProgressTime = Date.now();
      
      // 設置處理超時檢查 (30分鐘)
      const timeoutId = setTimeout(() => {
        if (!hasCompleted && currentProcess) {
          console.error('Processing timeout - killing process');
          mainWindow.webContents.send('processing-error', {
            success: false,
            message: 'Processing timeout - the operation took too long'
          });
          hasCompleted = true;
          currentProcess.kill('SIGTERM');
          reject({ success: false, error: 'Processing timeout' });
        }
      }, 30 * 60 * 1000); // 30分鐘
      
      // 處理stdout輸出
      subtitleProcess.stdout.on('data', (data) => {
        const dataStr = data.toString('utf8');
        output += dataStr;
        console.log('Python stdout:', dataStr);
        
        // 解析進度信息
        const lines = dataStr.split('\n');
        lines.forEach(line => {
          if (line.includes('PROGRESS:')) {
            const progressData = line.replace('PROGRESS:', '').trim()
            try {
              const progress = JSON.parse(progressData)
              console.log('Progress update:', progress)
              lastProgressTime = Date.now() // 更新最後進度時間
              mainWindow.webContents.send('processing-progress', progress)
            } catch (e) {
              console.log('Failed to parse progress:', progressData, e)
            }
          } else if (line.includes('COMPLETE:')) {
            const completeData = line.replace('COMPLETE:', '').trim()
            try {
              const completion = JSON.parse(completeData)
              console.log('Processing complete:', completion)
              console.log('Setting hasCompleted to true')
              mainWindow.webContents.send('processing-complete', completion)
              hasCompleted = true
            } catch (e) {
              console.log('Failed to parse completion:', completeData, e)
            }
          } else if (line.includes('ERROR:')) {
            const errorData = line.replace('ERROR:', '').trim()
            try {
              const errorInfo = JSON.parse(errorData)
              console.log('Processing error from Python:', errorInfo)
              mainWindow.webContents.send('processing-error', errorInfo)
              hasCompleted = true
            } catch (e) {
              console.log('Failed to parse error:', errorData, e)
            }
          } else if (line.trim() && !line.includes('INFO') && !line.includes('WARNING')) {
            // 記錄未預期的輸出
            console.log('Unexpected Python output:', line)
          }
        })
      })
      
      // 處理stderr輸出
      subtitleProcess.stderr.on('data', (data) => {
        const errorStr = data.toString('utf8');
        error += errorStr;
        console.log('Python stderr:', errorStr);
        
        // 不要立即將 stderr 視為錯誤，因為很多 Python 套件會輸出警告到 stderr
        // 只在進程異常退出時才處理
      })
      
      // 處理進程錯誤
      subtitleProcess.on('error', (err) => {
        console.error('Failed to start Python process:', err)
        if (!hasCompleted) {
          mainWindow.webContents.send('processing-error', { 
            success: false, 
            message: `無法啟動Python進程: ${err.message}` 
          })
          hasCompleted = true
          reject({ success: false, error: err.message })
        }
      })
      
      // 處理進程關閉
      subtitleProcess.on('close', (code) => {
        clearTimeout(timeoutId) // 清除超時檢查
        console.log('Python process closed with code:', code)
        console.log('Final output:', output)
        console.log('Final error:', error)
        console.log('Process closed. hasCompleted:', hasCompleted)
        console.log('Is paused:', isPaused)
        
        // 檢查是否因為停止而關閉
        if (isPaused) {
          console.log('Process closed due to stop operation - not sending error')
          if (!hasCompleted) {
            hasCompleted = true
            // 停止時不發送錯誤，直接 resolve
            resolve({ success: false, stopped: true, message: '處理已停止' })
          }
          return
        }
        
        // 只有在沒有發送過完成/錯誤事件時才發送
        if (!hasCompleted) {
          console.log('No completion event sent yet, sending now')
          if (code === 0) {
            mainWindow.webContents.send('processing-complete', { 
              success: true, 
              message: '所有字幕檔案已成功生成' 
            })
            resolve({ success: true, output })
          } else {
            mainWindow.webContents.send('processing-error', { 
              success: false, 
              message: error || '處理過程中發生未知錯誤' 
            })
            reject({ success: false, error })
          }
        } else {
          console.log('Completion event already sent, just resolving')
          // 如果已經發送過事件，只需要 resolve/reject Promise
          if (code === 0) {
            resolve({ success: true, output })
          } else {
            reject({ success: false, error })
          }
        }
      })
      
    } catch (error) {
      console.error('=== IPC process-files ERROR (Enhanced) ===', error);
      
      // 🚨 增強錯誤信息
      let userMessage = '處理失敗';
      if (error.message && error.message.includes('檔案不存在')) {
        userMessage = '選擇的檔案無法存取，請確認檔案路徑正確。';
      } else if (error.code === 'ENOENT') {
        userMessage = 'Python 環境損壞，請重新安裝應用程式。';
      } else if (error.code === 'EACCES') {
        userMessage = '權限不足，請以管理員身份執行程式。';
      } else if (error.message) {
        userMessage = `處理失敗: ${error.message}`;
      }
      
      // 發送結構化錯誤信息
      const errorInfo = {
        success: false,
        message: userMessage,
        code: error.code || 'PROCESSING_ERROR',
        timestamp: new Date().toISOString(),
        originalError: error.message || error.toString()
      };
      
      mainWindow.webContents.send('processing-error', errorInfo);
      reject(errorInfo);
    }
  })
})

// 處理未捕獲的異常
process.on('uncaughtException', (error) => {
  console.error('未捕獲的異常:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('未處理的 Promise 拒絕:', reason)
})