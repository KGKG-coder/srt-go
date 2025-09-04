import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations, getBrowserLanguage, t } from './translations';

const I18nContext = createContext();

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
};

/**
 * 固定語言模式的 I18n Provider
 * 語言在安裝時確定，運行時不可更改
 */
export const I18nProvider = ({ children }) => {
  const [locale, setLocale] = useState('en'); // 預設語言
  const [isLoading, setIsLoading] = useState(true);

  // 載入語言配置
  useEffect(() => {
    const loadLanguageConfig = async () => {
      try {
        // 嘗試從多個位置讀取語言配置
        let config = null;
        
        // 1. 嘗試從 public 目錄讀取
        try {
          const response = await fetch('/language_config.json');
          if (response.ok) {
            config = await response.json();
          }
        } catch (e) {
          console.warn('無法從 public 目錄讀取語言配置');
        }
        
        // 2. 嘗試從 Electron 主進程讀取
        if (!config && window.electronAPI && window.electronAPI.getLanguageConfig) {
          try {
            config = await window.electronAPI.getLanguageConfig();
          } catch (e) {
            console.warn('無法從 Electron 主進程讀取語言配置');
          }
        }
        
        // 3. 檢查環境變數
        if (!config && process.env.REACT_APP_SRTGO_LANGUAGE) {
          config = {
            selectedLanguage: process.env.REACT_APP_SRTGO_LANGUAGE
          };
        }
        
        // 4. 最後備用：檢查 localStorage（向後相容）
        if (!config) {
          const savedLocale = localStorage.getItem('srtgo-locale');
          if (savedLocale && translations[savedLocale]) {
            config = {
              selectedLanguage: savedLocale
            };
          }
        }
        
        // 設置語言
        if (config && config.selectedLanguage && translations[config.selectedLanguage]) {
          setLocale(config.selectedLanguage);
          console.log(`🌐 載入固定語言設定: ${config.selectedLanguage}`);
        } else {
          // 如果沒有配置，使用瀏覽器語言作為預設
          const browserLang = getBrowserLanguage();
          setLocale(browserLang);
          console.log(`🌐 使用瀏覽器語言作為預設: ${browserLang}`);
        }
        
      } catch (error) {
        console.error('載入語言配置失敗:', error);
        // 錯誤情況下使用瀏覽器語言
        setLocale(getBrowserLanguage());
      } finally {
        setIsLoading(false);
      }
    };

    loadLanguageConfig();
  }, []);

  // 翻譯函數
  const translate = (key) => t(key, locale);

  // 獲取當前語言資訊
  const getCurrentLanguageInfo = () => {
    const languageMap = {
      'en': { code: 'en', name: 'English', flag: '🇺🇸', nativeName: 'English' },
      'zh-TW': { code: 'zh-TW', name: 'Traditional Chinese', flag: '🇹🇼', nativeName: '繁體中文' },
      'zh-CN': { code: 'zh-CN', name: 'Simplified Chinese', flag: '🇨🇳', nativeName: '简体中文' },
      'ja': { code: 'ja', name: 'Japanese', flag: '🇯🇵', nativeName: '日本語' },
      'ko': { code: 'ko', name: 'Korean', flag: '🇰🇷', nativeName: '한국어' }
    };
    
    return languageMap[locale] || languageMap['en'];
  };

  // 固定語言模式的值（移除語言切換功能）
  const value = {
    locale,
    t: translate,
    currentLanguage: getCurrentLanguageInfo(),
    isLoading,
    isFixed: true, // 標記為固定語言模式
    // 移除的功能
    setLocale: null, // 不提供語言切換功能
    supportedLanguages: null, // 不提供語言列表
    changeLanguage: null // 不提供語言切換功能
  };

  // 載入中顯示
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '16px',
        color: '#666'
      }}>
        <div>
          <div style={{ marginBottom: '10px' }}>🌐 Loading language settings...</div>
          <div style={{ fontSize: '14px' }}>載入語言設定中...</div>
        </div>
      </div>
    );
  }

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

// 匯出語言檢測函數供外部使用
export const detectAndSetLanguage = async () => {
  // 這個函數用於初始化時檢測語言
  try {
    const response = await fetch('/language_config.json');
    if (response.ok) {
      const config = await response.json();
      return config.selectedLanguage;
    }
  } catch (e) {
    console.warn('無法檢測語言配置，使用瀏覽器語言');
  }
  
  return getBrowserLanguage();
};

export default I18nContext;