/**
 * 錯誤處理 Hook
 * 提供統一的錯誤處理和恢復功能
 */

import { useState, useCallback, useRef } from 'react';
import { analyzeError, executeRecovery, generateErrorReport } from '../utils/errorRecovery';
import logger from '../utils/logger';

export const useErrorHandler = (options = {}) => {
  const [currentError, setCurrentError] = useState(null);
  const [isRecovering, setIsRecovering] = useState(false);
  const [recoveryAttempts, setRecoveryAttempts] = useState(0);
  const [recoveryHistory, setRecoveryHistory] = useState([]);
  
  const maxRecoveryAttempts = useRef(options.maxRetries || 3);
  const onSettingsUpdate = useRef(options.onSettingsUpdate);
  const currentSettings = useRef(options.currentSettings);
  
  /**
   * 處理錯誤
   * @param {Error} error - 錯誤物件
   * @param {Object} context - 錯誤上下文
   */
  const handleError = useCallback(async (error, context = {}) => {
    logger.log('error', '處理錯誤:', error);
    
    // 分析錯誤
    const errorAnalysis = analyzeError(error, context);
    
    // 生成用戶友好的錯誤報告
    const errorReport = generateErrorReport(errorAnalysis);
    
    // 記錄錯誤
    const errorRecord = {
      ...errorAnalysis,
      report: errorReport,
      id: Date.now().toString()
    };
    
    setCurrentError(errorRecord);
    
    // 如果可以自動恢復且未超過重試次數
    if (errorReport.canRecover && recoveryAttempts < maxRecoveryAttempts.current) {
      await attemptRecovery(errorRecord);
    }
    
    return errorRecord;
  }, [recoveryAttempts]);
  
  /**
   * 嘗試錯誤恢復
   * @param {Object} errorRecord - 錯誤記錄
   */
  const attemptRecovery = useCallback(async (errorRecord) => {
    setIsRecovering(true);
    setRecoveryAttempts(prev => prev + 1);
    
    const recoveryOptions = {
      onSettingsUpdate: onSettingsUpdate.current,
      currentSettings: currentSettings.current,
      maxAttempts: maxRecoveryAttempts.current,
      currentAttempt: recoveryAttempts + 1
    };
    
    try {
      const recoverySuccess = await executeRecovery(errorRecord, recoveryOptions);
      
      const recoveryRecord = {
        timestamp: new Date().toISOString(),
        errorId: errorRecord.id,
        strategy: errorRecord.strategy,
        success: recoverySuccess,
        attempt: recoveryAttempts + 1
      };
      
      setRecoveryHistory(prev => [...prev, recoveryRecord]);
      
      if (recoverySuccess) {
        logger.log('info', `錯誤恢復成功 (嘗試 ${recoveryAttempts + 1})`);
        
        // 清除當前錯誤
        setTimeout(() => {
          clearError();
        }, 2000);
        
        return true;
      } else {
        logger.log('warn', `錯誤恢復失敗 (嘗試 ${recoveryAttempts + 1})`);
        return false;
      }
    } catch (recoveryError) {
      logger.log('error', '恢復過程中發生錯誤:', recoveryError);
      
      setRecoveryHistory(prev => [...prev, {
        timestamp: new Date().toISOString(),
        errorId: errorRecord.id,
        strategy: errorRecord.strategy,
        success: false,
        attempt: recoveryAttempts + 1,
        error: recoveryError.message
      }]);
      
      return false;
    } finally {
      setIsRecovering(false);
    }
  }, [recoveryAttempts]);
  
  /**
   * 手動重試
   */
  const retry = useCallback(async () => {
    if (!currentError) return false;
    
    logger.log('info', '手動重試錯誤恢復');
    return await attemptRecovery(currentError);
  }, [currentError, attemptRecovery]);
  
  /**
   * 清除當前錯誤
   */
  const clearError = useCallback(() => {
    setCurrentError(null);
    setRecoveryAttempts(0);
  }, []);
  
  /**
   * 重置錯誤處理狀態
   */
  const reset = useCallback(() => {
    setCurrentError(null);
    setIsRecovering(false);
    setRecoveryAttempts(0);
    setRecoveryHistory([]);
  }, []);
  
  /**
   * 更新設定
   */
  const updateSettings = useCallback((newSettings) => {
    currentSettings.current = { ...currentSettings.current, ...newSettings };
    if (onSettingsUpdate.current) {
      onSettingsUpdate.current(newSettings);
    }
  }, []);
  
  /**
   * 獲取錯誤統計
   */
  const getErrorStats = useCallback(() => {
    return {
      totalErrors: recoveryHistory.length,
      successfulRecoveries: recoveryHistory.filter(r => r.success).length,
      failedRecoveries: recoveryHistory.filter(r => !r.success).length,
      mostCommonError: getMostCommonError(),
      averageRecoveryTime: getAverageRecoveryTime()
    };
  }, [recoveryHistory]);
  
  const getMostCommonError = () => {
    if (recoveryHistory.length === 0) return null;
    
    const errorCounts = recoveryHistory.reduce((acc, record) => {
      acc[record.strategy] = (acc[record.strategy] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(errorCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || null;
  };
  
  const getAverageRecoveryTime = () => {
    const successfulRecoveries = recoveryHistory.filter(r => r.success);
    if (successfulRecoveries.length === 0) return 0;
    
    // 這裡可以添加實際的恢復時間計算
    return 1500; // 模擬平均恢復時間 1.5秒
  };
  
  /**
   * 檢查是否可以重試
   */
  const canRetry = recoveryAttempts < maxRecoveryAttempts.current && !isRecovering;
  
  return {
    // 狀態
    currentError,
    isRecovering,
    recoveryAttempts,
    recoveryHistory,
    canRetry,
    
    // 方法
    handleError,
    retry,
    clearError,
    reset,
    updateSettings,
    getErrorStats,
    
    // 計算屬性
    hasError: !!currentError,
    canAutoRecover: currentError?.report?.canRecover && canRetry
  };
};