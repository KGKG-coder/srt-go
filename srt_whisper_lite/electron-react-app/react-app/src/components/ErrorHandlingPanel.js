/**
 * 錯誤處理面板
 * 提供智能錯誤處理和恢復建議的UI組件
 * 整合新服務層的錯誤處理能力
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertCircle, AlertTriangle, Info, CheckCircle, 
  RotateCcw, Settings, HelpCircle, X, ChevronDown, 
  ChevronRight, Cpu, Download, Shield, Wrench 
} from 'lucide-react';
import clsx from 'clsx';
import { useI18n } from '../i18n/I18nContext';

const ErrorHandlingPanel = ({ 
  error = null, 
  onRetry = null, 
  onDismiss = null,
  onFixEnvironment = null 
}) => {
  const { t } = useI18n();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [recoveryStep, setRecoveryStep] = useState(0);

  // 錯誤嚴重程度配置
  const getSeverityConfig = (severity) => {
    switch (severity) {
      case 'critical':
        return {
          icon: AlertCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          headerBg: 'bg-red-100',
          title: t('settings.errorSeverity.critical')
        };
      case 'high':
        return {
          icon: AlertTriangle,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          headerBg: 'bg-orange-100',
          title: t('settings.errorSeverity.high')
        };
      case 'medium':
        return {
          icon: AlertTriangle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          headerBg: 'bg-yellow-100',
          title: t('settings.errorSeverity.medium')
        };
      case 'low':
        return {
          icon: Info,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          headerBg: 'bg-blue-100',
          title: t('settings.errorSeverity.low')
        };
      default:
        return {
          icon: Info,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          headerBg: 'bg-gray-100',
          title: t('settings.errorSeverity.default')
        };
    }
  };

  // 獲取恢復策略圖標
  const getRecoveryIcon = (strategy) => {
    switch (strategy) {
      case 'auto_retry':
      case 'retry':
        return RotateCcw;
      case 'fallback':
        return Cpu;
      case 'auto_download':
        return Download;
      case 'repair_environment':
        return Wrench;
      case 'manual':
        return Settings;
      default:
        return HelpCircle;
    }
  };

  // 處理重試
  const handleRetry = async () => {
    if (!onRetry) return;

    setIsRetrying(true);
    setRecoveryStep(1);

    try {
      await onRetry();
      setRecoveryStep(2);
      
      // 成功後自動關閉
      setTimeout(() => {
        onDismiss && onDismiss();
      }, 2000);
    } catch (retryError) {
      setRecoveryStep(3);
      console.error('Retry failed:', retryError);
    } finally {
      setIsRetrying(false);
    }
  };

  // 處理環境修復
  const handleFixEnvironment = async () => {
    if (!onFixEnvironment) return;

    setIsRetrying(true);
    setRecoveryStep(1);

    try {
      await onFixEnvironment();
      setRecoveryStep(2);
    } catch (fixError) {
      setRecoveryStep(3);
      console.error('Environment fix failed:', fixError);
    } finally {
      setIsRetrying(false);
    }
  };

  if (!error) return null;

  const severityConfig = getSeverityConfig(error.severity);
  const SeverityIcon = severityConfig.icon;
  const RecoveryIcon = getRecoveryIcon(error.recovery?.strategy);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.95 }}
        className={clsx(
          'relative rounded-lg border-2 shadow-lg overflow-hidden',
          severityConfig.borderColor,
          severityConfig.bgColor
        )}
      >
        {/* 錯誤標題列 */}
        <div className={clsx('px-4 py-3 flex items-center justify-between', severityConfig.headerBg)}>
          <div className="flex items-center space-x-3">
            <SeverityIcon className={clsx('w-5 h-5', severityConfig.color)} />
            <div>
              <h3 className={clsx('font-semibold', severityConfig.color)}>
                {severityConfig.title}
              </h3>
              <p className="text-sm text-gray-600">
                {error.category && `分類: ${error.category}`}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* 展開/收起按鈕 */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className={clsx(
                'p-1 rounded hover:bg-white/20 transition-colors',
                severityConfig.color
              )}
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>

            {/* 關閉按鈕 */}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className={clsx(
                  'p-1 rounded hover:bg-white/20 transition-colors',
                  severityConfig.color
                )}
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* 錯誤內容 */}
        <div className="px-4 py-3">
          {/* 錯誤消息 */}
          <div className="mb-3">
            <p className="text-gray-800 font-medium mb-2">
              {error.message || '發生未知錯誤'}
            </p>
            
            {error.context && isExpanded && (
              <div className="text-sm text-gray-600 bg-white/50 rounded p-2">
                <strong>錯誤上下文:</strong>
                <pre className="mt-1 text-xs overflow-x-auto">
                  {JSON.stringify(error.context, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {/* 恢復建議 */}
          {error.recovery && (
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-white/70 rounded-lg border">
                <RecoveryIcon className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-800">
                    建議的解決方案
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {error.recovery.message}
                  </div>

                  {/* 解決方案按鈕 */}
                  <div className="flex items-center space-x-2 mt-3">
                    {error.recovery.automatic && onRetry && (
                      <button
                        onClick={handleRetry}
                        disabled={isRetrying}
                        className={clsx(
                          'btn btn-sm flex items-center space-x-2',
                          isRetrying 
                            ? 'bg-gray-400 cursor-not-allowed' 
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        )}
                      >
                        {isRetrying ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            <span>處理中...</span>
                          </>
                        ) : (
                          <>
                            <RotateCcw className="w-4 h-4" />
                            <span>自動修復</span>
                          </>
                        )}
                      </button>
                    )}

                    {error.recovery.action === 'repair_environment' && onFixEnvironment && (
                      <button
                        onClick={handleFixEnvironment}
                        disabled={isRetrying}
                        className="btn btn-sm bg-green-600 hover:bg-green-700 text-white flex items-center space-x-2"
                      >
                        <Wrench className="w-4 h-4" />
                        <span>修復環境</span>
                      </button>
                    )}

                    {!error.recovery.automatic && (
                      <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        需要手動處理
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* 恢復進度指示器 */}
              {isRetrying && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="space-y-2"
                >
                  <div className="text-sm font-medium text-gray-700">恢復進度:</div>
                  <div className="space-y-1">
                    {[
                      { step: 1, label: '執行恢復策略', active: recoveryStep >= 1 },
                      { step: 2, label: '驗證修復結果', active: recoveryStep >= 2 },
                      { step: 3, label: '恢復完成', active: recoveryStep >= 3 }
                    ].map(({ step, label, active }) => (
                      <div 
                        key={step}
                        className="flex items-center space-x-2 text-sm"
                      >
                        <div className={clsx(
                          'w-4 h-4 rounded-full flex items-center justify-center text-xs',
                          active 
                            ? 'bg-green-500 text-white' 
                            : 'bg-gray-200 text-gray-500'
                        )}>
                          {recoveryStep === step && isRetrying ? (
                            <div className="w-2 h-2 border border-white border-t-transparent rounded-full animate-spin" />
                          ) : active ? (
                            <CheckCircle className="w-3 h-3" />
                          ) : (
                            step
                          )}
                        </div>
                        <span className={active ? 'text-gray-800' : 'text-gray-500'}>
                          {label}
                        </span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          )}

          {/* 詳細信息展開區域 */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 space-y-3"
              >
                {/* 錯誤統計 */}
                {error.frequency > 1 && (
                  <div className="bg-white/70 rounded-lg p-3 border">
                    <div className="flex items-center space-x-2 text-sm">
                      <AlertTriangle className="w-4 h-4 text-yellow-600" />
                      <span className="font-medium text-gray-800">
                        頻繁錯誤警告
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      此錯誤已發生 {error.frequency} 次，建議檢查系統配置
                    </div>
                  </div>
                )}

                {/* 解決方案列表 */}
                {error.categoryInfo?.solutions && (
                  <div className="bg-white/70 rounded-lg p-3 border">
                    <div className="text-sm font-medium text-gray-800 mb-2">
                      其他可能的解決方案:
                    </div>
                    <ul className="space-y-1 text-xs text-gray-600">
                      {error.categoryInfo.solutions.map((solution, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <span className="text-gray-400 mt-0.5">•</span>
                          <span>{solution}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 技術詳情 */}
                {error.stack && (
                  <div className="bg-white/70 rounded-lg p-3 border">
                    <div className="text-sm font-medium text-gray-800 mb-2">
                      技術詳情:
                    </div>
                    <pre className="text-xs text-gray-600 overflow-x-auto max-h-32">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 防護圖示裝飾 */}
        <div className="absolute top-2 right-2 opacity-10">
          <Shield className="w-8 h-8 text-gray-400" />
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ErrorHandlingPanel;