/**
 * 錯誤恢復工具
 * 提供智能錯誤恢復和診斷功能
 */

import logger from './logger';

// 錯誤分類和恢復策略
const ERROR_PATTERNS = {
  // Python 環境錯誤
  PYTHON_MISSING: {
    pattern: /python.*not found|python.*無法找到/i,
    category: 'environment',
    severity: 'critical',
    strategy: 'install_python',
    recovery: {
      automatic: false,
      message: '需要安裝Python環境',
      actions: ['install_python', 'check_path']
    }
  },
  
  // 模組缺失錯誤
  MODULE_MISSING: {
    pattern: /no module named|找不到模組|modulenotfounderror/i,
    category: 'dependencies',
    severity: 'high', 
    strategy: 'install_package',
    recovery: {
      automatic: true,
      message: '嘗試自動安裝缺失的模組',
      actions: ['install_missing_module', 'retry_import']
    }
  },
  
  // GPU/CUDA 錯誤
  CUDA_ERROR: {
    pattern: /cuda|gpu.*error|nvidia/i,
    category: 'hardware',
    severity: 'medium',
    strategy: 'fallback_cpu',
    recovery: {
      automatic: true,
      message: '切換到CPU模式繼續處理',
      actions: ['disable_gpu', 'use_cpu_mode']
    }
  },
  
  // 音頻檔案錯誤
  AUDIO_ERROR: {
    pattern: /audio.*error|soundfile|librosa|音頻.*錯誤/i,
    category: 'file_processing',
    severity: 'medium',
    strategy: 'audio_fallback',
    recovery: {
      automatic: true,
      message: '使用替代音頻處理方法',
      actions: ['convert_audio_format', 'use_basic_loader']
    }
  },
  
  // 記憶體不足錯誤
  MEMORY_ERROR: {
    pattern: /memory.*error|out of memory|記憶體不足/i,
    category: 'resources',
    severity: 'high',
    strategy: 'reduce_batch_size',
    recovery: {
      automatic: true,
      message: '減少處理批次大小',
      actions: ['reduce_batch', 'clear_cache', 'use_streaming']
    }
  },
  
  // 檔案權限錯誤
  PERMISSION_ERROR: {
    pattern: /permission denied|access denied|權限不足/i,
    category: 'permissions',
    severity: 'medium',
    strategy: 'fix_permissions',
    recovery: {
      automatic: false,
      message: '需要檢查檔案權限',
      actions: ['run_as_admin', 'change_output_dir']
    }
  }
};

/**
 * 分析錯誤並提供恢復建議
 * @param {Error} error - 錯誤物件
 * @param {Object} context - 錯誤發生的上下文
 * @returns {Object} 錯誤分析結果
 */
export const analyzeError = (error, context = {}) => {
  const errorMessage = error.message || error.toString();
  const errorStack = error.stack || '';
  
  logger.log('debug', 'Analyzing error:', errorMessage);
  
  // 匹配錯誤模式
  for (const [key, pattern] of Object.entries(ERROR_PATTERNS)) {
    if (pattern.pattern.test(errorMessage) || pattern.pattern.test(errorStack)) {
      return {
        id: key,
        category: pattern.category,
        severity: pattern.severity,
        strategy: pattern.strategy,
        recovery: pattern.recovery,
        originalError: error,
        context,
        timestamp: new Date().toISOString()
      };
    }
  }
  
  // 未知錯誤的預設處理
  return {
    id: 'UNKNOWN_ERROR',
    category: 'unknown',
    severity: 'medium',
    strategy: 'manual',
    recovery: {
      automatic: false,
      message: '發生未知錯誤，請檢查日誌',
      actions: ['check_logs', 'contact_support']
    },
    originalError: error,
    context,
    timestamp: new Date().toISOString()
  };
};

/**
 * 執行錯誤恢復策略
 * @param {Object} errorAnalysis - 錯誤分析結果
 * @param {Object} options - 恢復選項
 * @returns {Promise<boolean>} 恢復是否成功
 */
export const executeRecovery = async (errorAnalysis, options = {}) => {
  const { strategy, recovery } = errorAnalysis;
  
  logger.log('info', `執行錯誤恢復策略: ${strategy}`);
  
  try {
    switch (strategy) {
      case 'fallback_cpu':
        return await fallbackToCpu(options);
        
      case 'install_package':
        return await installMissingPackage(errorAnalysis, options);
        
      case 'audio_fallback':
        return await audioFallback(options);
        
      case 'reduce_batch_size':
        return await reduceBatchSize(options);
        
      case 'fix_permissions':
        return await fixPermissions(options);
        
      default:
        logger.log('warn', `未知的恢復策略: ${strategy}`);
        return false;
    }
  } catch (recoveryError) {
    logger.log('error', '錯誤恢復失敗:', recoveryError);
    return false;
  }
};

