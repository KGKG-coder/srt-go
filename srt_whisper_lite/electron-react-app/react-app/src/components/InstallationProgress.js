import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Download, CheckCircle, AlertCircle } from 'lucide-react';

const InstallationProgress = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [status, setStatus] = useState('idle'); // idle, installing, complete, error
  const [message, setMessage] = useState('');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (window.electronAPI) {
      // 監聽安裝進度
      window.electronAPI.onInstallationProgress((data) => {
        switch (data.type) {
          case 'start':
            setIsVisible(true);
            setStatus('installing');
            setMessage(data.message);
            setProgress(0);
            break;
          case 'update':
            setMessage(data.message);
            // 簡單的進度模擬，實際可以根據具體步驟更精確
            setProgress(prev => Math.min(prev + 10, 90));
            break;
          case 'complete':
            setProgress(100);
            setStatus('complete');
            setTimeout(() => {
              setIsVisible(false);
              setStatus('idle');
            }, 3000);
            break;
          case 'error':
            setStatus('error');
            setMessage(data.message || 'Installation failed');
            break;
          default:
            // Handle unknown message types gracefully
            console.warn('Unknown installation progress type:', data.type);
            break;
        }
      });
    }
  }, []);

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4"
      >
        <div className="text-center">
          {/* Icon */}
          <div className="mb-6">
            {status === 'installing' && (
              <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
                <Download className="w-8 h-8 text-blue-600 animate-bounce" />
              </div>
            )}
            {status === 'complete' && (
              <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            )}
            {status === 'error' && (
              <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
            )}
          </div>

          {/* Title */}
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {status === 'installing' && 'Setting up environment...'}
            {status === 'complete' && 'Setup complete!'}
            {status === 'error' && 'Setup failed'}
          </h3>

          {/* Message */}
          <p className="text-gray-600 mb-6 text-sm">
            {message}
          </p>

          {/* Progress Bar */}
          {status === 'installing' && (
            <div className="mb-6">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div
                  className="bg-blue-600 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">{progress}%</p>
            </div>
          )}

          {/* Status Messages */}
          {status === 'installing' && (
            <div className="text-sm text-gray-500">
              <p>Please wait while we set up the required environment.</p>
              <p className="mt-1">This may take several minutes...</p>
            </div>
          )}

          {status === 'complete' && (
            <div className="text-sm text-green-600">
              <p>Environment setup completed successfully!</p>
              <p className="mt-1">You can now use SRT GO to generate subtitles.</p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-sm text-red-600">
              <p>Failed to set up the environment.</p>
              <p className="mt-1">Please try installing Python manually.</p>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default InstallationProgress;