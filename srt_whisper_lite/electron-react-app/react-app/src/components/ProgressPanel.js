import React from 'react';
import { motion } from 'framer-motion';
import { Play, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

const ProgressPanel = ({ progress, currentFile, totalFiles, status = 'processing', timeRemaining = null }) => {
  // 格式化時間
  const formatTime = (seconds) => {
    if (!seconds || seconds < 0) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 獲取狀態圖標和顏色
  const getStatusInfo = () => {
    switch (status) {
      case 'processing':
        return {
          icon: Play,
          color: 'text-primary-500',
          bgColor: 'bg-primary-50',
          borderColor: 'border-primary-200'
        };
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-500',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200'
        };
      case 'error':
        return {
          icon: AlertCircle,
          color: 'text-red-500',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200'
        };
      default:
        return {
          icon: Play,
          color: 'text-gray-500',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200'
        };
    }
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'card p-6 border-2',
        statusInfo.borderColor,
        statusInfo.bgColor
      )}
    >
      {/* 標題區域 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={clsx('p-2 rounded-lg', statusInfo.bgColor)}>
            <StatusIcon className={clsx('w-6 h-6', statusInfo.color)} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {status === 'processing' && '正在處理字幕'}
              {status === 'completed' && '處理完成'}
              {status === 'error' && '處理失敗'}
            </h3>
            <p className="text-sm text-gray-600">
              {status === 'processing' && `處理中 ${Math.round(progress)}%`}
              {status === 'completed' && '所有檔案已成功處理'}
              {status === 'error' && '處理過程中發生錯誤'}
            </p>
          </div>
        </div>

        {/* 時間資訊 */}
        {timeRemaining && status === 'processing' && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>預計剩餘: {formatTime(timeRemaining)}</span>
          </div>
        )}
      </div>

      {/* 進度條 */}
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
              status === 'error' && 'bg-red-500'
            )}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* 當前處理檔案 */}
      {currentFile && (
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

      {/* 狀態特定的額外資訊 */}
      {status === 'processing' && (
        <motion.div
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="mt-4 text-center text-sm text-gray-500"
        >
          請保持程式開啟，處理時間取決於檔案大小和模型選擇
        </motion.div>
      )}

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

      {status === 'error' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-4 p-3 bg-red-100 border border-red-200 rounded-lg"
        >
          <div className="flex items-center space-x-2 text-red-800">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-medium">
              處理過程中發生錯誤，請檢查檔案和設定
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ProgressPanel;