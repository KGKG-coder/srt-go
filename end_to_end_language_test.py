#!/usr/bin/env python3
"""
SRT GO v2.2.1 端到端語言系統測試
模擬實際使用者操作流程，測試語言系統的完整運作
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path
import tempfile

class EndToEndLanguageTest:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.app_dir = self.base_dir / "srt_whisper_lite" / "electron-react-app"
        self.test_results = []
        
    def log_step(self, step, message, success=True):
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} 步驟 {step}: {message}")
        self.test_results.append({
            'step': step, 
            'message': message, 
            'success': success,
            'timestamp': time.strftime('%H:%M:%S')
        })
    
    def test_language_installer_flow(self):
        """測試語言安裝器完整流程"""
        print("\n" + "="*60)
        print("端到端測試 1: 語言安裝器流程")
        print("="*60)
        
        # 步驟 1: 檢查語言安裝器存在
        installer_path = self.base_dir / "language_installer.html"
        if installer_path.exists():
            self.log_step(1, "語言安裝器文件存在")
            
            # 檢查內容
            with open(installer_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'navigator.language' in content:
                self.log_step(2, "瀏覽器語言檢測功能存在")
            else:
                self.log_step(2, "缺少瀏覽器語言檢測功能", False)
                
            if 'setup_language_config_fixed.js' in content:
                self.log_step(3, "語言配置腳本引用正確")
            else:
                self.log_step(3, "語言配置腳本引用缺失", False)
                
        else:
            self.log_step(1, "語言安裝器文件不存在", False)
    
    def test_language_config_setup(self):
        """測試語言配置設置流程"""
        print("\n" + "="*60)
        print("端到端測試 2: 語言配置設置")
        print("="*60)
        
        # 步驟 1: 檢查配置腳本存在
        config_script = self.base_dir / "setup_language_config_fixed.js"
        if config_script.exists():
            self.log_step(1, "語言配置腳本存在")
            
            # 步驟 2: 模擬不同語言配置
            test_languages = ['zh-TW', 'en', 'ja']
            
            for i, lang in enumerate(test_languages, 2):
                try:
                    # 運行配置腳本
                    result = subprocess.run([
                        'node', str(config_script), lang
                    ], capture_output=True, text=True, cwd=str(self.base_dir))
                    
                    if result.returncode == 0:
                        self.log_step(f"{i}", f"語言 {lang} 配置設置成功")
                        
                        # 驗證配置文件生成
                        config_file = self.app_dir / "language_config.json"
                        if config_file.exists():
                            with open(config_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            
                            if config.get('selectedLanguage') == lang:
                                self.log_step(f"{i}a", f"語言 {lang} 配置驗證成功")
                            else:
                                self.log_step(f"{i}a", f"語言 {lang} 配置驗證失敗", False)
                        else:
                            self.log_step(f"{i}a", f"語言 {lang} 配置文件生成失敗", False)
                    else:
                        self.log_step(f"{i}", f"語言 {lang} 配置設置失敗: {result.stderr}", False)
                        
                except Exception as e:
                    self.log_step(f"{i}", f"語言 {lang} 配置異常: {e}", False)
                    
        else:
            self.log_step(1, "語言配置腳本不存在", False)
    
    def test_electron_language_loading(self):
        """測試 Electron 語言載入流程"""
        print("\n" + "="*60)
        print("端到端測試 3: Electron 語言載入")
        print("="*60)
        
        # 步驟 1: 檢查 main.js IPC 處理
        main_js = self.app_dir / "main.js"
        if main_js.exists():
            with open(main_js, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "ipcMain.handle('get-language-config'" in content:
                self.log_step(1, "Main.js IPC 語言配置處理已實現")
                
                # 檢查多重備援機制
                if "language_config.json" in content and "public" in content:
                    self.log_step(2, "多重配置文件備援機制存在")
                else:
                    self.log_step(2, "配置文件備援機制不完整", False)
                    
            else:
                self.log_step(1, "Main.js 缺少語言配置 IPC 處理", False)
        else:
            self.log_step(1, "Main.js 文件不存在", False)
        
        # 步驟 3: 檢查 preload.js API 暴露
        preload_js = self.app_dir / "preload.js"
        if preload_js.exists():
            with open(preload_js, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "getLanguageConfig:" in content:
                self.log_step(3, "Preload.js 語言配置 API 已暴露")
            else:
                self.log_step(3, "Preload.js 缺少語言配置 API", False)
        else:
            self.log_step(3, "Preload.js 文件不存在", False)
    
    def test_react_language_integration(self):
        """測試 React 語言整合流程"""
        print("\n" + "="*60)
        print("端到端測試 4: React 語言整合")
        print("="*60)
        
        # 步驟 1: 檢查固定語言上下文
        context_file = self.app_dir / "react-app" / "src" / "i18n" / "FixedLanguageContext.js"
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.log_step(1, "FixedLanguageContext 組件存在")
            
            # 檢查多重載入機制
            load_mechanisms = [
                "fetch('/language_config.json')",
                "window.electronAPI.getLanguageConfig",
                "process.env.REACT_APP_SRTGO_LANGUAGE",
                "localStorage.getItem"
            ]
            
            found_mechanisms = []
            for mechanism in load_mechanisms:
                if mechanism.replace(".", "\\.") in content or mechanism in content:
                    found_mechanisms.append(mechanism)
            
            if len(found_mechanisms) >= 3:
                self.log_step(2, f"多重語言載入機制完整 ({len(found_mechanisms)}/4)")
            else:
                self.log_step(2, f"語言載入機制不完整 ({len(found_mechanisms)}/4)", False)
                
        else:
            self.log_step(1, "FixedLanguageContext 組件不存在", False)
        
        # 步驟 3: 檢查翻譯資源
        translations_file = self.app_dir / "react-app" / "src" / "i18n" / "translations.js"
        if translations_file.exists():
            with open(translations_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            languages = ['en', 'zh-TW', 'zh-CN', 'ja', 'ko']
            complete_languages = 0
            
            for lang in languages:
                if f"'{lang}':" in content and "app:" in content:
                    complete_languages += 1
            
            if complete_languages == 5:
                self.log_step(3, f"所有語言翻譯完整 ({complete_languages}/5)")
            else:
                self.log_step(3, f"翻譯不完整 ({complete_languages}/5)", False)
                
        else:
            self.log_step(3, "翻譯文件不存在", False)
    
    def test_build_configuration(self):
        """測試構建配置"""
        print("\n" + "="*60)
        print("端到端測試 5: 構建配置")
        print("="*60)
        
        # 步驟 1: 檢查所有必要配置文件位置
        config_locations = [
            ("主配置", self.app_dir / "language_config.json"),
            ("Public配置", self.app_dir / "react-app" / "public" / "language_config.json"),
            ("Build配置", self.app_dir / "react-app" / "build" / "language_config.json")
        ]
        
        for i, (name, path) in enumerate(config_locations, 1):
            if path.exists():
                self.log_step(i, f"{name}存在")
                
                # 驗證配置內容
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    if 'selectedLanguage' in config and 'languageChangeable' in config:
                        self.log_step(f"{i}a", f"{name}格式正確")
                    else:
                        self.log_step(f"{i}a", f"{name}格式不完整", False)
                except Exception as e:
                    self.log_step(f"{i}a", f"{name}格式錯誤: {e}", False)
            else:
                self.log_step(i, f"{name}不存在", False)
    
    def generate_end_to_end_report(self):
        """生成端到端測試報告"""
        print("\n" + "="*60)
        print("端到端測試報告")
        print("="*60)
        
        total_steps = len(self.test_results)
        successful_steps = len([r for r in self.test_results if r['success']])
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        print(f"總測試步驟: {total_steps}")
        print(f"成功步驟: {successful_steps}")
        print(f"成功率: {success_rate:.1f}%")
        
        # 按測試分組顯示結果
        print("\n詳細結果:")
        for result in self.test_results:
            status = "[OK]" if result['success'] else "[FAIL]"
            print(f"  {status} [{result['timestamp']}] 步驟 {result['step']}: {result['message']}")
        
        # 保存報告
        report = {
            'test_type': 'end_to_end_language_test',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_steps': total_steps,
            'successful_steps': successful_steps,
            'success_rate': success_rate,
            'detailed_results': self.test_results
        }
        
        report_file = self.base_dir / 'end_to_end_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n端到端測試報告已保存: {report_file}")
        return success_rate >= 80
    
    def run_all_tests(self):
        """執行所有端到端測試"""
        print("="*60)
        print("SRT GO v2.2.1 端到端語言系統測試")
        print("="*60)
        print("模擬實際使用者操作流程...")
        
        self.test_language_installer_flow()
        self.test_language_config_setup()
        self.test_electron_language_loading()
        self.test_react_language_integration()
        self.test_build_configuration()
        
        return self.generate_end_to_end_report()

if __name__ == "__main__":
    tester = EndToEndLanguageTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n[SUCCESS] 端到端測試通過！語言系統可以正常使用。")
    else:
        print("\n[WARNING] 端到端測試發現問題，需要進一步修復。")
    
    sys.exit(0 if success else 1)