import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import clsx from 'clsx';

const Toast = ({ type = 'info', message, onClose, autoClose = true, duration = 5000 }) => {
  // 自動關閉
  useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, onClose]);

  // 獲取圖標和樣式
  const getToastConfig = () => {
    switch (type) {
      case 'success':
        return {
          icon: CheckCircle,
          className: 'toast-success',
          iconColor: 'text-green-500',
          textColor: 'text-green-800',
          titleColor: 'text-green-900'
        };
      case 'error':
        return {
          icon: AlertCircle,
          className: 'toast-error',
          iconColor: 'text-red-500',
          textColor: 'text-red-800',
          titleColor: 'text-red-900'
        };
      case 'warning':
        return {
          icon: AlertTriangle,
          className: 'toast-warning',
          iconColor: 'text-yellow-500',
          textColor: 'text-yellow-800',
          titleColor: 'text-yellow-900'
        };
      default:
        return {
          icon: Info,
          className: '',
          iconColor: 'text-blue-500',
          textColor: 'text-blue-800',
          titleColor: 'text-blue-900'
        };
    }
  };

  const config = getToastConfig();
  const Icon = config.icon;

  // 獲取標題
  const getTitle = () => {
    switch (type) {
      case 'success':
        return '成功';
      case 'error':
        return '錯誤';
      case 'warning':
        return '警告';
      default:
        return '提示';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.95 }}
      transition={{ 
        type: 'spring',
        stiffness: 400,
        damping: 25
      }}
      className={clsx('toast', config.className)}
    >
      <div className="flex items-start space-x-3">
        {/* 圖標 */}
        <div className="flex-shrink-0">
          <Icon className={clsx('w-5 h-5', config.iconColor)} />
        </div>

        {/* 內容 */}
        <div className="flex-1 min-w-0">
          <div className={clsx('font-medium text-sm mb-1', config.titleColor)}>
            {getTitle()}
          </div>
          <div className={clsx('text-sm', config.textColor)}>
            {message}
          </div>
        </div>

        {/* 關閉按鈕 */}
        {onClose && (
          <button
            onClick={onClose}
            className={clsx(
              'flex-shrink-0 p-1 rounded-lg transition-colors duration-200',
              'hover:bg-gray-100 focus:outline-none focus:bg-gray-100',
              config.textColor
            )}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 進度條（自動關閉時顯示） */}
      {autoClose && (
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-current opacity-20 rounded-b-lg"
          initial={{ width: '100%' }}
          animate={{ width: '0%' }}
          transition={{ duration: duration / 1000, ease: 'linear' }}
        />
      )}
    </motion.div>
  );
};

export default Toast;