import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Zap, CheckCircle, FileText, Square } from 'lucide-react';
import clsx from 'clsx';

// Core component imports (immediate load)
import FileSelection from './components/FileSelection';
import CustomCorrections from './components/CustomCorrections';
import SettingsPanel from './components/SettingsPanelComplete';
import Toast from './components/Toast';

// Lazy loaded components (code splitting)
import {
  ErrorHandlingPanel,
  PerformanceMonitor,
  InstallationProgress,
  EnhancedProgressPanel
} from './utils/lazyImports';

// Service layer imports
import { getUIServiceAdapter } from './services/UIServiceAdapter';

// Multi-language support
import { I18nProvider, useI18n } from './i18n/I18nContext';

// Logging system and error handling
import logger from './utils/logger';
import { useErrorHandler } from './hooks/useErrorHandler';

// Enhanced error handling utility functions with IPC serialization support
const formatErrorMessage = (error) => {
  if (!error) return 'Unknown error';
  
  // If it's a string, return directly
  if (typeof error === 'string') {
    return error;
  }
  
  // If it's an Error object, extract useful information
  if (error instanceof Error) {
    return error.message || error.toString();
  }
  
  // If it's a plain object, extract key information
  if (typeof error === 'object') {
    // Handle IPC-serialized error objects (our new format)
    if (error.success === false && error.message) {
      return String(error.message);
    }
    
    // Try to extract common error properties
    if (error.message) {
      return String(error.message);
    }
    if (error.error) {
      return formatErrorMessage(error.error);
    }
    if (error.details) {
      return String(error.details);
    }
    if (error.reason) {
      return String(error.reason);
    }
    if (error.description) {
      return String(error.description);
    }
    
    // Handle Electron IPC error format
    if (error.code && error.timestamp) {
      const msg = error.message || 'Processing error occurred';
      return `${msg} (Code: ${error.code})`;
    }
    
    // Try JSON serialization, fallback to toString if failed
    try {
      const serialized = JSON.stringify(error, null, 2);
      // If serialization succeeds and is not empty object, extract useful info
      if (serialized !== '{}' && serialized !== 'null') {
        // For debugging: limit the size of JSON output
        if (serialized.length > 200) {
          return `Error object (${Object.keys(error).join(', ')})`;
        }
        return serialized;
      }
    } catch (e) {
      // JSON serialization failed, use toString
    }
    
    // Final fallback for objects
    const objectType = error.constructor ? error.constructor.name : 'Object';
    return `${objectType} error occurred`;
  }
  
  // Other types, convert to string
  return String(error);
};

// Safe Toast display function
const showSafeToast = (setToast, type, message) => {
  const safeMessage = formatErrorMessage(message);
  logger.toast(type, safeMessage);
  setToast({ type, message: safeMessage, id: Date.now() });
  setTimeout(() => setToast(null), 5000);
};

