const { contextBridge, ipcRenderer } = require('electron')

// 向渲染進程暴露安全的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 應用信息
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
  
  // 對話框
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  
  // 文件操作
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  
  // 字幕處理
  processFiles: (options) => ipcRenderer.invoke('process-files', options),
  pauseProcessing: () => ipcRenderer.invoke('pause-processing'),
  
  // 進度監聽
  onProgress: (callback) => {
    ipcRenderer.on('processing-progress', (event, data) => callback(data))
  },
  
  onComplete: (callback) => {
    ipcRenderer.on('processing-complete', (event, data) => callback(data))
  },
  
  onError: (callback) => {
    ipcRenderer.on('processing-error', (event, data) => callback(data))
  },

  // 環境安裝進度監聽
  onInstallationProgress: (callback) => {
    ipcRenderer.on('installation-progress', (event, data) => callback(data))
  },
  
  removeProgressListeners: () => {
    ipcRenderer.removeAllListeners('processing-progress')
    ipcRenderer.removeAllListeners('processing-complete')
    ipcRenderer.removeAllListeners('processing-error')
  },
  
  // 數據存儲
  store: {
    get: (key) => ipcRenderer.invoke('store-get', key),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value),
    delete: (key) => ipcRenderer.invoke('store-delete', key)
  },
  
  // 平台信息
  platform: process.platform,
  
  // 版本信息
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  }
})

// 全局錯誤處理
window.addEventListener('error', (event) => {
  console.error('渲染進程錯誤:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('未處理的 Promise 拒絕:', event.reason)
})

// 性能監控
if (process.env.NODE_ENV === 'development') {
  window.addEventListener('load', () => {
    const perfData = performance.getEntriesByType('navigation')[0]
    console.log('頁面載入性能:', {
      總時間: `${perfData.loadEventEnd - perfData.fetchStart}ms`,
      DOM解析: `${perfData.domComplete - perfData.domLoading}ms`
    })
  })
}