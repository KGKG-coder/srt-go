import React, { createContext, useContext, useState, useEffect } from 'react';
import { getBrowserLanguage, t } from './translations';

const I18nContext = createContext();

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
};

export const I18nProvider = ({ children }) => {
  const [locale, setLocale] = useState(() => {
    // 從 localStorage 讀取保存的語言設置，否則自動檢測瀏覽器語言
    const savedLocale = localStorage.getItem('srtgo-locale');
    return savedLocale || getBrowserLanguage();
  });

  // 當語言改變時保存到 localStorage
  useEffect(() => {
    localStorage.setItem('srtgo-locale', locale);
  }, [locale]);

  // 翻譯函數
  const translate = (key) => t(key, locale);

  // 獲取支援的語言列表
  const supportedLanguages = [
    { code: 'zh-TW', name: '繁體中文', flag: '🇹🇼' },
    { code: 'zh-CN', name: '简体中文', flag: '🇨🇳' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'ko', name: '한국어', flag: '🇰🇷' }
  ];

  const value = {
    locale,
    setLocale,
    t: translate,
    supportedLanguages
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};