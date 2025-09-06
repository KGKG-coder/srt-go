import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, FolderOpen, Info, Zap, Globe, FileText, Languages, Mic, MessageSquare, Send, Bug, Lightbulb, HelpCircle } from 'lucide-react';
import clsx from 'clsx';
import { useI18n } from '../i18n/I18nContext';

const SettingsPanelComplete = ({ settings, onSettingsChange }) => {
  const { t, locale, setLocale, supportedLanguages } = useI18n();
  const [isSelectingFolder, setIsSelectingFolder] = useState(false);
  
  // Feedback form state
  const [feedbackForm, setFeedbackForm] = useState({
    type: 'bug',
    title: '',
    name: '',
    email: '',
    message: ''
  });
  const [feedbackErrors, setFeedbackErrors] = useState({});
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState(null);
  
  // 語言選項
  const languageOptions = [
    { value: 'auto', flag: '🌐' },
    { value: 'zh', flag: '🇨🇳' },
    { value: 'en', flag: '🇺🇸' },
    { value: 'ja', flag: '🇯🇵' },
    { value: 'ko', flag: '🇰🇷' }
  ];

  // 動態輸出選項
  const getOutputOptions = (audioLanguage) => {
    switch(audioLanguage) {
      case 'zh':
        return [
          { value: 'zh-TW', label: t('languages.zh-TW'), flag: '🇹🇼' },
          { value: 'zh-CN', label: t('languages.zh-CN'), flag: '🇨🇳' }
        ];
      case 'en':
        return [
          { value: 'same', label: t('settings.keepOriginal') + '（English）' }
        ];
      default:
        return [
          { value: 'same', label: t('settings.keepOriginal') }
        ];
    }
  };

  // 輸出格式選項
  const formatOptions = [
    { value: 'srt' },
    { value: 'vtt' },
    { value: 'txt' }
  ];

  // 處理設置變更
  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    onSettingsChange(newSettings);
  };

  // 處理語言選擇變更
  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    let defaultOutput = 'same';
    if (newLanguage === 'zh') {
      defaultOutput = 'zh-TW';
    }
    const newSettings = {
      ...settings,
      language: newLanguage,
      outputLanguage: defaultOutput
    };
    onSettingsChange(newSettings);
  };

  // 處理輸出語言變更
  const handleOutputLanguageChange = (e) => {
    handleSettingChange('outputLanguage', e.target.value);
  };

  // 選擇輸出資料夾
  const handleSelectFolder = async () => {
    if (window.electronAPI) {
      setIsSelectingFolder(true);
      try {
        const result = await window.electronAPI.selectFolder();
        if (result) {
          handleSettingChange('customDir', result);
        }
      } catch (error) {
        console.error('Folder selection failed:', error);
      } finally {
        setIsSelectingFolder(false);
      }
    }
  };
  
  // 驗證email格式
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };
  
  // 回報類型選項
  const feedbackTypes = [
    { value: 'bug', label: 'Bug 問題', icon: <Bug className="w-4 h-4" />, color: 'red' },
    { value: 'feature', label: '功能建議', icon: <Lightbulb className="w-4 h-4" />, color: 'blue' },
    { value: 'other', label: '其他', icon: <HelpCircle className="w-4 h-4" />, color: 'gray' }
  ];
  
  // 預設範本
  const templates = {
    bug: {
      title: '【Bug】',
      message: '問題描述：\n\n重現步驟：\n1. \n2. \n3. \n\n預期結果：\n\n實際結果：\n\n系統環境：'
    },
    feature: {
      title: '【功能建議】',
      message: '功能描述：\n\n使用場景：\n\n預期效益：'
    },
    other: {
      title: '',
      message: ''
    }
  };
  
  // 切換類型時應用範本
  const handleTypeChange = (type) => {
    setFeedbackForm(prev => ({
      ...prev,
      type,
      title: templates[type].title,
      message: templates[type].message
    }));
  };
  
  // 處理回報表單送出
  const handleFeedbackSubmit = async () => {
    setFeedbackErrors({});
    setFeedbackError(null);
    
    const errors = {};
    if (!feedbackForm.title.trim()) {
      errors.title = t('settings.feedbackRequired') || '此欄位為必填';
    }
    if (!feedbackForm.name.trim()) {
      errors.name = t('settings.feedbackRequired') || '此欄位為必填';
    }
    if (!feedbackForm.email.trim()) {
      errors.email = t('settings.feedbackRequired') || '此欄位為必填';
    } else if (!isValidEmail(feedbackForm.email.trim())) {
      errors.email = '請輸入有效的電子信箱格式';
    }
    if (!feedbackForm.message.trim()) {
      errors.message = t('settings.feedbackRequired') || '此欄位為必填';
    } else if (feedbackForm.message.trim().length > 2000) {
      errors.message = '內容不得超過 2000 字';
    }
    
    if (Object.keys(errors).length > 0) {
      setFeedbackErrors(errors);
      return;
    }
    
    setIsSubmittingFeedback(true);
    
    try {
      const embedColor = {
        bug: 15158332,
        feature: 3447003,
        other: 9807270
      }[feedbackForm.type];
      
      const typeLabel = {
        bug: '🐛 Bug 問題',
        feature: '💡 功能建議',
        other: '📝 其他回報'
      }[feedbackForm.type];
      
      const discordPayload = {
        embeds: [{
          title: `${typeLabel} - SRT GO 用戶回報`,
          color: embedColor,
          fields: [
            {
              name: '📝 標題',
              value: feedbackForm.title.trim(),
              inline: false
            },
            {
              name: '👤 聯絡人',
              value: feedbackForm.name.trim(),
              inline: true
            },
            {
              name: '📧 聯絡信箱',
              value: feedbackForm.email.trim(),
              inline: true
            },
            {
              name: '🏷️ 類型',
              value: typeLabel,
              inline: true
            },
            {
              name: '💬 詳細內容',
              value: feedbackForm.message.trim().substring(0, 1000) + 
                     (feedbackForm.message.trim().length > 1000 ? '...(內容過長，已截斷)' : ''),
              inline: false
            },
            {
              name: '⚙️ 系統資訊',
              value: `語言: ${locale}\nUser-Agent: ${navigator.userAgent.substring(0, 100)}\n版本: v2.2.1`,
              inline: false
            }
          ],
          timestamp: new Date().toISOString(),
          footer: {
            text: `SRT GO v2.2.1 用戶回報系統 | 字數: ${feedbackForm.message.trim().length}`
          }
        }]
      };
      
      const webhookUrl = 'https://discord.com/api/webhooks/1413541953316065382/-WyvN6D6EsZ3kgXsLyxxyX_-mHy14a13hcbFDwcDsZ6dfBMeKlkqNklnTfPll7qGcb13';
      
      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(discordPayload)
      });
      
      if (response.ok) {
        setFeedbackSubmitted(true);
        setFeedbackForm({ type: 'bug', title: '', name: '', email: '', message: '' });
        setFeedbackErrors({});
      } else {
        throw new Error(`Discord webhook failed with status: ${response.status}`);
      }
      
    } catch (error) {
      console.error('送出回報時發生錯誤:', error);
      setFeedbackError(error.message);
    } finally {
      setIsSubmittingFeedback(false);
    }
  };
  
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="section-title">{t('settings.title')}</h2>
        <p className="section-subtitle">
          {t('settings.subtitle')}
        </p>
      </div>
      
      <div className="space-y-8">
        {/* 介面語言設定 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <Languages className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">{t('settings.interfaceLanguage')}</label>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            {t('settings.interfaceLanguageDescription')}
          </p>
          
          <div className="grid grid-cols-2 gap-3">
            {supportedLanguages.map((lang) => (
              <label
                key={lang.code}
                className={clsx(
                  'flex items-center p-3 border rounded-lg cursor-pointer transition-all duration-200',
                  locale === lang.code
                    ? 'border-primary-300 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                )}
              >
                <input
                  type="radio"
                  name="interfaceLanguage"
                  value={lang.code}
                  checked={locale === lang.code}
                  onChange={(e) => setLocale(e.target.value)}
                  className="sr-only"
                />
                
                <div className="flex items-center space-x-3 flex-1">
                  <span className="text-xl">{lang.flag}</span>
                  <span className="font-medium text-gray-900">{lang.name}</span>
                </div>
                
                {locale === lang.code && (
                  <div className="w-3 h-3 bg-primary-500 rounded-full" />
                )}
              </label>
            ))}
          </div>
        </div>

        {/* AI 模型資訊 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <Zap className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">{t('settings.aiModel')}</label>
          </div>
          <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-900">{t('models.large.name')}</span>
              <span className="text-xs text-primary-600 bg-primary-100 px-2 py-1 rounded">
                {t('settings.professionalVersion') || '專業版'}
              </span>
            </div>
            <p className="text-sm text-gray-600">{t('models.large.description')}</p>
          </div>
        </div>

        {/* 音訊語言設定 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <Mic className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">{t('settings.audioLanguage') || '音訊語言'}</label>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            {t('settings.audioLanguageDesc') || '指定音訊語言以提高識別精度'}
          </p>
          <select
            value={settings.language}
            onChange={handleLanguageChange}
            className="input w-full"
          >
            {languageOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.flag} {t(`languages.${option.value}`)}
              </option>
            ))}
          </select>
        </div>

        {/* 動態輸出選項 */}
        {settings.language && settings.language !== 'auto' && (
          <div className="setting-item">
            <div className="flex items-center space-x-2 mb-3">
              <Globe className="w-5 h-5 text-primary-500" />
              <label className="text-lg font-medium text-gray-900">
                {t('settings.outputOptions') || '輸出選項'}
              </label>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              {settings.language === 'zh' 
                ? t('settings.chineseOptionsDesc') || '選擇繁體、簡體'
                : settings.language === 'en'
                ? t('settings.englishOptionsDesc') || '英文只能保留原文'
                : t('settings.translationOptionsDesc') || '選擇輸出格式'}
            </p>
            <select
              value={settings.outputLanguage}
              onChange={handleOutputLanguageChange}
              className="input w-full"
            >
              {getOutputOptions(settings.language).map(option => (
                <option key={option.value} value={option.value}>
                  {option.flag && `${option.flag} `}{option.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* 輸出格式設定 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <FileText className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">{t('settings.outputFormat')}</label>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            {t('settings.formatDescription')}
          </p>
          
          <div className="grid grid-cols-2 gap-3">
            {formatOptions.map((option) => (
              <label
                key={option.value}
                className={clsx(
                  'flex items-center p-3 border rounded-lg cursor-pointer transition-all duration-200',
                  settings.outputFormat === option.value
                    ? 'border-primary-300 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                )}
              >
                <input
                  type="radio"
                  name="format"
                  value={option.value}
                  checked={settings.outputFormat === option.value}
                  onChange={(e) => handleSettingChange('outputFormat', e.target.value)}
                  className="sr-only"
                />
                
                <div className="flex-1">
                  <div className="font-medium text-gray-900 mb-1">
                    {t(`formats.${option.value}.name`)}
                  </div>
                  <p className="text-xs text-gray-600">{t(`formats.${option.value}.description`)}</p>
                </div>
                
                {settings.outputFormat === option.value && (
                  <div className="ml-2 w-3 h-3 bg-primary-500 rounded-full" />
                )}
              </label>
            ))}
          </div>
        </div>

        {/* 輸出資料夾設定 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <FolderOpen className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">{t('settings.outputFolder')}</label>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            {t('settings.folderDescription')}
          </p>
          
          <div className="flex space-x-3">
            <input
              type="text"
              value={settings.customDir}
              onChange={(e) => handleSettingChange('customDir', e.target.value)}
              placeholder={t('settings.useDefault')}
              className="input flex-1"
              readOnly
            />
            <button
              onClick={handleSelectFolder}
              disabled={isSelectingFolder}
              className="btn btn-secondary btn-md flex-shrink-0"
            >
              {isSelectingFolder ? (
                <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <FolderOpen className="w-4 h-4" />
              )}
              <span className="ml-2">{t('settings.select')}</span>
            </button>
          </div>
        </div>

        {/* 進階選項 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <Settings className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">{t('settings.advanced')}</label>
          </div>
          
          <div className="space-y-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enableCorrections}
                onChange={(e) => handleSettingChange('enableCorrections', e.target.checked)}
                className="rounded border-gray-300 text-primary-500 focus:ring-primary-200"
              />
              <div>
                <div className="font-medium text-gray-900">{t('settings.enableCorrections')}</div>
                <div className="text-sm text-gray-600">{t('settings.correctionsDescription')}</div>
              </div>
            </label>
            
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.enable_gpu !== false}
                onChange={(e) => handleSettingChange('enable_gpu', e.target.checked)}
                className="rounded border-gray-300 text-primary-500 focus:ring-primary-200"
              />
              <div>
                <div className="font-medium text-gray-900">啟用GPU加速</div>
                <div className="text-sm text-gray-600">使用顯卡加速處理，需要支援CUDA的NVIDIA顯卡</div>
              </div>
            </label>
          </div>
        </div>
        
        {/* 建議與bug回報區塊 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <MessageSquare className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">
              {t('settings.feedback') || '建議與bug回報'}
            </label>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            {t('settings.feedbackSubtitle') || '向開發團隊回報問題或提供改進建議'}
          </p>
          
          {feedbackSubmitted ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-4 bg-green-50 border border-green-200 rounded-lg text-center"
            >
              <div className="flex items-center justify-center space-x-2 mb-2">
                <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="font-medium text-green-900">回報已送出</div>
              </div>
              <p className="text-sm text-green-700">感謝您的回報！我們會盡快處理您的意見。</p>
              <button
                onClick={() => {
                  setFeedbackSubmitted(false);
                  setFeedbackForm({ type: 'bug', title: '', name: '', email: '', message: '' });
                }}
                className="mt-3 text-sm text-green-600 hover:text-green-700 underline"
              >
                送出另一個回報
              </button>
            </motion.div>
          ) : feedbackError ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-4 bg-red-50 border border-red-200 rounded-lg"
            >
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div className="font-medium text-red-900">送出失敗</div>
              </div>
              <p className="text-sm text-red-700 mb-3">送出過程中發生錯誤，請稍後再試。</p>
              <button
                onClick={() => setFeedbackError(null)}
                className="text-sm text-red-600 hover:text-red-700 underline"
              >
                重新嘗試
              </button>
            </motion.div>
          ) : (
            <div className="space-y-4">
              {/* 回報類型選擇 */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  選擇回報類型
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {feedbackTypes.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => handleTypeChange(type.value)}
                      className={clsx(
                        'flex items-center justify-center space-x-2 p-2 border rounded-lg transition-all',
                        feedbackForm.type === type.value
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : 'border-gray-300 hover:border-gray-400'
                      )}
                    >
                      {type.icon}
                      <span className="text-sm">{type.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* 標題欄位 */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  {t('settings.feedbackTitle') || '標題'} <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={feedbackForm.title}
                  onChange={(e) => {
                    setFeedbackForm(prev => ({ ...prev, title: e.target.value }));
                    if (feedbackErrors.title) {
                      setFeedbackErrors(prev => ({ ...prev, title: null }));
                    }
                  }}
                  placeholder={t('settings.feedbackTitlePlaceholder') || '請簡述您的問題或建議'}
                  className={clsx(
                    'input w-full',
                    feedbackErrors.title ? 'border-red-300 focus:ring-red-200' : ''
                  )}
                />
                {feedbackErrors.title && (
                  <p className="text-sm text-red-600 mt-1">{feedbackErrors.title}</p>
                )}
              </div>
              
              {/* 稱呼欄位 */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  {t('settings.feedbackName') || '怎麼稱呼您'} <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={feedbackForm.name}
                  onChange={(e) => {
                    setFeedbackForm(prev => ({ ...prev, name: e.target.value }));
                    if (feedbackErrors.name) {
                      setFeedbackErrors(prev => ({ ...prev, name: null }));
                    }
                  }}
                  placeholder={t('settings.feedbackNamePlaceholder') || '您的稱呼或暱稱'}
                  className={clsx(
                    'input w-full',
                    feedbackErrors.name ? 'border-red-300 focus:ring-red-200' : ''
                  )}
                />
                {feedbackErrors.name && (
                  <p className="text-sm text-red-600 mt-1">{feedbackErrors.name}</p>
                )}
              </div>
              
              {/* Email欄位 */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  {t('settings.feedbackEmail') || '聯絡信箱'} <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={feedbackForm.email}
                  onChange={(e) => {
                    setFeedbackForm(prev => ({ ...prev, email: e.target.value }));
                    if (feedbackErrors.email) {
                      setFeedbackErrors(prev => ({ ...prev, email: null }));
                    }
                  }}
                  placeholder={t('settings.feedbackEmailPlaceholder') || '您的電子信箱'}
                  className={clsx(
                    'input w-full',
                    feedbackErrors.email ? 'border-red-300 focus:ring-red-200' : ''
                  )}
                />
                {feedbackErrors.email && (
                  <p className="text-sm text-red-600 mt-1">{feedbackErrors.email}</p>
                )}
              </div>
              
              {/* 詳細內容欄位 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    {t('settings.feedbackMessage') || '詳細內容'} <span className="text-red-500">*</span>
                  </label>
                  <span className="text-xs text-gray-500">
                    {feedbackForm.message.length}/2000 字
                  </span>
                </div>
                <textarea
                  value={feedbackForm.message}
                  onChange={(e) => {
                    if (e.target.value.length <= 2000) {
                      setFeedbackForm(prev => ({ ...prev, message: e.target.value }));
                      if (feedbackErrors.message) {
                        setFeedbackErrors(prev => ({ ...prev, message: null }));
                      }
                    }
                  }}
                  placeholder={t('settings.feedbackMessagePlaceholder') || '請詳細描述您遇到的問題或改進建議...'}
                  rows={6}
                  className={clsx(
                    'input w-full resize-none',
                    feedbackErrors.message ? 'border-red-300 focus:ring-red-200' : ''
                  )}
                />
                {feedbackErrors.message && (
                  <p className="text-sm text-red-600 mt-1">{feedbackErrors.message}</p>
                )}
              </div>
              
              {/* 送出按鈕 */}
              <button
                onClick={handleFeedbackSubmit}
                disabled={isSubmittingFeedback}
                className={clsx(
                  'w-full btn btn-primary btn-lg flex items-center justify-center space-x-2',
                  isSubmittingFeedback ? 'opacity-70 cursor-not-allowed' : ''
                )}
              >
                {isSubmittingFeedback ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>{t('settings.feedbackSubmitting') || '送出中...'}</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>{t('settings.feedbackSubmit') || '送出回報'}</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* 提醒訊息 */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <div className="font-medium text-blue-900 mb-1">{t('settings.tip')}</div>
            <div className="text-blue-700">
              {t('settings.modelDownloadTip')}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPanelComplete;