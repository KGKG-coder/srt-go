/**
 * 性能優化工具
 * 包含動態加載、緩存和優化實用函數
 */

// 組件緩存
const componentCache = new Map();

/**
 * 緩存組件渲染結果
 * @param {string} key - 緩存鍵
 * @param {Function} renderFunction - 渲染函數
 * @returns {*} 渲染結果
 */
export const memoizeComponent = (key, renderFunction) => {
  if (componentCache.has(key)) {
    return componentCache.get(key);
  }
  
  const result = renderFunction();
  componentCache.set(key, result);
  return result;
};

/**
 * 清除組件緩存
 * @param {string} key - 要清除的緩存鍵（可選）
 */
export const clearComponentCache = (key = null) => {
  if (key) {
    componentCache.delete(key);
  } else {
    componentCache.clear();
  }
};

/**
 * 防抖函數
 * @param {Function} func - 要防抖的函數
 * @param {number} wait - 等待時間（毫秒）
 * @returns {Function} 防抖函數
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * 節流函數
 * @param {Function} func - 要節流的函數
 * @param {number} limit - 時間限制（毫秒）
 * @returns {Function} 節流函數
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * 動態加載CSS
 * @param {string} href - CSS文件路径
 */
export const loadCSS = (href) => {
  return new Promise((resolve, reject) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    link.onload = resolve;
    link.onerror = reject;
    document.head.appendChild(link);
  });
};

/**
 * 預加載圖片
 * @param {string[]} urls - 圖片URL數組
 */
export const preloadImages = (urls) => {
  return Promise.all(
    urls.map(url => 
      new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = resolve;
        img.onerror = reject;
        img.src = url;
      })
    )
  );
};

/**
 * 檢查是否為慢網絡連接
 */
export const isSlowConnection = () => {
  if ('connection' in navigator) {
    const connection = navigator.connection;
    return connection.effectiveType === 'slow-2g' || 
           connection.effectiveType === '2g' || 
           (connection.downlink && connection.downlink < 1.5);
  }
  return false;
};

/**
 * 記憶化生成器 - 用於昂貴的計算
 */
export const createMemoizer = () => {
  const cache = new Map();
  
  return (fn, keyGenerator) => {
    return (...args) => {
      const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
      
      if (cache.has(key)) {
        return cache.get(key);
      }
      
      const result = fn(...args);
      cache.set(key, result);
      return result;
    };
  };
};