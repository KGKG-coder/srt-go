/**
 * 懶加載組件
 * 通過代碼分割減少初始包大小
 */
import { lazy } from 'react';

// 懶加載非關鍵組件
export const ErrorHandlingPanel = lazy(() => import('../components/ErrorHandlingPanel'));
export const PerformanceMonitor = lazy(() => import('../components/PerformanceMonitor'));
export const InstallationProgress = lazy(() => import('../components/InstallationProgress'));

// 重型組件懶加載
export const EnhancedProgressPanel = lazy(() => import('../components/EnhancedProgressPanel'));

// 服務相關組件懶加載
export const ServiceStatusDebug = lazy(() => import('../components/ServiceStatusDebug'));