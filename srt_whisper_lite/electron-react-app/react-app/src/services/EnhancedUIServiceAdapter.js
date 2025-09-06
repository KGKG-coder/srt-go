/**
 * 增強版 UI 服務適配器
 * 整合統一模型管理器和進階快取系統
 * 提供高性能的處理服務和智能狀態管理
 */

import { EventEmitter } from 'events';

// Development logging - will be stripped in production
const isDev = process.env.NODE_ENV === 'development';
const devLog = (...args) => isDev && devLog(...args);

class EnhancedUIServiceAdapter extends EventEmitter {
  constructor() {
    super();
    this.initialized = false;
    this.enhancedBackendReady = false;
    this.currentSessionId = null;
    this.lastSystemInfo = null;
    this.pollingInterval = null;
    this.retryCount = 0;
    this.maxRetries = 3;
    
    // 增強版 UI 狀態
    this.enhancedState = {
      backend: 'unknown', // enhanced | standard | legacy
      systemInfo: null,
      sessionStats: {
        totalSessions: 0,
        activeSessions: 0,
        completedSessions: 0,
        failedSessions: 0
      },
      processingQueue: [],
      cacheStats: {
        hitRate: 0,
        totalSize: 0,
        entriesCount: 0
      },
      resourceUsage: {
        cpuUsage: 0,
        memoryUsage: 0,
        availableMemory: 0
      },
      modelInfo: {
        currentModel: 'unknown',
        loadTime: 0,
        availableModels: []
      },
      capabilities: {
        caching: false,
        modelManagement: false,
        resourceMonitoring: false,
        concurrentProcessing: false
      }
    };

    // 傳統狀態（向後兼容）
    this.legacyState = {
      isProcessing: false,
      isPaused: false,
      progress: 0,
      currentFile: '',
      currentFileIndex: 0,
      completedFiles: new Set(),
      error: null
    };

    // 自動初始化
    this.initialize();
  }

  /**
   * 初始化增強版適配器
   */
  async initialize() {
    if (this.initialized) return;

    try {
      devLog('=== Initializing Enhanced UI Service Adapter ===');
      
      // 檢查增強版後端是否可用
      if (window.electronAPI && window.electronAPI.getSystemInfo) {
        await this._initializeEnhancedBackend();
      } else {
        await this._initializeLegacyMode();
      }

      this.initialized = true;
      this.emit('initialized', { 
        enhancedBackendReady: this.enhancedBackendReady,
        backend: this.enhancedState.backend,
        capabilities: this.enhancedState.capabilities
      });

      // 開始狀態監控
      if (this.enhancedBackendReady) {
        this._startStatusMonitoring();
      }

      devLog(`✅ Enhanced UI Service Adapter initialized (${this.enhancedState.backend} mode)`);

    } catch (error) {
      console.error('Enhanced UI Service Adapter initialization failed:', error);
      await this._initializeLegacyMode();
      this.initialized = true;
    }
  }

  /**
   * 初始化增強版後端
   */
  async _initializeEnhancedBackend() {
    try {
      // 獲取系統信息
      const systemInfo = await window.electronAPI.getSystemInfo();
      
      if (systemInfo && !systemInfo.error) {
        this.enhancedBackendReady = true;
        this.enhancedState.backend = 'enhanced';
        this.enhancedState.systemInfo = systemInfo;
        this.lastSystemInfo = systemInfo;
        
        // 檢查可用功能
        await this._checkCapabilities();
        
        // 設置增強版事件監聽
        this._setupEnhancedEventListeners();
        
        devLog('✅ Enhanced backend initialized');
        devLog('System Info:', systemInfo);
        devLog('Capabilities:', this.enhancedState.capabilities);
        
      } else {
        throw new Error('Enhanced backend not available');
      }

    } catch (error) {
      console.warn('Enhanced backend initialization failed:', error);
      this.enhancedBackendReady = false;
      this.enhancedState.backend = 'standard';
      
      // 嘗試標準後端
      await this._initializeStandardBackend();
    }
  }

  /**
   * 初始化標準後端
   */
  async _initializeStandardBackend() {
    try {
      // 檢查標準處理 API
      if (window.electronAPI && window.electronAPI.processFiles) {
        this.enhancedState.backend = 'standard';
        this._setupStandardEventListeners();
        devLog('✅ Standard backend initialized');
      } else {
        throw new Error('Standard backend not available');
      }
    } catch (error) {
      console.warn('Standard backend initialization failed:', error);
      await this._initializeLegacyMode();
    }
  }

  /**
   * 初始化傳統模式
   */
  async _initializeLegacyMode() {
    this.enhancedBackendReady = false;
    this.enhancedState.backend = 'legacy';
    this.enhancedState.capabilities = {
      caching: false,
      modelManagement: false,
      resourceMonitoring: false,
      concurrentProcessing: false
    };
    
    // 設置傳統事件監聽
    this._setupLegacyEventListeners();
    
    devLog('⚠️ Using legacy mode');
  }

  /**
   * 檢查後端能力
   */
  async _checkCapabilities() {
    try {
      const capabilities = {
        caching: false,
        modelManagement: false,
        resourceMonitoring: false,
        concurrentProcessing: false
      };

      // 檢查增強版處理 API
      if (window.electronAPI.enhancedProcessFiles) {
        capabilities.concurrentProcessing = true;
        capabilities.caching = true;
        capabilities.modelManagement = true;
      }

      // 檢查系統監控 API
      if (window.electronAPI.getAllSessionsStatus) {
        capabilities.resourceMonitoring = true;
      }

      this.enhancedState.capabilities = capabilities;

    } catch (error) {
      console.error('Capability check failed:', error);
    }
  }

  /**
   * 設置增強版事件監聽
   */
  _setupEnhancedEventListeners() {
    if (!window.electronAPI) return;

    // 增強版後端就緒事件
    if (window.electronAPI.onEnhancedBackendReady) {
      window.electronAPI.onEnhancedBackendReady((data) => {
        this.enhancedState.systemInfo = data.systemInfo;
        this.enhancedState.capabilities = { ...this.enhancedState.capabilities, ...data.config };
        
        this.emit('backendReady', {
          backend: 'enhanced',
          systemInfo: data.systemInfo,
          config: data.config
        });
      });
    }

    // 處理進度事件（增強版）
    if (window.electronAPI.onProgress) {
      window.electronAPI.onProgress((progress) => {
        this._updateProgressState(progress);
        this.emit('progressUpdate', {
          ...progress,
          enhanced: true,
          sessionId: progress.sessionId || this.currentSessionId
        });
      });
    }

    // 處理完成事件（增強版）
    if (window.electronAPI.onComplete) {
      window.electronAPI.onComplete((result) => {
        this._updateCompletionState(result);
        this.emit('taskCompleted', {
          ...result,
          enhanced: true,
          sessionId: result.sessionId || this.currentSessionId
        });
      });
    }

    // 處理錯誤事件（增強版）
    if (window.electronAPI.onError) {
      window.electronAPI.onError((error) => {
        this._updateErrorState(error);
        this.emit('taskFailed', {
          ...error,
          enhanced: true,
          sessionId: error.sessionId || this.currentSessionId
        });
      });
    }
  }

  /**
   * 設置標準事件監聽
   */
  _setupStandardEventListeners() {
    if (!window.electronAPI) return;

    // 標準進度事件
    if (window.electronAPI.onProgress) {
      window.electronAPI.onProgress((progress) => {
        this._updateProgressState(progress);
        this.emit('progressUpdate', progress);
      });
    }

    // 標準完成事件
    if (window.electronAPI.onComplete) {
      window.electronAPI.onComplete((result) => {
        this._updateCompletionState(result);
        this.emit('taskCompleted', result);
      });
    }

    // 標準錯誤事件
    if (window.electronAPI.onError) {
      window.electronAPI.onError((error) => {
        this._updateErrorState(error);
        this.emit('taskFailed', { error, success: false });
      });
    }
  }

  /**
   * 設置傳統事件監聽
   */
  _setupLegacyEventListeners() {
    // 與原始 UIServiceAdapter 相同的實現
    this._setupStandardEventListeners();
  }

  /**
   * 開始狀態監控
   */
  _startStatusMonitoring() {
    if (this.pollingInterval) return;

    this.pollingInterval = setInterval(async () => {
      try {
        await this._updateSystemStatus();
      } catch (error) {
        console.error('Status monitoring error:', error);
      }
    }, 5000); // 每5秒更新一次

    devLog('✅ Status monitoring started');
  }

  /**
   * 更新系統狀態
   */
  async _updateSystemStatus() {
    try {
      if (this.enhancedBackendReady && window.electronAPI.getAllSessionsStatus) {
        const status = await window.electronAPI.getAllSessionsStatus();
        
        if (status && !status.error) {
          this._updateSessionStats(status);
          this._updateSystemInfo(status.systemInfo);
          
          this.emit('statusUpdate', {
            sessionStats: this.enhancedState.sessionStats,
            systemInfo: this.enhancedState.systemInfo,
            capabilities: this.enhancedState.capabilities
          });
        }
      }
    } catch (error) {
      console.debug('Status update failed:', error);
    }
  }

  /**
   * 更新會話統計
   */
  _updateSessionStats(status) {
    if (!status.sessions) return;

    const stats = {
      totalSessions: status.sessions.length,
      activeSessions: status.sessions.filter(s => s.status === 'running').length,
      completedSessions: status.sessions.filter(s => s.status === 'completed').length,
      failedSessions: status.sessions.filter(s => s.status === 'error').length
    };

    this.enhancedState.sessionStats = stats;
  }

  /**
   * 更新系統信息
   */
  _updateSystemInfo(systemInfo) {
    if (systemInfo) {
      this.enhancedState.systemInfo = { ...this.enhancedState.systemInfo, ...systemInfo };
      this.lastSystemInfo = systemInfo;
    }
  }

  /**
   * 更新進度狀態
   */
  _updateProgressState(progress) {
    // 更新傳統狀態（向後兼容）
    this.legacyState.progress = progress.percent || 0;
    this.legacyState.currentFile = progress.filename || progress.message || '';
    this.legacyState.isProcessing = true;
    
    if (progress.status === 'completed' && progress.filename) {
      this.legacyState.completedFiles.add(progress.filename);
      this.legacyState.currentFileIndex += 1;
    }
  }

  /**
   * 更新完成狀態
   */
  _updateCompletionState(result) {
    this.legacyState.isProcessing = false;
    this.legacyState.isPaused = false;
    this.legacyState.progress = 100;
    this.currentSessionId = null;
    
    // 更新會話統計
    this.enhancedState.sessionStats.completedSessions += 1;
    
    if (result.results) {
      result.results.forEach(r => {
        if (r.success && r.input) {
          const filename = r.input.split('/').pop() || r.input.split('\\').pop();
          this.legacyState.completedFiles.add(filename);
        }
      });
    }
  }

  /**
   * 更新錯誤狀態
   */
  _updateErrorState(error) {
    this.legacyState.isProcessing = false;
    this.legacyState.isPaused = false;
    this.legacyState.error = error;
    this.currentSessionId = null;
    
    // 更新會話統計
    this.enhancedState.sessionStats.failedSessions += 1;
  }

  /**
   * 開始處理字幕（增強版）
   */
  async startSubtitleProcessing(options) {
    const { files, settings, corrections = [] } = options;

    try {
      // 重置狀態
      this._resetProcessingState();

      devLog(`Starting subtitle processing with ${this.enhancedState.backend} backend`);

      if (this.enhancedBackendReady && window.electronAPI.enhancedProcessFiles) {
        // 使用增強版處理
        const result = await window.electronAPI.enhancedProcessFiles({
          files: files,
          settings,
          corrections: settings.enableCorrections ? corrections : []
        });

        if (result.success) {
          this.currentSessionId = result.sessionId;
          this.enhancedState.sessionStats.totalSessions += 1;
          this.enhancedState.sessionStats.activeSessions += 1;
          
          devLog(`✅ Enhanced processing started, session: ${result.sessionId}`);
          
          this.emit('processingStarted', {
            sessionId: result.sessionId,
            backend: result.backend,
            enhanced: true
          });
        }

        return result;

      } else if (window.electronAPI.processFiles) {
        // 使用標準處理
        devLog('Using standard processing');
        
        const result = await window.electronAPI.processFiles({
          files: files,
          settings,
          corrections: settings.enableCorrections ? corrections : []
        });

        this.emit('processingStarted', {
          backend: this.enhancedState.backend,
          enhanced: false
        });

        return { success: true };

      } else {
        throw new Error('No processing backend available');
      }

    } catch (error) {
      this.legacyState.isProcessing = false;
      this.legacyState.error = error;
      
      console.error('Processing start failed:', error);
      
      // 嘗試重試
      if (this.retryCount < this.maxRetries) {
        this.retryCount++;
        devLog(`Retrying processing (${this.retryCount}/${this.maxRetries})...`);
        
        // 等待一下再重試
        await new Promise(resolve => setTimeout(resolve, 1000));
        return this.startSubtitleProcessing(options);
      }
      
      throw error;
    }
  }

  /**
   * 停止處理（增強版）
   */
  async stopProcessing() {
    try {
      this.legacyState.isPaused = true;

      if (this.enhancedBackendReady && this.currentSessionId) {
        // 使用增強版停止
        const result = await window.electronAPI.enhancedStopProcessing(this.currentSessionId);
        
        if (result.success) {
          devLog(`✅ Enhanced processing stopped for session: ${this.currentSessionId}`);
          this.enhancedState.sessionStats.activeSessions = Math.max(0, this.enhancedState.sessionStats.activeSessions - 1);
        }
        
        return result;

      } else if (window.electronAPI.pauseProcessing) {
        // 使用標準停止
        const result = await window.electronAPI.pauseProcessing();
        devLog('Standard processing stopped');
        return result;

      } else {
        devLog('No stop method available');
        return { success: false, message: 'No stop method available' };
      }

    } catch (error) {
      console.error('Failed to stop processing:', error);
      return { success: false, error: error.message };
    } finally {
      this._resetProcessingState();
    }
  }

