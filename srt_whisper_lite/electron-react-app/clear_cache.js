
// 清除舊的設定緩存，強制使用 LARGE 模型
console.log('[FIX] 清除舊的 localStorage 設定...');

// 移除舊設定
localStorage.removeItem('srtgo-settings');
localStorage.removeItem('srtgo-corrections');

// 設定新的強制 LARGE 模型設定
const forcedSettings = {
  model: 'large',
  language: 'auto',
  outputLanguage: 'same',
  outputFormat: 'srt',
  customDir: '',
  enableCorrections: true
};

localStorage.setItem('srtgo-settings', JSON.stringify(forcedSettings));

console.log('[OK] 強制設定為 LARGE 模型');
console.log('設定內容:', forcedSettings);

// 重新載入頁面以套用新設定
window.location.reload();