/**
 * 切換到CPU模式
 */
async function fallbackToCpu(options) {
  logger.log('info', '切換到CPU模式');
  
  if (options.onSettingsUpdate) {
    options.onSettingsUpdate({
      enable_gpu: false,
      performanceMode: 'cpu'
    });
  }
  
  return true;
}

/**
 * 安裝缺失的套件
 */
async function installMissingPackage(errorAnalysis, options) {
  const moduleName = extractModuleName(errorAnalysis.originalError.message);
  logger.log('info', `嘗試安裝缺失的模組: ${moduleName}`);
  
  // 這裡可以整合實際的套件安裝邏輯
  // 例如調用Python的pip安裝
  
  return false; // 預設返回false，因為需要用戶干預
}

/**
 * 音頻處理降級
 */
async function audioFallback(options) {
  logger.log('info', '使用基礎音頻處理模式');
  
  if (options.onSettingsUpdate) {
    options.onSettingsUpdate({
      use_advanced_audio: false,
      audio_processor: 'basic'
    });
  }
  
  return true;
}

/**
 * 減少批次大小
 */
async function reduceBatchSize(options) {
  logger.log('info', '減少處理批次大小');
  
  if (options.onSettingsUpdate) {
    const currentBatchSize = options.currentSettings?.batch_size || 16;
    const newBatchSize = Math.max(1, Math.floor(currentBatchSize / 2));
    
    options.onSettingsUpdate({
      batch_size: newBatchSize
    });
  }
  
  return true;
}

/**
 * 修復檔案權限
 */
async function fixPermissions(options) {
  logger.log('info', '嘗試修復檔案權限');
  
  // 建議用戶以管理員身份運行或更改輸出目錄
  return false; // 需要用戶手動操作
}

/**
 * 從錯誤訊息中提取模組名稱
 */
function extractModuleName(errorMessage) {
  const matches = errorMessage.match(/no module named ['"]?([^'"]+)['"]?/i);
  return matches ? matches[1] : 'unknown';
}

/**
 * 生成用戶友好的錯誤報告
 * @param {Object} errorAnalysis - 錯誤分析結果
 * @returns {Object} 用戶友好的錯誤報告
 */
export const generateErrorReport = (errorAnalysis) => {
  const { category, severity, recovery, originalError } = errorAnalysis;
  
  return {
    title: getErrorTitle(category),
    description: getErrorDescription(errorAnalysis),
    severity,
    canRecover: recovery.automatic,
    recoveryMessage: recovery.message,
    suggestedActions: recovery.actions.map(action => getActionDescription(action)),
    technicalDetails: {
      error: originalError.message,
      stack: originalError.stack,
      timestamp: errorAnalysis.timestamp
    }
  };
};

/**
 * 獲取錯誤標題
 */
function getErrorTitle(category) {
  const titles = {
    environment: 'Python環境問題',
    dependencies: '套件依賴問題', 
    hardware: '硬體相容性問題',
    file_processing: '檔案處理問題',
    resources: '系統資源問題',
    permissions: '權限問題',
    unknown: '未知錯誤'
  };
  
  return titles[category] || '未知錯誤';
}

/**
 * 獲取錯誤描述
 */
function getErrorDescription(errorAnalysis) {
  // 根據錯誤類型提供詳細描述
  const descriptions = {
    PYTHON_MISSING: 'SRT GO 無法找到Python環境。請確保已正確安裝Python。',
    MODULE_MISSING: '缺少必需的Python套件。程式會嘗試自動安裝。',
    CUDA_ERROR: 'GPU處理出現問題。程式將自動切換到CPU模式。',
    AUDIO_ERROR: '音頻檔案處理失敗。將嘗試使用替代方法處理。',
    MEMORY_ERROR: '系統記憶體不足。將減少處理批次大小以節省記憶體。',
    PERMISSION_ERROR: '檔案存取權限不足。請檢查輸出目錄的權限設定。'
  };
  
  return descriptions[errorAnalysis.id] || '發生了未預期的錯誤。';
}

/**
 * 獲取動作描述
 */
function getActionDescription(action) {
  const actions = {
    install_python: '安裝Python環境',
    check_path: '檢查環境變數',
    install_missing_module: '安裝缺失的模組',
    retry_import: '重新載入模組',
    disable_gpu: '禁用GPU處理',
    use_cpu_mode: '使用CPU模式',
    convert_audio_format: '轉換音頻格式',
    use_basic_loader: '使用基礎音頻載入器',
    reduce_batch: '減少批次大小',
    clear_cache: '清除快取',
    use_streaming: '使用串流處理',
    run_as_admin: '以管理員身份執行',
    change_output_dir: '更改輸出目錄',
    check_logs: '檢查錯誤日誌',
    contact_support: '聯繫技術支援'
  };
  
  return actions[action] || action;
}