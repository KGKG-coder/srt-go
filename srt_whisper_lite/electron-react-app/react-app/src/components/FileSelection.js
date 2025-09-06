import React, { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, File, X, FolderOpen, Check } from 'lucide-react';
import clsx from 'clsx';
import { useI18n } from '../i18n/I18nContext';

const FileSelection = ({ selectedFiles, onFilesChange, completedFiles = new Set() }) => {
  const { t } = useI18n();
  const [isDragOver, setIsDragOver] = useState(false);

  // 處理檔案拖拽
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    // 只有當離開拖拽區域本身時才設置為false
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setIsDragOver(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    console.log('Drop event triggered:', e.dataTransfer.files);
    
    const files = Array.from(e.dataTransfer.files).filter(file => {
      const ext = file.name.toLowerCase().split('.').pop();
      return ['mp4', 'mp3', 'wav', 'avi', 'mov', 'mkv', 'm4a', 'flac', 'ogg'].includes(ext);
    });

    console.log('Filtered files:', files);

    if (files.length > 0) {
      const fileObjects = files.map(file => ({
        path: file.path || file.webkitRelativePath || file.name,
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      }));
      console.log('File objects:', fileObjects);
      onFilesChange([...selectedFiles, ...fileObjects]);
    } else {
      console.warn('No valid files found in drop');
    }
  }, [selectedFiles, onFilesChange]);

  // 點擊選擇檔案
  const handleFileSelect = async () => {
    if (window.electronAPI) {
      try {
        const result = await window.electronAPI.selectFiles();
        if (result && result.length > 0) {
          const fileObjects = result.map(filePath => ({
            path: filePath,
            name: filePath.split('\\').pop() || filePath.split('/').pop(),
            size: 0, // Electron 會在處理時獲取實際大小
            type: '',
            lastModified: Date.now()
          }));
          onFilesChange([...selectedFiles, ...fileObjects]);
        }
      } catch (error) {
        console.error('File selection failed:', error);
      }
    }
  };

  // 移除檔案
  const removeFile = (index) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    onFilesChange(newFiles);
  };

  // 格式化檔案大小
  const formatFileSize = (bytes) => {
    if (bytes === 0) return t('fileSelection.unknownSize');
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // 獲取檔案類型圖標
  const getFileTypeIcon = (filename) => {
    const ext = filename.toLowerCase().split('.').pop();
    const videoExts = ['mp4', 'avi', 'mov', 'mkv'];
    const audioExts = ['mp3', 'wav', 'm4a', 'flac', 'ogg'];
    
    if (videoExts.includes(ext)) {
      return '🎬';
    } else if (audioExts.includes(ext)) {
      return '🎵';
    }
    return '📁';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="section-title">{t('fileSelection.title')}</h2>
        <p className="section-subtitle">
          {t('fileSelection.subtitle')}
        </p>
      </div>

      {/* 拖拽上傳區域 */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleFileSelect}
        className={clsx(
          'dropzone',
          'min-h-48 flex flex-col items-center justify-center p-8 mb-6 cursor-pointer',
          isDragOver && 'dropzone-active'
        )}
      >
        <motion.div
          animate={{ scale: isDragOver ? 1.05 : 1 }}
          transition={{ duration: 0.2 }}
          className="text-center"
        >
          <div className="mb-4">
            {isDragOver ? (
              <Upload className="w-16 h-16 text-primary-500 mx-auto" />
            ) : (
              <FolderOpen className="w-16 h-16 text-gray-400 mx-auto" />
            )}
          </div>
          
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isDragOver ? t('fileSelection.dropzoneActive') : t('fileSelection.dropzone')}
          </h3>
          
          <p className="text-gray-500 text-sm">
            {t('fileSelection.supportedFormats')}
          </p>
        </motion.div>
      </div>

      {/* 已選檔案列表 */}
      {selectedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            {t('fileSelection.selectedFiles')} ({selectedFiles.length})
          </h3>
          
          <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin">
            {selectedFiles.map((file, index) => (
              <motion.div
                key={`${file.path}-${index}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={clsx(
                  "file-item group relative overflow-hidden",
                  completedFiles.has(file.name) && "bg-primary-50 border-primary-200"
                )}
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <span className="text-2xl flex-shrink-0">
                    {getFileTypeIcon(file.name)}
                  </span>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {completedFiles.has(file.name) && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="flex items-center justify-center w-8 h-8 bg-primary-500 rounded-full"
                    >
                      <Check className="w-5 h-5 text-white" />
                    </motion.div>
                  )}
                  
                  <button
                    onClick={() => removeFile(index)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all duration-200"
                    title={t('fileSelection.removeFile')}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* 空狀態提示 */}
      {selectedFiles.length === 0 && (
        <div className="text-center py-8">
          <File className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">{t('fileSelection.noFiles')}</p>
          <p className="text-sm text-gray-400 mt-1">
            {t('fileSelection.startUpload')}
          </p>
        </div>
      )}
    </div>
  );
};

export default FileSelection;