/**
 * 生產環境安全的日誌系統
 * 在開發環境記錄詳細日誌，在生產環境僅記錄錯誤
 */

const isDevelopment = process.env.NODE_ENV === 'development';

class Logger {
  log(level, message, ...args) {
    if (isDevelopment) {
      console[level](`[${level.toUpperCase()}] ${message}`, ...args);
    } else if (level === 'error') {
      // 生產環境僅記錄錯誤
      console.error(`[ERROR] ${message}`, ...args);
    }
    // 生產環境靜默其他級別的日誌
  }

  debug(message, ...args) {
    this.log('log', message, ...args);
  }

  info(message, ...args) {
    this.log('info', message, ...args);
  }

  warn(message, ...args) {
    this.log('warn', message, ...args);
  }

  error(message, ...args) {
    this.log('error', message, ...args);
  }

  // Toast日誌（開發環境顯示，生產環境僅記錄錯誤類型）
  toast(type, message) {
    if (isDevelopment) {
      console.log(`Toast [${type}]: ${message}`);
    } else if (type === 'error') {
      console.error(`Toast Error: ${message}`);
    }
  }
}

const logger = new Logger();
export default logger;