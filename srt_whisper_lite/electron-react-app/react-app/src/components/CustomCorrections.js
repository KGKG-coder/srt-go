import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, Edit3, Save, X, ArrowRight } from 'lucide-react';
import clsx from 'clsx';
import { useI18n } from '../i18n/I18nContext';

const CustomCorrections = ({ corrections, onCorrectionsChange }) => {
  const { t, locale } = useI18n();
  const [editingIndex, setEditingIndex] = useState(-1);
  const [newCorrection, setNewCorrection] = useState({ find: '', replace: '' });
  const [isAdding, setIsAdding] = useState(false);

  // 添加新的修正規則
  const handleAddCorrection = () => {
    if (newCorrection.find.trim() && newCorrection.replace.trim()) {
      const updatedCorrections = [...corrections, { ...newCorrection, enabled: true }];
      onCorrectionsChange(updatedCorrections);
      setNewCorrection({ find: '', replace: '' });
      setIsAdding(false);
    }
  };

  // 編輯修正規則
  const handleEditCorrection = (index, field, value) => {
    const updatedCorrections = [...corrections];
    updatedCorrections[index] = { ...updatedCorrections[index], [field]: value };
    onCorrectionsChange(updatedCorrections);
  };

  // 刪除修正規則
  const handleDeleteCorrection = (index) => {
    const updatedCorrections = corrections.filter((_, i) => i !== index);
    onCorrectionsChange(updatedCorrections);
    setEditingIndex(-1);
  };

  // 切換規則啟用狀態
  const toggleCorrection = (index) => {
    const updatedCorrections = [...corrections];
    updatedCorrections[index].enabled = !updatedCorrections[index].enabled;
    onCorrectionsChange(updatedCorrections);
  };

  // 保存編輯
  const saveEdit = () => {
    setEditingIndex(-1);
  };

  // 根據介面語言動態生成預設修正規則建議
  const getDefaultSuggestions = (currentLocale) => {
    switch(currentLocale) {
      case 'en':
        return [
          { find: 'um', replace: '' },
          { find: 'uh', replace: '' },
          { find: 'you know', replace: '' },
          { find: 'I mean', replace: '' },
          { find: 'like,', replace: '' },
          { find: 'basically', replace: '' },
          { find: 'actually', replace: '' },
          { find: 'well,', replace: '' }
        ];
      default: // 'zh-TW' 和其他中文語系
        return [
          { find: '嗯', replace: '' },
          { find: '啊', replace: '' },
          { find: '那個', replace: '' },
          { find: '就是說', replace: '' },
          { find: '呃', replace: '' },
          { find: '然後', replace: '' },
          { find: 'basically', replace: '基本上' },
          { find: 'actually', replace: '實際上' }
        ];
    }
  };
  
  // 使用 useMemo 確保建議規則隨語言變化
  const defaultSuggestions = React.useMemo(() => {
    return getDefaultSuggestions(locale);
  }, [locale]);

  const addSuggestion = (suggestion) => {
    const exists = corrections.some(c => c.find === suggestion.find);
    if (!exists) {
      const updatedCorrections = [...corrections, { ...suggestion, enabled: true }];
      onCorrectionsChange(updatedCorrections);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="section-title">{t('corrections.title')}</h2>
        <p className="section-subtitle">
          {t('corrections.subtitle')}
        </p>
      </div>

      {/* 添加新規則 */}
      <div className="mb-6">
        <button
          onClick={() => setIsAdding(!isAdding)}
          className="btn btn-primary btn-md flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>{t('corrections.addRule')}</span>
        </button>

        <AnimatePresence>
          {isAdding && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 p-4 bg-gray-50 rounded-lg"
            >
              <div className="grid grid-cols-5 gap-3 items-end">
                <div className="col-span-2">
                  <label className="label">{t('corrections.originalText')}</label>
                  <input
                    type="text"
                    value={newCorrection.find}
                    onChange={(e) => setNewCorrection({ ...newCorrection, find: e.target.value })}
                    placeholder={t('corrections.originalText')}
                    className="input"
                  />
                </div>
                
                <div className="flex items-center justify-center">
                  <ArrowRight className="w-5 h-5 text-gray-400" />
                </div>
                
                <div className="col-span-2">
                  <label className="label">{t('corrections.replacementText')}</label>
                  <input
                    type="text"
                    value={newCorrection.replace}
                    onChange={(e) => setNewCorrection({ ...newCorrection, replace: e.target.value })}
                    placeholder={t('corrections.replaceHint')}
                    className="input"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-2 mt-4">
                <button
                  onClick={() => {
                    setIsAdding(false);
                    setNewCorrection({ find: '', replace: '' });
                  }}
                  className="btn btn-ghost btn-sm"
                >
                  {t('corrections.cancel')}
                </button>
                <button
                  onClick={handleAddCorrection}
                  disabled={!newCorrection.find.trim()}
                  className="btn btn-primary btn-sm"
                >
                  {t('corrections.add')}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 修正規則列表 */}
      <div className="space-y-3 mb-6">
        <h3 className="text-lg font-medium text-gray-900">
          {t('corrections.ruleCount')} ({corrections.length})
        </h3>

        {corrections.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <Edit3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">{t('corrections.noRules')}</p>
            <p className="text-sm text-gray-400 mt-1">
              {t('corrections.addRulesHint')}
            </p>
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto scrollbar-thin">
            <AnimatePresence>
              {corrections.map((correction, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className={clsx(
                    'p-4 bg-white border rounded-lg transition-all duration-200',
                    correction.enabled 
                      ? 'border-gray-200 hover:border-gray-300' 
                      : 'border-gray-100 bg-gray-50 opacity-60'
                  )}
                >
                  {editingIndex === index ? (
                    // 編輯模式
                    <div className="space-y-3">
                      <div className="grid grid-cols-5 gap-3 items-center">
                        <div className="col-span-2">
                          <input
                            type="text"
                            value={correction.find}
                            onChange={(e) => handleEditCorrection(index, 'find', e.target.value)}
                            className="input text-sm"
                            placeholder={t('corrections.originalText')}
                          />
                        </div>
                        
                        <div className="flex items-center justify-center">
                          <ArrowRight className="w-4 h-4 text-gray-400" />
                        </div>
                        
                        <div className="col-span-2">
                          <input
                            type="text"
                            value={correction.replace}
                            onChange={(e) => handleEditCorrection(index, 'replace', e.target.value)}
                            className="input text-sm"
                            placeholder={t('corrections.replacementText')}
                          />
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={correction.enabled}
                            onChange={() => toggleCorrection(index)}
                            className="rounded border-gray-300 text-primary-500 focus:ring-primary-200"
                          />
                          <span className="text-sm text-gray-600">{t('corrections.enable')}</span>
                        </label>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={saveEdit}
                            className="btn btn-primary btn-sm"
                          >
                            <Save className="w-3 h-3 mr-1" />
                            {t('corrections.save')}
                          </button>
                          <button
                            onClick={() => setEditingIndex(-1)}
                            className="btn btn-ghost btn-sm"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    // 顯示模式
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 flex-1 min-w-0">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={correction.enabled}
                            onChange={() => toggleCorrection(index)}
                            className="rounded border-gray-300 text-primary-500 focus:ring-primary-200"
                          />
                        </label>
                        
                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                          <span className={clsx(
                            'px-2 py-1 bg-red-100 text-red-700 text-sm rounded font-mono',
                            !correction.enabled && 'opacity-50'
                          )}>
                            {correction.find || t('corrections.empty')}
                          </span>
                          <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <span className={clsx(
                            'px-2 py-1 bg-green-100 text-green-700 text-sm rounded font-mono',
                            !correction.enabled && 'opacity-50'
                          )}>
                            {correction.replace || t('corrections.remove')}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-1 ml-4">
                        <button
                          onClick={() => setEditingIndex(index)}
                          className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                          title={t('corrections.edit')}
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteCorrection(index)}
                          className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                          title={t('corrections.delete')}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* 建議規則 */}
      {defaultSuggestions.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-3">{t('corrections.suggestions')}</h3>
          <p className="text-sm text-gray-600 mb-3">
            {t('corrections.suggestionsHint')}
          </p>
          
          <div className="flex flex-wrap gap-2">
            {defaultSuggestions.map((suggestion, index) => {
              const exists = corrections.some(c => c.find === suggestion.find);
              return (
                <button
                  key={index}
                  onClick={() => addSuggestion(suggestion)}
                  disabled={exists}
                  className={clsx(
                    'inline-flex items-center space-x-2 px-3 py-1.5 text-sm rounded-lg transition-all duration-200',
                    exists
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-primary-50 text-primary-700 hover:bg-primary-100 cursor-pointer'
                  )}
                >
                  <span className="font-mono">{suggestion.find}</span>
                  <ArrowRight className="w-3 h-3" />
                  <span className="font-mono">{suggestion.replace || `(${t('corrections.remove')})`}</span>
                  {!exists && <Plus className="w-3 h-3" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomCorrections;