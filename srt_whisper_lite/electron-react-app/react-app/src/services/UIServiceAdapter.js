/**
 * UI服務適配器
 * 橋接新的服務層與現有React UI組件
 * 提供統一的狀態管理和事件處理
 */

import { EventEmitter } from 'events';

class UIServiceAdapter extends EventEmitter {
  constructor() {
    super();
    this.initialized = false;
    this.serviceReady = false;
    this.currentTaskId = null;
    this.environmentStatus = null;
    this.lastProgress = 0;
    
    // UI狀態
    this.uiState = {
      isProcessing: false,
      isPaused: false,
      progress: 0,
      currentFile: '',
      currentFileIndex: 0,
      completedFiles: new Set(),
      error: null,
      environment: null,
      serviceHealth: 'unknown'
    };

    // 初始化適配器
    this.initialize();
  }

  /**
   * 初始化適配器
   */
  async initialize() {
    if (this.initialized) return;

    try {
      // 檢查是否有可用的服務
      if (window.electronAPI && window.electronAPI.initializeServices) {
        await this._initializeWithServices();
      } else {
        // 降級到傳統模式
        await this._initializeLegacyMode();
      }

      this.initialized = true;
      this.emit('initialized', { serviceReady: this.serviceReady });

    } catch (error) {
      console.error('UIServiceAdapter initialization failed:', error);
      await this._initializeLegacyMode();
      this.initialized = true;
    }
  }

  /**
   * 使用新服務層初始化
   */
  async _initializeWithServices() {
    try {
      // 初始化服務層
      const result = await window.electronAPI.initializeServices();
      this.serviceReady = result.success;

      if (this.serviceReady) {
        // 獲取環境狀態
        this.environmentStatus = await window.electronAPI.getEnvironmentStatus();
        this.uiState.environment = this.environmentStatus;
        this.uiState.serviceHealth = this.environmentStatus.overall || 'unknown';

        // 設置服務事件監聽
        this._setupServiceEventListeners();

        // Service layer initialized successfully
      }

    } catch (error) {
      console.warn('Service layer initialization failed, falling back to legacy mode:', error);
      this.serviceReady = false;
      throw error;
    }
  }

  /**
   * 傳統模式初始化（向後兼容）
   */
  async _initializeLegacyMode() {
    this.serviceReady = false;
    this.uiState.serviceHealth = 'legacy';
    
    // 設置傳統事件監聽
    this._setupLegacyEventListeners();
    
    // Using legacy mode
  }

  /**
   * 設置新服務層事件監聽
   */
  _setupServiceEventListeners() {
    if (!window.electronAPI.onServiceEvent) return;

    // 任務事件
    window.electronAPI.onServiceEvent('taskStarted', (data) => {
      this.currentTaskId = data.task.id;
      this.uiState.isProcessing = true;
      this.uiState.currentFile = data.task.metadata?.audioPath || '';
      this.emit('taskStarted', data.task);
    });

    window.electronAPI.onServiceEvent('progressUpdate', (data) => {
      const task = data.task;
      this.uiState.progress = task.progress;
      this.uiState.currentFile = task.stageMessage || this.uiState.currentFile;
      
      // 發送UI更新事件
      this.emit('progressUpdate', {
        percent: task.progress,
        filename: this.uiState.currentFile,
        stage: task.currentStage,
        stageMessage: task.stageMessage
      });
    });

    window.electronAPI.onServiceEvent('taskCompleted', (data) => {
      this.uiState.isProcessing = false;
      this.uiState.progress = 100;
      this.currentTaskId = null;
      
      this.emit('taskCompleted', {
        success: true,
        result: data.result,
        task: data.task
      });
    });

    window.electronAPI.onServiceEvent('taskFailed', (data) => {
      this.uiState.isProcessing = false;
      this.uiState.error = data.error;
      this.currentTaskId = null;
      
      this.emit('taskFailed', {
        success: false,
        error: data.error,
        task: data.task
      });
    });

    // 錯誤處理事件
    window.electronAPI.onServiceEvent('error', (data) => {
      this.emit('serviceError', {
        category: data.error.category,
        message: data.error.message,
        recovery: data.recovery
      });
    });

    // 環境事件
    window.electronAPI.onServiceEvent('fallbackToCPU', () => {
      this.emit('environmentChange', {
        type: 'fallback_cpu',
        message: '已切換到CPU模式'
      });
    });
  }

  /**
   * 設置傳統事件監聽（向後兼容）
   */
  _setupLegacyEventListeners() {
    if (!window.electronAPI) return;

    // 傳統進度事件
    if (window.electronAPI.onProgress) {
      window.electronAPI.onProgress((progress) => {
        this.uiState.progress = progress.percent || 0;
        this.uiState.currentFile = progress.filename || '';
        
        if (progress.status === 'completed') {
          this.uiState.completedFiles.add(progress.filename);
        }

        this.emit('progressUpdate', progress);
      });
    }

    // 傳統完成事件
    if (window.electronAPI.onComplete) {
      window.electronAPI.onComplete((result) => {
        this.uiState.isProcessing = false;
        this.uiState.progress = 100;
        this.emit('taskCompleted', result);
      });
    }

    // 傳統錯誤事件
    if (window.electronAPI.onError) {
      window.electronAPI.onError((error) => {
        this.uiState.isProcessing = false;
        this.uiState.error = error;
        this.emit('taskFailed', { error, success: false });
      });
    }
  }

