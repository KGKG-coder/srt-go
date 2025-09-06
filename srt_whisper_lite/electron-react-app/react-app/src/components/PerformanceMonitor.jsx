import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Clock, TrendingUp, Gauge } from 'lucide-react';
import clsx from 'clsx';

const PerformanceMonitor = ({ 
  isProcessing = false, 
  currentRTF = null, 
  performanceMode = 'auto',
  processingTime = null,
  audioDuration = null 
}) => {
  const [rtfHistory, setRtfHistory] = useState([]);
  const [averageRTF, setAverageRTF] = useState(null);

  // RTF 性能等級定義
  const getPerformanceTier = (rtf) => {
    if (rtf <= 0.135) return { tier: '優秀級', color: 'green', bgColor: 'bg-green-50', textColor: 'text-green-700' };
    if (rtf <= 0.2) return { tier: '良好級', color: 'blue', bgColor: 'bg-blue-50', textColor: 'text-blue-700' };
    if (rtf <= 0.5) return { tier: '可接受級', color: 'yellow', bgColor: 'bg-yellow-50', textColor: 'text-yellow-700' };
    if (rtf <= 1.0) return { tier: '需改善級', color: 'orange', bgColor: 'bg-orange-50', textColor: 'text-orange-700' };
    return { tier: '需優化級', color: 'red', bgColor: 'bg-red-50', textColor: 'text-red-700' };
  };

  // 獲取性能模式資訊
  const getPerformanceModeInfo = (mode) => {
    switch(mode) {
      case 'gpu':
        return { icon: '⚡', name: 'GPU 加速', target: '≤0.067', color: 'blue' };
      case 'cpu':
        return { icon: '🖥️', name: 'CPU 優化', target: '≤0.135', color: 'gray' };
      default:
        return { icon: '🤖', name: '智能自動', target: '≤0.135', color: 'green' };
    }
  };

  // 更新RTF歷史記錄
  useEffect(() => {
    if (currentRTF !== null && currentRTF > 0) {
      setRtfHistory(prev => {
        const newHistory = [...prev, currentRTF].slice(-10); // 保留最近10個值
        const avg = newHistory.reduce((sum, rtf) => sum + rtf, 0) / newHistory.length;
        setAverageRTF(avg);
        return newHistory;
      });
    }
  }, [currentRTF]);

  const performanceInfo = getPerformanceModeInfo(performanceMode);
  const currentTier = currentRTF ? getPerformanceTier(currentRTF) : null;
  const averageTier = averageRTF ? getPerformanceTier(averageRTF) : null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl border border-slate-200 p-4 space-y-4"
    >
      {/* 標題區域 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-slate-600" />
          <h3 className="font-semibold text-slate-800">性能監控</h3>
        </div>
        
        {/* 狀態指示器 */}
        <div className="flex items-center space-x-2">
          <div className={clsx(
            "w-2 h-2 rounded-full",
            isProcessing ? "bg-green-500 animate-pulse" : "bg-gray-300"
          )} />
          <span className="text-sm text-slate-600">
            {isProcessing ? '處理中' : '待機'}
          </span>
        </div>
      </div>

      {/* 性能模式顯示 */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-white rounded-lg p-3 border border-slate-200">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-lg">{performanceInfo.icon}</span>
            <span className="text-sm font-medium text-slate-700">當前模式</span>
          </div>
          <div className="text-sm text-slate-600">{performanceInfo.name}</div>
          <div className="text-xs text-slate-500">目標 RTF: {performanceInfo.target}</div>
        </div>

        <div className="bg-white rounded-lg p-3 border border-slate-200">
          <div className="flex items-center space-x-2 mb-1">
            <Gauge className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-700">基準對比</span>
          </div>
          <div className="text-sm text-slate-600">基準: RTF 2.012</div>
          {averageRTF && (
            <div className="text-xs text-green-600">
              提升: {((2.012 - averageRTF) / 2.012 * 100).toFixed(1)}%
            </div>
          )}
        </div>
      </div>

      {/* RTF 性能指標 */}
      {(currentRTF !== null || averageRTF !== null) && (
        <div className="space-y-3">
          {/* 當前 RTF */}
          {currentRTF !== null && (
            <div className="bg-white rounded-lg p-3 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">當前 RTF</span>
                <span className={clsx(
                  "text-xs px-2 py-1 rounded-full",
                  currentTier.bgColor,
                  currentTier.textColor
                )}>
                  {currentTier.tier}
                </span>
              </div>
              
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-slate-800">
                  {currentRTF.toFixed(3)}
                </span>
                <span className="text-sm text-slate-500">RTF</span>
              </div>
              
              {/* RTF 進度條 */}
              <div className="mt-2">
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className={clsx(
                      "h-2 rounded-full transition-all duration-500",
                      currentRTF <= 0.135 ? "bg-green-500" :
                      currentRTF <= 0.2 ? "bg-blue-500" :
                      currentRTF <= 0.5 ? "bg-yellow-500" :
                      currentRTF <= 1.0 ? "bg-orange-500" : "bg-red-500"
                    )}
                    style={{ 
                      width: `${Math.min((1 - Math.min(currentRTF, 1)) * 100, 100)}%` 
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* 平均 RTF */}
          {averageRTF !== null && rtfHistory.length > 1 && (
            <div className="bg-white rounded-lg p-3 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">平均 RTF</span>
                <span className={clsx(
                  "text-xs px-2 py-1 rounded-full",
                  averageTier.bgColor,
                  averageTier.textColor
                )}>
                  {averageTier.tier}
                </span>
              </div>
              
              <div className="flex items-baseline space-x-2">
                <span className="text-xl font-bold text-slate-800">
                  {averageRTF.toFixed(3)}
                </span>
                <span className="text-sm text-slate-500">平均值 ({rtfHistory.length} 次)</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 處理時間統計 */}
      {processingTime !== null && audioDuration !== null && (
        <div className="bg-white rounded-lg p-3 border border-slate-200">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-700">處理統計</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-slate-500">音頻時長</div>
              <div className="font-medium">{audioDuration.toFixed(1)}s</div>
            </div>
            <div>
              <div className="text-slate-500">處理時間</div>
              <div className="font-medium">{processingTime.toFixed(1)}s</div>
            </div>
          </div>
        </div>
      )}

      {/* RTF 歷史趨勢 */}
      {rtfHistory.length > 2 && (
        <div className="bg-white rounded-lg p-3 border border-slate-200">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-700">性能趨勢</span>
          </div>
          
          <div className="flex items-end space-x-1 h-8">
            {rtfHistory.map((rtf, index) => (
              <div
                key={index}
                className={clsx(
                  "flex-1 rounded-sm transition-all duration-300",
                  rtf <= 0.135 ? "bg-green-400" :
                  rtf <= 0.2 ? "bg-blue-400" :
                  rtf <= 0.5 ? "bg-yellow-400" :
                  rtf <= 1.0 ? "bg-orange-400" : "bg-red-400"
                )}
                style={{ 
                  height: `${Math.max(8, Math.min(32, (1 - Math.min(rtf, 2)) * 24))}px` 
                }}
                title={`RTF: ${rtf.toFixed(3)}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* 性能建議 */}
      {currentRTF !== null && (
        <div className={clsx(
          "rounded-lg p-3 border",
          currentTier.bgColor,
          `border-${currentTier.color}-200`
        )}>
          <div className="text-sm">
            <div className={clsx("font-medium mb-1", currentTier.textColor)}>
              {currentRTF <= 0.135 ? "🎉 性能優秀" :
               currentRTF <= 0.2 ? "👍 性能良好" :
               currentRTF <= 1.0 ? "⚠️ 可考慮優化" : "🔧 建議檢查配置"}
            </div>
            <div className={clsx("text-xs", currentTier.textColor)}>
              {currentRTF <= 0.135 ? "當前配置已達最佳性能，適合批量處理" :
               currentRTF <= 0.2 ? "性能接近目標，可考慮升級硬體" :
               currentRTF <= 1.0 ? "建議檢查系統資源或嘗試CPU模式" : "建議檢查硬體配置或降低設置"}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default PerformanceMonitor;