  /**
   * 重置處理狀態
   */
  _resetProcessingState() {
    this.legacyState.isProcessing = false;
    this.legacyState.isPaused = false;
    this.legacyState.progress = 0;
    this.legacyState.currentFile = '';
    this.legacyState.currentFileIndex = 0;
    this.legacyState.completedFiles = new Set();
    this.legacyState.error = null;
    this.retryCount = 0;
  }

  /**
   * 獲取詳細狀態報告
   */
  async getDetailedStatusReport() {
    try {
      const baseReport = {
        timestamp: new Date().toISOString(),
        backend: this.enhancedState.backend,
        initialized: this.initialized,
        enhancedBackendReady: this.enhancedBackendReady,
        currentSession: this.currentSessionId,
        legacyState: { ...this.legacyState },
        enhancedState: { ...this.enhancedState }
      };

      if (this.enhancedBackendReady && window.electronAPI.getAllSessionsStatus) {
        const status = await window.electronAPI.getAllSessionsStatus();
        return {
          ...baseReport,
          serverStatus: status
        };
      }

      return baseReport;

    } catch (error) {
      return {
        timestamp: new Date().toISOString(),
        error: error.message,
        backend: this.enhancedState.backend
      };
    }
  }

  /**
   * 獲取會話狀態
   */
  async getSessionStatus(sessionId = null) {
    try {
      const targetSessionId = sessionId || this.currentSessionId;
      
      if (this.enhancedBackendReady && targetSessionId && window.electronAPI.getSessionStatus) {
        return await window.electronAPI.getSessionStatus(targetSessionId);
      }
      
      return null;
    } catch (error) {
      console.error('Get session status failed:', error);
      return null;
    }
  }

  /**
   * 獲取服務狀態（向後兼容）
   */
  getServiceStatus() {
    return {
      initialized: this.initialized,
      serviceReady: this.enhancedBackendReady || this.enhancedState.backend !== 'legacy',
      backend: this.enhancedState.backend,
      capabilities: this.enhancedState.capabilities,
      uiState: { ...this.legacyState },
      enhancedState: { ...this.enhancedState },
      currentSession: this.currentSessionId,
      systemInfo: this.lastSystemInfo
    };
  }

  /**
   * 獲取功能可用性
   */
  getFeatureAvailability() {
    return {
      ...this.enhancedState.capabilities,
      enhancedProcessing: this.enhancedBackendReady,
      sessionManagement: this.enhancedBackendReady,
      systemMonitoring: this.enhancedBackendReady,
      legacyMode: this.enhancedState.backend === 'legacy'
    };
  }

  /**
   * 格式化進度信息（向後兼容）
   */
  formatProgressForUI() {
    return {
      percent: this.legacyState.progress,
      filename: this.legacyState.currentFile,
      fileIndex: this.legacyState.currentFileIndex,
      completedCount: this.legacyState.completedFiles.size,
      isProcessing: this.legacyState.isProcessing,
      isPaused: this.legacyState.isPaused,
      error: this.legacyState.error,
      
      // 增強版信息
      enhanced: this.enhancedBackendReady,
      backend: this.enhancedState.backend,
      sessionId: this.currentSessionId,
      sessionStats: this.enhancedState.sessionStats
    };
  }

  /**
   * 清理資源
   */
  dispose() {
    // 停止狀態監控
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }

    // 停止當前處理
    if (this.currentSessionId) {
      this.stopProcessing().catch(console.error);
    }

    // 清理事件監聽
    this.removeAllListeners();
    
    // 重置狀態
    this.initialized = false;
    this.enhancedBackendReady = false;
    this.currentSessionId = null;

    devLog('Enhanced UI Service Adapter disposed');
  }
}

// 創建單例實例
let enhancedUIServiceAdapter = null;

export const getEnhancedUIServiceAdapter = () => {
  if (!enhancedUIServiceAdapter) {
    enhancedUIServiceAdapter = new EnhancedUIServiceAdapter();
  }
  return enhancedUIServiceAdapter;
};

// 向後兼容的導出
export const getUIServiceAdapter = getEnhancedUIServiceAdapter;

export default EnhancedUIServiceAdapter;