  /**
   * 開始處理字幕
   * @param {Object} options 處理選項
   */
  async startSubtitleProcessing(options) {
    const { files, settings, corrections = [] } = options;

    try {
      // 重置狀態
      this.uiState.isProcessing = true;
      this.uiState.isPaused = false;
      this.uiState.progress = 0;
      this.uiState.currentFile = '';
      this.uiState.currentFileIndex = 0;
      this.uiState.completedFiles = new Set();
      this.uiState.error = null;

      if (this.serviceReady && window.electronAPI.createSubtitleTask) {
        // 使用新服務層
        for (const file of files) {
          const taskId = await window.electronAPI.createSubtitleTask(file.path, {
            ...settings,
            corrections: settings.enableCorrections ? corrections : []
          });
          this.currentTaskId = taskId;
        }
      } else {
        // 使用傳統方式
        await window.electronAPI.processFiles({
          files: files,
          settings,
          corrections: settings.enableCorrections ? corrections : []
        });
      }

      return { success: true };

    } catch (error) {
      this.uiState.isProcessing = false;
      this.uiState.error = error;
      
      // 嘗試錯誤恢復
      if (this.serviceReady) {
        await this._attemptErrorRecovery(error, options);
      }
      
      throw error;
    }
  }

  /**
   * 停止處理
   */
  async stopProcessing() {
    try {
      this.uiState.isPaused = true;

      if (this.serviceReady && this.currentTaskId) {
        await window.electronAPI.cancelTask(this.currentTaskId);
      } else if (window.electronAPI.pauseProcessing) {
        await window.electronAPI.pauseProcessing();
      }

      this.uiState.isProcessing = false;
      this.uiState.progress = 0;
      this.currentTaskId = null;

      this.emit('processingStopped');

    } catch (error) {
      console.error('Failed to stop processing:', error);
      // 強制停止
      this.uiState.isProcessing = false;
      this.uiState.progress = 0;
      this.currentTaskId = null;
    }
  }

  /**
   * 獲取環境狀態
   */
  async getEnvironmentStatus(forceRefresh = false) {
    try {
      if (this.serviceReady) {
        this.environmentStatus = await window.electronAPI.getEnvironmentStatus(forceRefresh);
        this.uiState.environment = this.environmentStatus;
        this.uiState.serviceHealth = this.environmentStatus.overall || 'unknown';
      }
      
      return this.environmentStatus;
    } catch (error) {
      console.error('Failed to get environment status:', error);
      return { error: error.message, overall: 'error' };
    }
  }

  /**
   * 獲取服務狀態
   */
  getServiceStatus() {
    return {
      initialized: this.initialized,
      serviceReady: this.serviceReady,
      uiState: { ...this.uiState },
      environment: this.environmentStatus,
      currentTask: this.currentTaskId
    };
  }

  /**
   * 嘗試錯誤恢復
   */
  async _attemptErrorRecovery(error, originalOptions) {
    try {
      if (!window.electronAPI.handleError) return false;

      const result = await window.electronAPI.handleError(error, {
        operation: 'subtitle_processing',
        options: originalOptions
      });

      if (result.canRecover && result.recovery.automatic) {
        this.emit('errorRecovery', {
          message: `嘗試自動恢復: ${result.recovery.message}`,
          strategy: result.recovery.strategy
        });

        // 等待恢復完成
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 重試處理
        return await this.startSubtitleProcessing(originalOptions);
      }

      return false;
    } catch (recoveryError) {
      console.error('Error recovery failed:', recoveryError);
      return false;
    }
  }

  /**
   * 獲取詳細狀態報告
   */
  async getDetailedStatusReport() {
    try {
      if (this.serviceReady && window.electronAPI.getDetailedStatusReport) {
        const report = await window.electronAPI.getDetailedStatusReport();
        return {
          ...report,
          uiAdapter: this.getServiceStatus()
        };
      }
      
      return {
        timestamp: new Date().toISOString(),
        mode: 'legacy',
        uiAdapter: this.getServiceStatus()
      };
    } catch (error) {
      return {
        timestamp: new Date().toISOString(),
        error: error.message,
        uiAdapter: this.getServiceStatus()
      };
    }
  }

  /**
   * 格式化進度信息（與現有UI兼容）
   */
  formatProgressForUI() {
    return {
      percent: this.uiState.progress,
      filename: this.uiState.currentFile,
      fileIndex: this.uiState.currentFileIndex,
      completedCount: this.uiState.completedFiles.size,
      isProcessing: this.uiState.isProcessing,
      isPaused: this.uiState.isPaused,
      error: this.uiState.error
    };
  }

  /**
   * 檢查功能可用性
   */
  getFeatureAvailability() {
    return {
      advancedProgressTracking: this.serviceReady,
      errorRecovery: this.serviceReady,
      environmentMonitoring: this.serviceReady,
      taskCancellation: this.serviceReady,
      realTimeStatusReporting: this.serviceReady,
      legacyMode: !this.serviceReady
    };
  }

  /**
   * 清理資源
   */
  dispose() {
    this.removeAllListeners();
    this.initialized = false;
    this.serviceReady = false;
    this.currentTaskId = null;
    this.environmentStatus = null;
  }
}

// 創建單例實例
let uiServiceAdapter = null;

export const getUIServiceAdapter = () => {
  if (!uiServiceAdapter) {
    uiServiceAdapter = new UIServiceAdapter();
  }
  return uiServiceAdapter;
};

export default UIServiceAdapter;