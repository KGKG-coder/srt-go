/**
 * 服務狀態調試組件
 * 用於開發和測試時檢查服務層整合狀態
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, AlertTriangle, CheckCircle, Info, 
  EyeOff, RefreshCw, Cpu, Zap 
} from 'lucide-react';
import clsx from 'clsx';
import { getUIServiceAdapter } from '../services/UIServiceAdapter';

const ServiceStatusDebug = ({ show = false, onToggle = null }) => {
  const [serviceAdapter] = useState(() => getUIServiceAdapter());
  const [statusData, setStatusData] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const updateStatus = () => {
      if (serviceAdapter) {
        const status = serviceAdapter.getServiceStatus();
        setStatusData(status);
        setLastUpdate(new Date().toLocaleTimeString());
      }
    };

    // 初始狀態
    updateStatus();

    // 設置定期更新
    const interval = setInterval(updateStatus, 2000);

    return () => clearInterval(interval);
  }, [serviceAdapter]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      if (serviceAdapter?.serviceReady) {
        await serviceAdapter.getEnvironmentStatus(true);
      }
      const status = serviceAdapter.getServiceStatus();
      setStatusData(status);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Status refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  if (!show) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-20 right-4 z-40 p-2 bg-gray-800 text-white rounded-lg shadow-lg hover:bg-gray-700 transition-colors"
        title="顯示服務狀態調試信息"
      >
        <Activity className="w-4 h-4" />
      </button>
    );
  }

  const getStatusIcon = (health) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'degraded':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'critical':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default:
        return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 300 }}
        className="fixed bottom-4 right-4 z-50 w-80 bg-white border border-gray-200 rounded-lg shadow-xl overflow-hidden"
      >
        {/* 標題欄 */}
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-900">
                服務狀態調試
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="p-1 rounded hover:bg-gray-200 transition-colors"
                title="刷新狀態"
              >
                <RefreshCw className={clsx(
                  'w-3 h-3 text-gray-600',
                  isRefreshing && 'animate-spin'
                )} />
              </button>
              <button
                onClick={onToggle}
                className="p-1 rounded hover:bg-gray-200 transition-colors"
                title="隱藏調試面板"
              >
                <EyeOff className="w-3 h-3 text-gray-600" />
              </button>
            </div>
          </div>
          {lastUpdate && (
            <div className="text-xs text-gray-500 mt-1">
              最後更新: {lastUpdate}
            </div>
          )}
        </div>

        {/* 狀態內容 */}
        <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
          {statusData ? (
            <>
              {/* 基本狀態 */}
              <div className="space-y-2">
                <div className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                  基本狀態
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span>初始化完成:</span>
                    <span className={clsx(
                      'font-medium',
                      statusData.initialized ? 'text-green-600' : 'text-red-600'
                    )}>
                      {statusData.initialized ? '是' : '否'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span>服務準備:</span>
                    <div className="flex items-center space-x-1">
                      {statusData.serviceReady ? (
                        <Zap className="w-3 h-3 text-green-600" />
                      ) : (
                        <Cpu className="w-3 h-3 text-yellow-600" />
                      )}
                      <span className={clsx(
                        'font-medium',
                        statusData.serviceReady ? 'text-green-600' : 'text-yellow-600'
                      )}>
                        {statusData.serviceReady ? '新服務層' : '傳統模式'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* UI 狀態 */}
              {statusData.uiState && (
                <div className="space-y-2">
                  <div className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                    UI 狀態
                  </div>
                  
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span>處理中:</span>
                      <span className={clsx(
                        'font-medium',
                        statusData.uiState.isProcessing ? 'text-blue-600' : 'text-gray-600'
                      )}>
                        {statusData.uiState.isProcessing ? '是' : '否'}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>進度:</span>
                      <span className="font-medium text-gray-900">
                        {Math.round(statusData.uiState.progress)}%
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>服務健康度:</span>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(statusData.uiState.serviceHealth)}
                        <span className="font-medium text-gray-900">
                          {statusData.uiState.serviceHealth}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 環境狀態 */}
              {statusData.environment && (
                <div className="space-y-2">
                  <div className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                    環境狀態
                  </div>
                  
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span>整體狀態:</span>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(statusData.environment.overall)}
                        <span className="font-medium text-gray-900">
                          {statusData.environment.overall}
                        </span>
                      </div>
                    </div>
                    
                    {statusData.environment.python && (
                      <div className="flex items-center justify-between">
                        <span>Python:</span>
                        <span className={clsx(
                          'font-medium',
                          statusData.environment.python.ready ? 'text-green-600' : 'text-red-600'
                        )}>
                          {statusData.environment.python.ready ? '就緒' : '未就緒'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 當前任務 */}
              {statusData.currentTask && (
                <div className="space-y-2">
                  <div className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                    當前任務
                  </div>
                  
                  <div className="text-xs text-gray-600 bg-gray-50 rounded p-2">
                    ID: {statusData.currentTask}
                  </div>
                </div>
              )}

              {/* 功能可用性 */}
              {serviceAdapter && (
                <div className="space-y-2">
                  <div className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                    功能可用性
                  </div>
                  
                  <div className="space-y-1 text-xs">
                    {Object.entries(serviceAdapter.getFeatureAvailability()).map(([feature, available]) => (
                      <div key={feature} className="flex items-center justify-between">
                        <span className="capitalize">
                          {feature.replace(/([A-Z])/g, ' $1').toLowerCase()}:
                        </span>
                        <span className={clsx(
                          'font-medium',
                          available ? 'text-green-600' : 'text-gray-400'
                        )}>
                          {available ? '可用' : '不可用'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <div className="text-sm">載入狀態數據中...</div>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ServiceStatusDebug;