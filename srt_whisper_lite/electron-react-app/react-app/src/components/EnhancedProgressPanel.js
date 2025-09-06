/**
 * 增強進度面板
 * 整合新服務層的進度追蹤和錯誤處理功能
 * 向後兼容現有UI設計
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, Clock, CheckCircle, AlertCircle, AlertTriangle, 
  Cpu, Zap, RotateCcw, Info, ChevronDown, ChevronUp 
} from 'lucide-react';
import clsx from 'clsx';
import { getUIServiceAdapter } from '../services/UIServiceAdapter';

const EnhancedProgressPanel = ({ 
  progress = 0, 
  currentFile = '', 
  totalFiles = 0, 
  status = 'idle',
  onRetry = null 
}) => {
  const [serviceAdapter] = useState(() => getUIServiceAdapter());
  const [serviceStatus, setServiceStatus] = useState(null);
  const [environmentInfo, setEnvironmentInfo] = useState(null);
  const [errorDetails, setErrorDetails] = useState(null);
  const [recoveryInfo, setRecoveryInfo] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [timeEstimate, setTimeEstimate] = useState(null);
  const [currentStage, setCurrentStage] = useState('');

  // 更新服務狀態
  const updateServiceStatus = useCallback(async () => {
    try {
      const status = serviceAdapter.getServiceStatus();
      setServiceStatus(status);
    } catch (error) {
      console.error('Failed to get service status:', error);
    }
  }, [serviceAdapter]);

  useEffect(() => {
    if (!serviceAdapter.initialized) return;

    // 監聽服務事件
    const handleProgressUpdate = (data) => {
      if (data.stage !== undefined) {
        setCurrentStage(data.stageMessage || `階段 ${data.stage + 1}`);
      }
      
      // 計算預估時間
      if (data.percent > 0 && data.startTime) {
        const elapsed = Date.now() - data.startTime;
        const estimated = (elapsed / data.percent) * (100 - data.percent);
        setTimeEstimate(estimated);
      }
    };

    const handleServiceError = (data) => {
      setErrorDetails({
        category: data.category,
        message: data.message,
        recovery: data.recovery
      });
    };

    const handleErrorRecovery = (data) => {
      setRecoveryInfo({
        message: data.message,
        strategy: data.strategy
      });
      
      // 3秒後清除恢復信息
      setTimeout(() => setRecoveryInfo(null), 3000);
    };

    const handleEnvironmentChange = (data) => {
      setEnvironmentInfo(data);
      
      // 自動清除環境變更通知
      setTimeout(() => setEnvironmentInfo(null), 5000);
    };

    // 註冊事件監聽器
    serviceAdapter.on('progressUpdate', handleProgressUpdate);
    serviceAdapter.on('serviceError', handleServiceError);
    serviceAdapter.on('errorRecovery', handleErrorRecovery);
    serviceAdapter.on('environmentChange', handleEnvironmentChange);

    // 獲取初始狀態
    updateServiceStatus();

    return () => {
      serviceAdapter.off('progressUpdate', handleProgressUpdate);
      serviceAdapter.off('serviceError', handleServiceError);
      serviceAdapter.off('errorRecovery', handleErrorRecovery);
      serviceAdapter.off('environmentChange', handleEnvironmentChange);
    };
  }, [serviceAdapter, updateServiceStatus]);

  // 格式化時間
  const formatTime = (milliseconds) => {
    if (!milliseconds || milliseconds < 0) return '--:--';
    const seconds = Math.floor(milliseconds / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 獲取狀態配置
  const getStatusConfig = () => {
    switch (status) {
      case 'processing':
        return {
          icon: Play,
          color: 'text-primary-500',
          bgColor: 'bg-primary-50',
          borderColor: 'border-primary-200',
          title: '正在處理字幕',
          subtitle: `處理進度 ${Math.round(progress)}%`
        };
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-500',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          title: '處理完成',
          subtitle: '所有檔案已成功處理'
        };
      case 'error':
        return {
          icon: AlertCircle,
          color: 'text-red-500',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          title: '處理失敗',
          subtitle: '處理過程中發生錯誤'
        };
      case 'warning':
        return {
          icon: AlertTriangle,
          color: 'text-yellow-500',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          title: '部分成功',
          subtitle: '部分檔案處理成功'
        };
      default:
        return {
          icon: Info,
          color: 'text-gray-500',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          title: '準備就緒',
          subtitle: '等待開始處理'
        };
    }
  };

  const statusConfig = getStatusConfig();
  const StatusIcon = statusConfig.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'card p-6 border-2 relative overflow-hidden',
        statusConfig.borderColor,
        statusConfig.bgColor
      )}
    >
      {/* 環境變更通知 */}
      <AnimatePresence>
        {environmentInfo && (
          <motion.div
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            className="absolute top-4 right-4 bg-blue-100 border border-blue-200 rounded-lg p-3 max-w-xs"
          >
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              <span className="text-sm text-blue-800 font-medium">
                {environmentInfo.message}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 錯誤恢復通知 */}
      <AnimatePresence>
        {recoveryInfo && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute top-4 right-4 bg-green-100 border border-green-200 rounded-lg p-3 max-w-xs"
          >
            <div className="flex items-center space-x-2">
              <RotateCcw className="w-4 h-4 text-green-600" />
              <span className="text-sm text-green-800 font-medium">
                {recoveryInfo.message}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主要標題區域 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={clsx('p-2 rounded-lg', statusConfig.bgColor)}>
            <StatusIcon className={clsx('w-6 h-6', statusConfig.color)} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {statusConfig.title}
            </h3>
            <p className="text-sm text-gray-600">
              {statusConfig.subtitle}
            </p>
            {currentStage && status === 'processing' && (
              <p className="text-xs text-gray-500 mt-1">
                當前階段: {currentStage}
              </p>
            )}
          </div>
        </div>

        {/* 時間和服務狀態 */}
        <div className="flex items-center space-x-4">
          {timeEstimate && status === 'processing' && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>預計剩餘: {formatTime(timeEstimate)}</span>
            </div>
          )}

          {serviceStatus?.serviceReady && (
            <div className="flex items-center space-x-2 text-sm text-green-600">
              <Zap className="w-4 h-4" />
              <span>服務就緒</span>
            </div>
          )}
        </div>
      </div>

      {/* 進度條 */}
      {status !== 'idle' && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">整體進度</span>
            <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
          </div>
          
          <div className="progress-bar">
            <motion.div
              className={clsx(
                'progress-fill',
                status === 'completed' && 'bg-green-500',
                status === 'error' && 'bg-red-500',
                status === 'warning' && 'bg-yellow-500'
              )}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>
      )}

      {/* 當前處理檔案 */}
      {currentFile && status === 'processing' && (
        <div className="mb-4">
          <div className="text-sm font-medium text-gray-700 mb-1">當前檔案</div>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
            <span className="truncate">{currentFile}</span>
          </div>
        </div>
      )}

      {/* 檔案統計 */}
      {totalFiles > 0 && (
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {Math.ceil((progress / 100) * totalFiles)}
            </div>
            <div className="text-xs text-gray-500">已完成</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {totalFiles - Math.ceil((progress / 100) * totalFiles)}
            </div>
            <div className="text-xs text-gray-500">剩餘</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{totalFiles}</div>
            <div className="text-xs text-gray-500">總計</div>
          </div>
        </div>
      )}

      {/* 錯誤詳情 */}
      {errorDetails && status === 'error' && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-4 p-4 bg-red-100 border border-red-200 rounded-lg"
        >
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="font-medium text-red-800">
                錯誤分類: {errorDetails.category}
              </div>
              <div className="text-sm text-red-700 mt-1">
                {errorDetails.message}
              </div>
              
              {errorDetails.recovery && (
                <div className="mt-3 p-3 bg-red-50 rounded border border-red-200">
                  <div className="text-sm font-medium text-red-800">
                    建議的恢復方案:
                  </div>
                  <div className="text-sm text-red-700 mt-1">
                    {errorDetails.recovery.message}
                  </div>
                  
                  {errorDetails.recovery.automatic && onRetry && (
                    <button
                      onClick={onRetry}
                      className="mt-2 btn btn-sm bg-red-600 text-white hover:bg-red-700"
                    >
                      <RotateCcw className="w-4 h-4 mr-1" />
                      自動重試
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* 成功完成狀態 */}
      {status === 'completed' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-4 p-3 bg-green-100 border border-green-200 rounded-lg"
        >
          <div className="flex items-center space-x-2 text-green-800">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">
              所有字幕檔案已成功生成並儲存
            </span>
          </div>
        </motion.div>
      )}

      {/* 高級狀態面板 (可展開) */}
      {serviceStatus?.serviceReady && (
        <div className="mt-4 border-t border-gray-200 pt-4">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center justify-between w-full text-sm text-gray-600 hover:text-gray-800"
          >
            <span>系統狀態詳情</span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 space-y-2 text-xs text-gray-600"
              >
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="font-medium">服務健康度:</span>
                    <span className={clsx(
                      'ml-2 px-2 py-0.5 rounded-full text-xs',
                      serviceStatus.uiState.serviceHealth === 'healthy' && 'bg-green-100 text-green-800',
                      serviceStatus.uiState.serviceHealth === 'degraded' && 'bg-yellow-100 text-yellow-800',
                      serviceStatus.uiState.serviceHealth === 'critical' && 'bg-red-100 text-red-800'
                    )}>
                      {serviceStatus.uiState.serviceHealth}
                    </span>
                  </div>
                  
                  {serviceStatus.environment && (
                    <div>
                      <span className="font-medium">環境狀態:</span>
                      <span className={clsx(
                        'ml-2 px-2 py-0.5 rounded-full text-xs',
                        serviceStatus.environment.ready && 'bg-green-100 text-green-800',
                        !serviceStatus.environment.ready && 'bg-red-100 text-red-800'
                      )}>
                        {serviceStatus.environment.ready ? '就緒' : '未就緒'}
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* 處理提示 */}
      {status === 'processing' && (
        <motion.div
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="mt-4 text-center text-sm text-gray-500"
        >
          {serviceStatus?.serviceReady 
            ? '使用進階服務處理中，請保持程式開啟'
            : '請保持程式開啟，處理時間取決於檔案大小和模型選擇'
          }
        </motion.div>
      )}
    </motion.div>
  );
};

export default EnhancedProgressPanel;