function AppContent() {
  const { t } = useI18n();
  
  // State management
  const [activeTab, setActiveTab] = useState('files'); // files, corrections, settings
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [completedFiles, setCompletedFiles] = useState(new Set());
  const [toast, setToast] = useState(null);
  const [settings, setSettings] = useState({
    model: 'large',  // Force use LARGE model - not changeable
    language: 'auto',
    outputLanguage: 'same', // Add output language setting
    outputFormat: 'srt',
    customDir: '',
    enableCorrections: true,
    performanceMode: 'auto'  // Performance optimization mode
  });
  const [corrections, setCorrections] = useState([]);
  
  // New service layer state
  const [serviceAdapter] = useState(() => getUIServiceAdapter());
  const [showProgressPanel, setShowProgressPanel] = useState(false);
  
  // Enhanced error handling
  const {
    currentError,
    isRecovering,
    handleError,
    retry: retryError,
    clearError,
    canAutoRecover
  } = useErrorHandler({
    maxRetries: 3,
    onSettingsUpdate: (newSettings) => {
      setSettings(prev => ({ ...prev, ...newSettings }));
    },
    currentSettings: settings
  });
  
  // Performance monitoring state
  const [performanceData, setPerformanceData] = useState({
    currentRTF: null,
    processingTime: null,
    audioDuration: null,
    startTime: null
  });

  // Use safe Toast function
  const showToast = (type, message) => {
    showSafeToast(setToast, type, message);
  };

  // Force ensure model setting is large - Large-v3 special edition
  useEffect(() => {
    if (settings.model !== 'large') {
      logger.warn('[Large-v3] Model setting corrected to large for optimal performance');
      const correctedSettings = { ...settings, model: 'large' };
      setSettings(correctedSettings);
      localStorage.setItem('srtgo-settings', JSON.stringify(correctedSettings));
    }
  }, [settings.model, settings]);

  // New service layer initialization and event listening
  useEffect(() => {
    const initializeServiceAdapter = async () => {
      try {
        // Wait for service adapter initialization
        await serviceAdapter.initialize();
        
        // Setup service layer event listening
        serviceAdapter.on('progressUpdate', (data) => {
          if (!isPaused) {
            setProgress(data.percent || 0);
            setCurrentFile(data.filename || '');
            
            // Update real-time RTF for service adapter
            if ((data.percent || 0) > 0) {
              setPerformanceData(prev => {
                const currentTime = Date.now();
                const elapsedTime = prev.startTime ? (currentTime - prev.startTime) / 1000 : null;
                
                if (elapsedTime && prev.audioDuration) {
                  // Calculate estimated total processing time based on progress
                  const estimatedTotalTime = (elapsedTime / (data.percent || 1)) * 100;
                  const rtf = estimatedTotalTime / prev.audioDuration;
                  
                  return {
                    ...prev,
                    currentRTF: rtf
                  };
                }
                
                return prev;
              });
            }
            
            if (data.status === 'completed') {
              setCompletedFiles(prev => new Set([...prev, data.filename]));
              setCurrentFileIndex(prev => prev + 1);
            }
          }
        });

        serviceAdapter.on('taskCompleted', (result) => {
          setIsProcessing(false);
          setIsPaused(false);
          setProgress(100);
          setShowProgressPanel(false);
          
          // Update performance monitoring
          setPerformanceData(prev => {
            const processingTime = prev.startTime ? (Date.now() - prev.startTime) / 1000 : null;
            const rtf = processingTime && prev.audioDuration ? processingTime / prev.audioDuration : null;
            
            return {
              ...prev,
              processingTime,
              currentRTF: rtf
            };
          });
          
          if (result.success && result.result?.results) {
            setCompletedFiles(prev => {
              const newCompletedFiles = new Set(prev);
              result.result.results.forEach(r => {
                if (r.success && r.input) {
                  const filename = r.input.split('\\').pop() || r.input.split('/').pop();
                  newCompletedFiles.add(filename);
                }
              });
              return newCompletedFiles;
            });
          }
          
          const message = result.message || 
            (result.success ? `Successfully generated ${result.result?.successful || 0} subtitle files` : 'Processing failed');
          
          showToast(result.success ? 'success' : 'error', message);
        });

        serviceAdapter.on('taskFailed', (result) => {
          setIsProcessing(false);
          setIsPaused(false);
          setShowProgressPanel(false);
          
          // Enhanced error handling
          const errorInfo = {
            message: formatErrorMessage(result.error),
            category: result.error?.category || 'unknown',
            severity: 'high'
          };
          
          handleError(new Error(errorInfo.message), { category: errorInfo.category, severity: errorInfo.severity });
          showToast('error', errorInfo.message);
        });

        serviceAdapter.on('serviceError', (data) => {
          handleError(new Error(data.message), { category: data.category, recovery: data.recovery, severity: 'high' });
        });

        // Get initial service status
        serviceAdapter.getServiceStatus();
        
      } catch (error) {
        console.warn('Service adapter initialization failed, using legacy mode:', error);
      }
    };

    initializeServiceAdapter();

    // Check if electronAPI is available
    if (!window.electronAPI) {
      console.error('window.electronAPI is undefined!');
      logger.debug('Window object initialized');
      
      // Development environment fallback
      if (process.env.NODE_ENV === 'development') {
        console.warn('Creating mock electronAPI for development');
        window.electronAPI = {
          processFiles: async (options) => {
            logger.debug('Mock processFiles called:', options);
            return Promise.reject(new Error('ElectronAPI not available in development mode'));
          },
          selectFiles: async () => {
            logger.debug('Mock selectFiles called');
            return [];
          },
          onProgress: () => {},
          onComplete: () => {},
          onError: () => {},
          onInstallationProgress: () => {},
          removeProgressListeners: () => {},
          store: {
            get: async () => null,
            set: async () => {},
            delete: async () => {}
          }
        };
      }
    } else {
      logger.info('ElectronAPI loaded successfully');
    }

    // Traditional IPC event listening (backward compatibility)
    if (window.electronAPI) {
      // Listen for processing progress (legacy mode)
      window.electronAPI.onProgress((progress) => {
        if (!serviceAdapter.serviceReady && !isPaused) {
          setProgress(progress.percent);
          setCurrentFile(progress.filename);
          
          // Update real-time RTF if processing time is available
          if (progress.percent > 0) {
            setPerformanceData(prev => {
              const currentTime = Date.now();
              const elapsedTime = prev.startTime ? (currentTime - prev.startTime) / 1000 : null;
              
              if (elapsedTime && prev.audioDuration) {
                // Calculate estimated total processing time based on progress
                const estimatedTotalTime = (elapsedTime / progress.percent) * 100;
                const rtf = estimatedTotalTime / prev.audioDuration;
                
                return {
                  ...prev,
                  currentRTF: rtf
                };
              }
              
              return prev;
            });
          }
          
          if (progress.status === 'completed') {
            setCompletedFiles(prev => new Set([...prev, progress.filename]));
            setCurrentFileIndex(prev => prev + 1);
          }
        }
      });

      // Listen for processing completion (legacy mode)
      window.electronAPI.onComplete((result) => {
        if (!serviceAdapter.serviceReady) {
          setIsProcessing(false);
          setIsPaused(false);
          setProgress(100);
          setShowProgressPanel(false);
          
          // Update performance monitoring
          setPerformanceData(prev => {
            const processingTime = prev.startTime ? (Date.now() - prev.startTime) / 1000 : null;
            const rtf = processingTime && prev.audioDuration ? processingTime / prev.audioDuration : null;
            
            return {
              ...prev,
              processingTime,
              currentRTF: rtf
            };
          });
          
          const isSuccess = result.success !== undefined 
            ? result.success 
            : (result.successful > 0 && result.results && result.results.every(r => r.success));
          
          if (isSuccess && result.results) {
            setCompletedFiles(prev => {
              const newCompletedFiles = new Set(prev);
              result.results.forEach(r => {
                if (r.success && r.input) {
                  const filename = r.input.split('\\').pop() || r.input.split('/').pop();
                  newCompletedFiles.add(filename);
                }
              });
              return newCompletedFiles;
            });
          }
          
          const message = result.message || 
            (isSuccess ? `Successfully generated ${result.successful || result.results?.length || 0} subtitle files` : 'Processing failed');
          
          showToast(isSuccess ? 'success' : 'error', message);
        }
      });

      // Enhanced error listening (legacy mode)
      window.electronAPI.onError((error) => {
        if (!serviceAdapter.serviceReady) {
          setIsProcessing(false);
          setIsPaused(false);
          setShowProgressPanel(false);
          
          const errorInfo = {
            message: formatErrorMessage(error),
            category: 'unknown',
            severity: 'high'
          };
          
          handleError(new Error(errorInfo.message), { category: errorInfo.category, severity: errorInfo.severity });
          showToast('error', errorInfo.message);
        }
      });
    }

    // Load saved settings and correction rules
    loadSettings();
    loadCorrections();

    // Cleanup function
    return () => {
      if (serviceAdapter) {
        serviceAdapter.removeAllListeners();
      }
    };
  }, [serviceAdapter, isPaused]);

  // Load settings
  const loadSettings = () => {
    logger.debug('=== loadSettings called ===');
    const savedSettings = localStorage.getItem('srtgo-settings');
    logger.debug('Saved settings from localStorage:', savedSettings);
    
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings);
      logger.debug('Parsed settings:', parsed);
      
      // Use saved settings directly, no forced language reset
      logger.debug('Using settings as saved (no language reset):', parsed);
      setSettings(parsed);
    } else {
      // If no saved settings, use defaults
      const defaultSettings = {
        model: 'large',  // Force use LARGE model - not changeable
        language: 'auto',
        outputLanguage: 'same',
        outputFormat: 'srt',
        customDir: '',
        enableCorrections: true
      };
      logger.debug('No saved settings, using defaults:', defaultSettings);
      setSettings(defaultSettings);
    }
  };

  // Save settings
  const saveSettings = (newSettings) => {
    logger.debug('=== saveSettings called ===');
    logger.debug('Current settings before save:', settings);
    logger.debug('New settings to save:', newSettings);
    
    setSettings(newSettings);
    localStorage.setItem('srtgo-settings', JSON.stringify(newSettings));
    
    logger.debug('Settings saved to localStorage');
    
    // Verification save
    setTimeout(() => {
      const saved = localStorage.getItem('srtgo-settings');
      logger.debug('Verification - saved settings in localStorage:', saved);
    }, 100);
  };

  // Load correction rules
  const loadCorrections = () => {
    const savedCorrections = localStorage.getItem('srtgo-corrections');
    if (savedCorrections) {
      setCorrections(JSON.parse(savedCorrections));
    }
  };

  // Save correction rules
  const saveCorrections = (newCorrections) => {
    setCorrections(newCorrections);
    localStorage.setItem('srtgo-corrections', JSON.stringify(newCorrections));
  };

  // Enhanced processing start function
  // Helper function to estimate total audio duration
  const extractTotalAudioDuration = async (files) => {
    try {
      // For now, use a practical estimation approach
      // In the future, this could be enhanced with Electron API to get actual file metadata
      let totalDuration = 0;
      
      for (const filePath of files) {
        // Estimate duration based on file extension and common patterns
        const fileName = filePath.toLowerCase();
        
        if (fileName.includes('test') || fileName.includes('sample')) {
          // Test files are usually short
          totalDuration += 15;
        } else if (fileName.includes('song') || fileName.includes('music')) {
          // Music files are typically longer
          totalDuration += 180; // 3 minutes average
        } else {
          // General audio/video files
          totalDuration += 60; // 1 minute average
        }
      }
      
      return totalDuration > 0 ? totalDuration : null;
    } catch (error) {
      console.warn('Failed to estimate total audio duration:', error);
      // Ultimate fallback: 1 minute per file
      return files.length * 60;
    }
  };

  const handleStartProcessing = async () => {
    // Check if electronAPI is available
    if (!window.electronAPI || !window.electronAPI.processFiles) {
      showToast('error', 'Electron API not available. Please restart the application.');
      console.error('ElectronAPI not available:', window.electronAPI);
      return;
    }

    if (selectedFiles.length === 0) {
      showToast('warning', t('toast.selectFiles'));
      return;
    }

    // Reset state
    setIsProcessing(true);
    setIsPaused(false);
    setProgress(0);
    setCurrentFile('');
    setCurrentFileIndex(0);
    setCompletedFiles(new Set());
    clearError();
    setShowProgressPanel(true);
    
    // Initialize performance monitoring and extract audio duration
    const totalAudioDuration = await extractTotalAudioDuration(selectedFiles);
    setPerformanceData({
      currentRTF: null,
      processingTime: null,
      audioDuration: totalAudioDuration,
      startTime: Date.now()
    });

    try {
      // Prefer new service layer
      if (serviceAdapter.serviceReady) {
        await serviceAdapter.startSubtitleProcessing({
          files: selectedFiles,
          settings,
          corrections: settings.enableCorrections ? corrections : []
        });
      } else {
        // Fallback to legacy mode
        await window.electronAPI.processFiles({
          files: selectedFiles,
          settings,
          corrections: settings.enableCorrections ? corrections : []
        });
      }
    } catch (error) {
      logger.error('processFiles error:', error);
      
      // Check if error is due to stop operation
      if (isPaused || (error && (error.paused || error.stopped))) {
        logger.info('Processing interrupted by stop operation');
        return;
      }
      
      setIsProcessing(false);
      setShowProgressPanel(false);
      
      // Enhanced error message formatting with IPC debugging
      const errorMessage = formatErrorMessage(error);
      logger.error('Raw error object received:', error);
      logger.error('Formatted error message:', errorMessage);
      
      // Handle error with enhanced error handler
      await handleError(error, {
        operation: 'file_processing',
        files: selectedFiles,
        settings: settings
      });
      
      // Use safe error display
      const toastMessage = t('toast.processingFailed') ? 
        t('toast.processingFailed') + ': ' + errorMessage : 
        'Processing failed: ' + errorMessage;
      
      showToast('error', toastMessage);
    }
  };

  // Stop processing (integrate new service layer)
  const handleStopProcessing = async () => {
    logger.info('Stop processing request');
    
    try {
      setIsPaused(true);
      
      // Prefer new service layer
      if (serviceAdapter.serviceReady) {
        await serviceAdapter.stopProcessing();
      } else {
        // Fallback to legacy mode
        if (window.electronAPI.pauseProcessing) {
          await window.electronAPI.pauseProcessing();
        }
      }
      
      // Update state
      setIsProcessing(false);
      setProgress(0);
      setCurrentFile('');
      setCurrentFileIndex(0);
      setShowProgressPanel(false);
      
      logger.info('Processing stopped');
      showToast('info', 'Processing stopped');
      
    } catch (error) {
      logger.error('Stop processing error:', error);
      // Force stop
      setIsProcessing(false);
      setProgress(0);
      setCurrentFile('');
      setCurrentFileIndex(0);
      setShowProgressPanel(false);
    }
  };

  // Tab configuration
  const tabs = [
    { id: 'files', label: t('tabs.files'), icon: Zap },
    { id: 'corrections', label: t('tabs.corrections'), icon: FileText },
    { id: 'settings', label: t('tabs.settings'), icon: Settings }
  ];


  // Helper function: format progress status
  const getProgressStatus = () => {
    if (completedFiles.size === selectedFiles.length && selectedFiles.length > 0) {
      return 'completed';
    } else if (currentError) {
      return 'error';
    } else if (isProcessing) {
      return 'processing';
    } else {
      return 'idle';
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans">
      {/* Fixed header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* LOGO and title */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-gray-900">{t('app.title')}</h1>
                <p className="text-sm text-gray-500">{t('app.subtitle')}</p>
              </div>
            </div>
            
            {/* Processing button */}
            <div className="flex items-center space-x-3">
              <button
                onClick={handleStartProcessing}
                disabled={isProcessing || selectedFiles.length === 0}
                className={clsx(
                  'btn btn-primary btn-lg',
                  'flex items-center space-x-2',
                  (isProcessing || selectedFiles.length === 0) && 'opacity-50 cursor-not-allowed'
                )}
              >
                {isProcessing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>{isPaused ? t('app.paused') : t('app.processing')}</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span>{t('app.startProcessing')}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content area - add spacing for fixed header and footer */}
      <main 
        className="max-w-7xl mx-auto px-6 py-8" 
        style={{ 
          paddingTop: '100px',
          paddingBottom: isProcessing ? '120px' : '20px'
        }}
      >
        <div className="grid grid-cols-12 gap-8">
          {/* Side navigation */}
          <aside className="col-span-3">
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={clsx(
                      'w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200',
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-600 border-r-2 border-primary-500'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* File statistics */}
            {selectedFiles.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 bg-gray-50 rounded-lg"
              >
                <div className="text-sm text-gray-600 mb-1">{t('fileSelection.filesSelected')}</div>
                <div className="text-2xl font-semibold text-gray-900">{selectedFiles.length}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {selectedFiles.reduce((total, file) => total + (file.size || 0), 0) > 0 && 
                    `${t('fileSelection.totalSize')}: ${(selectedFiles.reduce((total, file) => total + (file.size || 0), 0) / 1024 / 1024).toFixed(1)} MB`
                  }
                </div>
              </motion.div>
            )}
          </aside>

          {/* Main content panel */}
          <div className="col-span-9 space-y-6">
            {/* Error handling panel */}
            <AnimatePresence>
              {currentError && (
                <Suspense fallback={<div className="error-panel-loading">Loading error panel...</div>}>
                  <ErrorHandlingPanel
                    error={currentError}
                    onRetry={retryError}
                    onDismiss={clearError}
                    onFixEnvironment={async () => {
                      if (serviceAdapter.serviceReady) {
                        try {
                          await serviceAdapter.getEnvironmentStatus(true);
                          clearError();
                          showToast('success', 'Environment status updated');
                        } catch (error) {
                          console.error('Environment fix failed:', error);
                        }
                      }
                    }}
                  />
                </Suspense>
              )}
            </AnimatePresence>

            {/* Enhanced progress panel */}
            <AnimatePresence>
              {(showProgressPanel || currentError || completedFiles.size > 0) && (
                <Suspense fallback={<div className="card p-6 animate-pulse bg-gray-50">{t('common.loading')}</div>}>
                  <EnhancedProgressPanel
                    progress={progress}
                    currentFile={currentFile}
                    totalFiles={selectedFiles.length}
                    status={getProgressStatus()}
                    onRetry={retryError}
                  />
                </Suspense>
              )}
            </AnimatePresence>

            {/* Main function panel */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl card"
              >
                {activeTab === 'files' && (
                  <FileSelection
                    selectedFiles={selectedFiles}
                    onFilesChange={setSelectedFiles}
                    completedFiles={completedFiles}
                  />
                )}
                
                {activeTab === 'corrections' && (
                  <CustomCorrections
                    corrections={corrections}
                    onCorrectionsChange={saveCorrections}
                  />
                )}
                
                {activeTab === 'settings' && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2">
                      <SettingsPanel
                        settings={settings}
                        onSettingsChange={saveSettings}
                      />
                    </div>
                    <div className="lg:col-span-1">
                      <Suspense fallback={<div className="card p-6 animate-pulse bg-gray-50">{t('common.loading')}</div>}>
                        <PerformanceMonitor
                          isProcessing={isProcessing}
                          currentRTF={performanceData.currentRTF}
                          performanceMode={settings.performanceMode}
                          processingTime={performanceData.processingTime}
                          audioDuration={performanceData.audioDuration}
                        />
                      </Suspense>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

      </main>

      {/* Toast notifications */}
      <AnimatePresence>
        {toast && (
          <Toast
            key={toast.id}
            type={toast.type}
            message={toast.message}
            onClose={() => setToast(null)}
          />
        )}
      </AnimatePresence>

      {/* Environment installation progress */}
      <Suspense fallback={<div className="loading-placeholder" />}>
        <InstallationProgress />
      </Suspense>

      {/* Service status indicator */}
      {serviceAdapter?.serviceReady && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="fixed bottom-4 left-4 z-40 bg-green-100 border border-green-200 rounded-lg px-3 py-2 text-sm text-green-800 shadow-sm"
        >
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>Advanced service enabled</span>
          </div>
        </motion.div>
      )}

      {/* Fixed progress bar footer (only show in non-enhanced mode or legacy mode) */}
      <AnimatePresence>
        {isProcessing && !showProgressPanel && (
          <motion.footer
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg"
          >
            <div className="max-w-7xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                {/* Progress info area */}
                <div className="flex items-center space-x-4 min-w-0 flex-1">
                  <div className="w-3 h-3 bg-primary-500 rounded-full animate-pulse flex-shrink-0"></div>
                  
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-medium text-gray-700 truncate">
                        {currentFile ? `Processing: ${currentFile}` : 'Preparing...'}
                      </div>
                      <div className="text-sm text-gray-500 font-medium ml-4">
                        {Math.round(progress)}%
                      </div>
                    </div>
                    
                    {/* Progress bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                      />
                    </div>
                    
                    {/* File Statistics */}
                    <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                      <span>
                        File Progress: {currentFileIndex + 1} / {selectedFiles.length}
                      </span>
                      <span>
                        Completed: {completedFiles.size} files
                      </span>
                      {!serviceAdapter?.serviceReady && (
                        <span className="text-yellow-600">Legacy mode</span>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Control Buttons */}
                <div className="flex items-center space-x-3 ml-6">
                  <button
                    onClick={handleStopProcessing}
                    className="btn btn-secondary flex items-center space-x-2 hover:bg-red-50 hover:border-red-200 hover:text-red-600"
                  >
                    <Square className="w-4 h-4" />
                    <span>Stop</span>
                  </button>
                </div>
              </div>
            </div>
          </motion.footer>
        )}
      </AnimatePresence>

      {/* Development mode debug panel - disabled for now */}
    </div>
  );
}

// Main application wrapper component
function App() {
  return (
    <I18nProvider>
      <AppContent />
    </I18nProvider>
  );
}

export default App;
