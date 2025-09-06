#!/usr/bin/env python3
"""
強制 Electron React GUI 使用 LARGE 模型
修正 UI 顯示和實際執行的模型設定
"""

import json
import os
from pathlib import Path

def update_app_js():
    """修正 App.js 中的預設設定"""
    app_js_path = Path("electron-react-app/react-app/src/App.js")
    
    if not app_js_path.exists():
        print(f"[ERROR] 找不到文件: {app_js_path}")
        return False
    
    # 讀取文件
    with open(app_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修正預設設定，確保強制使用 large 模型
    old_default = '''  const [settings, setSettings] = useState({
    model: 'large',  // 固定使用 LARGE 模型
    language: 'auto',
    outputLanguage: 'same', // 新增輸出語言設定
    outputFormat: 'srt',
    customDir: '',
    enableCorrections: true
  });'''
    
    new_default = '''  const [settings, setSettings] = useState({
    model: 'large',  // 強制使用 LARGE 模型 - 不可更改
    language: 'auto',
    outputLanguage: 'same', // 新增輸出語言設定
    outputFormat: 'srt',
    customDir: '',
    enableCorrections: true
  });'''
    
    # 也修正 loadSettings 中的預設值
    old_load_default = '''      const defaultSettings = {
        model: 'large',  // 固定使用 LARGE 模型
        language: 'auto',
        outputLanguage: 'same',
        outputFormat: 'srt',
        customDir: '',
        enableCorrections: true
      };'''
    
    new_load_default = '''      const defaultSettings = {
        model: 'large',  // 強制使用 LARGE 模型 - 不可更改
        language: 'auto',
        outputLanguage: 'same',
        outputFormat: 'srt',
        customDir: '',
        enableCorrections: true
      };'''
    
    # 添加強制模型修正
    force_large_code = '''
  // 強制確保模型設定為 large
  useEffect(() => {
    if (settings.model !== 'large') {
      console.log('[FIX] 檢測到模型設定不是 large，強制修正為 large');
      const correctedSettings = { ...settings, model: 'large' };
      setSettings(correctedSettings);
      localStorage.setItem('srtgo-settings', JSON.stringify(correctedSettings));
    }
  }, [settings.model]);
'''
    
    # 進行替換
    content = content.replace(old_default, new_default)
    content = content.replace(old_load_default, new_load_default)
    
    # 在 useEffect 前添加強制模型修正
    import_line = "import { I18nProvider, useI18n } from './i18n/I18nContext';"
    if import_line in content:
        content = content.replace(import_line, import_line + force_large_code)
    
    # 寫回文件
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] 已修正 {app_js_path}")
    return True

def update_settings_panel():
    """確保 SettingsPanel 顯示正確的模型信息"""
    settings_path = Path("electron-react-app/react-app/src/components/SettingsPanel.js")
    
    if not settings_path.exists():
        print(f"[ERROR] 找不到文件: {settings_path}")
        return False
    
    # 讀取文件
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 確保模型顯示部分正確
    old_model_section = '''            <label className="text-lg font-medium text-gray-900">{t('settings.aiModel')}</label>
            <p className="text-sm text-gray-600 mb-3">{t('settings.professionalVersion')}</p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <span className="font-medium text-gray-900">{t('models.large.name')}</span>
              <span className="text-green-600 ml-2">✓ {t('models.large.description')}</span>
            </div>'''
    
    new_model_section = '''            <label className="text-lg font-medium text-gray-900">{t('settings.aiModel')}</label>
            <p className="text-sm text-gray-600 mb-3">{t('settings.professionalVersion')}</p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <span className="font-medium text-gray-900">Large (專業版)</span>
              <span className="text-green-600 ml-2">✓ 最高準確度，專業級AI模型</span>
            </div>'''
    
    # 進行替換
    if old_model_section in content:
        content = content.replace(old_model_section, new_model_section)
        
        # 寫回文件
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] 已修正 {settings_path}")
        return True
    else:
        print(f"[INFO] {settings_path} 無需修正")
        return True

def clear_localStorage_cache():
    """創建清除緩存的 JavaScript 腳本"""
    js_script = '''
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
'''
    
    # 保存腳本
    script_path = Path("electron-react-app/clear_cache.js")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(js_script)
    
    print(f"[OK] 已創建清除緩存腳本: {script_path}")
    print("[INFO] 在瀏覽器開發者工具的 Console 中執行此腳本來清除舊設定")
    
    return script_path

def update_electron_backend():
    """確保 electron_backend.py 正確處理模型設定"""
    backend_path = Path("electron_backend.py")
    
    if not backend_path.exists():
        print(f"[ERROR] 找不到文件: {backend_path}")
        return False
    
    # 讀取文件
    with open(backend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 確保模型設定強制為 large
    force_large_code = '''
    # 強制使用 LARGE 模型（專業版配置）
    settings['model'] = 'large'
    logger.info(f"[FIX] 強制使用 LARGE 模型（原設定: {settings.get('model', 'unknown')}）")
'''
    
    # 在處理設定的地方添加強制修正
    if "settings = json.loads(args.settings)" in content:
        old_line = "settings = json.loads(args.settings)"
        new_line = old_line + force_large_code
        content = content.replace(old_line, new_line)
        
        # 寫回文件
        with open(backend_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] 已修正 {backend_path}")
        return True
    else:
        print(f"[INFO] {backend_path} 無需修正")
        return True

def main():
    """主函數"""
    print("[*] 正在強制設定 Electron React GUI 使用 LARGE 模型...")
    print("=" * 60)
    
    # 修正前端設定
    update_app_js()
    update_settings_panel()
    
    # 修正後端設定
    update_electron_backend()
    
    # 創建清除緩存腳本
    clear_cache_script = clear_localStorage_cache()
    
    print("\n" + "=" * 60)
    print("[OK] 修正完成！")
    print("\n[INFO] 後續步驟:")
    print("1. 重新啟動 Electron React 應用程式")
    print("2. 開啟瀏覽器開發者工具 (F12)")
    print("3. 在 Console 中執行以下命令清除舊設定:")
    print("   localStorage.removeItem('srtgo-settings');")
    print("   location.reload();")
    print("4. 確認 UI 顯示「Large (專業版)」模型")
    print("5. 執行測試確認實際使用 LARGE 模型")
    
    return True

if __name__ == "__main__":
    main()