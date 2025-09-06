import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, MessageSquare, Send, User, Mail, Type, FileText as Text, Bug, Lightbulb, HelpCircle } from 'lucide-react';
import clsx from 'clsx';
import { useI18n } from '../i18n/I18nContext';

const SettingsPanelSimplified = ({ settings, onSettingsChange }) => {
  const { t, locale } = useI18n();
  
  // Feedback form state
  const [feedbackForm, setFeedbackForm] = useState({
    type: 'bug', // bug, feature, other
    title: '',
    name: '',
    email: '',
    message: ''
  });
  const [feedbackErrors, setFeedbackErrors] = useState({});
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState(null);
  
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
    // 重置錯誤
    setFeedbackErrors({});
    setFeedbackError(null);
    
    // 驗證必填欄位
    const errors = {};
    if (!feedbackForm.title.trim()) {
      errors.title = '此欄位為必填';
    }
    if (!feedbackForm.name.trim()) {
      errors.name = '此欄位為必填';
    }
    if (!feedbackForm.email.trim()) {
      errors.email = '此欄位為必填';
    } else if (!isValidEmail(feedbackForm.email.trim())) {
      errors.email = '請輸入有效的電子信箱格式';
    }
    if (!feedbackForm.message.trim()) {
      errors.message = '此欄位為必填';
    } else if (feedbackForm.message.trim().length > 2000) {
      errors.message = '內容不得超過 2000 字';
    }
    
    if (Object.keys(errors).length > 0) {
      setFeedbackErrors(errors);
      return;
    }
    
    setIsSubmittingFeedback(true);
    
    try {
      // 根據類型設定顏色
      const embedColor = {
        bug: 15158332, // 紅色
        feature: 3447003, // 藍色
        other: 9807270 // 灰色
      }[feedbackForm.type];
      
      // 類型標籤
      const typeLabel = {
        bug: '🐛 Bug 問題',
        feature: '💡 功能建議',
        other: '📝 其他回報'
      }[feedbackForm.type];
      
      // 準備Discord webhook資料
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
      
      // 送出到Discord webhook
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
        <h2 className="section-title">{t('settings.title') || '設定'}</h2>
        <p className="section-subtitle">
          {t('settings.subtitle') || '調整設定以優化字幕生成'}
        </p>
      </div>
      
      <div className="space-y-8">
        {/* 建議與bug回報區塊 - 增強版 */}
        <div className="setting-item">
          <div className="flex items-center space-x-2 mb-3">
            <MessageSquare className="w-5 h-5 text-primary-500" />
            <label className="text-lg font-medium text-gray-900">
              {t('settings.feedback') || '建議與bug回報'}
            </label>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            {t('settings.feedbackSubtitle') || '向開發團隊回報問題或提供改進建議，幫助我們改善產品'}
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
                          ? `border-${type.color}-500 bg-${type.color}-50 text-${type.color}-700`
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
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    標題 <span className="text-red-500">*</span>
                  </label>
                </div>
                <input
                  type="text"
                  value={feedbackForm.title}
                  onChange={(e) => {
                    setFeedbackForm(prev => ({ ...prev, title: e.target.value }));
                    if (feedbackErrors.title) {
                      setFeedbackErrors(prev => ({ ...prev, title: null }));
                    }
                  }}
                  placeholder="請簡述您的問題或建議"
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
                  怎麼稱呼您 <span className="text-red-500">*</span>
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
                  placeholder="您的稱呼或暱稱"
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
                  聯絡信箱 <span className="text-red-500">*</span>
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
                  placeholder="您的電子信箱"
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
                    詳細內容 <span className="text-red-500">*</span>
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
                  placeholder="請詳細描述您遇到的問題或改進建議..."
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
                    <span>送出中...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>送出回報</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPanelSimplified;