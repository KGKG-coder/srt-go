#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能後端選擇器 (Smart Backend Selector)
自動選擇最佳的 Python 環境和後端配置

版本：v2.2.1
最後更新：2025-08-27
"""

import sys
import os
import subprocess
import logging
import json
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import importlib.util

logger = logging.getLogger(__name__)

class SmartBackendSelector:
    """智能後端選擇器，實現3層回退機制"""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.available_pythons = self._discover_python_environments()
        self.backend_capabilities = {}
        
    def _discover_python_environments(self) -> Dict[str, Dict[str, Any]]:
        """發現所有可用的 Python 環境"""
        environments = {}
        
        # 1. 系統 Python（優先級最高）
        system_python = self._check_system_python()
        if system_python:
            environments['system'] = system_python
            
        # 2. 嵌入式 Python（本地備份）
        embedded_python = self._check_embedded_python()
        if embedded_python:
            environments['embedded'] = embedded_python
            
        # 3. 當前 Python（最後備案）
        current_python = {
            'path': sys.executable,
            'version': sys.version,
            'priority': 3,
            'type': 'current'
        }
        environments['current'] = current_python
        
        return environments
        
    def _check_system_python(self) -> Optional[Dict[str, Any]]:
        """檢查系統 Python 環境 - 修正跨電腦相容性"""
        system_paths = [
            # PATH中的Python（最通用）
            'python',
            'python3',
            'python3.13',
            'python3.11',
            'python3.12',
            
            # 系統級安裝位置
            'C:\\Python313\\python.exe',
            'C:\\Python311\\python.exe',
            'C:\\Python312\\python.exe',
        ]
        
        # 添加用戶特定的Python安裝位置
        import os
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            user_python_paths = [
                os.path.join(user_profile, 'AppData', 'Local', 'Programs', 'Python', 'Python313', 'python.exe'),
                os.path.join(user_profile, 'AppData', 'Local', 'Programs', 'Python', 'Python311', 'python.exe'),
                os.path.join(user_profile, 'AppData', 'Local', 'Programs', 'Python', 'Python312', 'python.exe'),
                os.path.join(user_profile, 'AppData', 'Local', 'Microsoft', 'WindowsApps', 'python.exe'),
                os.path.join(user_profile, 'AppData', 'Local', 'Microsoft', 'WindowsApps', 'python3.exe')
            ]
            system_paths.extend(user_python_paths)
        
        for python_path in system_paths:
            try:
                result = subprocess.run(
                    [python_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    if self._check_ai_dependencies(python_path):
                        return {
                            'path': python_path,
                            'version': version,
                            'priority': 1,
                            'type': 'system',
                            'ai_ready': True
                        }
                    else:
                        return {
                            'path': python_path,
                            'version': version,
                            'priority': 1,
                            'type': 'system',
                            'ai_ready': False
                        }
                        
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                continue
                
        return None
        
    def _check_embedded_python(self) -> Optional[Dict[str, Any]]:
        """檢查嵌入式 Python 環境 - 修正跨電腦相容性"""
        embedded_paths = []
        
        # 1. 從當前腳本位置推導可能的嵌入式Python位置
        script_dir = self.current_dir
        
        # 常見的相對路徑結構
        potential_paths = [
            # 標準結構：python/ 目錄與 mini_python/ 同級
            script_dir.parent / 'mini_python' / 'python.exe',
            
            # 打包結構：resources/resources/python/ 與 resources/resources/mini_python/ 同級
            script_dir.parent / 'mini_python' / 'python.exe',
            
            # 深層結構：向上兩層
            script_dir.parent.parent / 'mini_python' / 'python.exe',
            
            # 複雜結構：resources/resources/
            script_dir.parent.parent / 'resources' / 'mini_python' / 'python.exe',
            
            # Electron應用結構：相對於資源目錄
            script_dir / '..' / '..' / 'mini_python' / 'python.exe',
            
            # 絕對搜尋：從執行檔目錄開始
            Path(sys.executable).parent.parent / 'mini_python' / 'python.exe' if hasattr(sys, 'executable') else None
        ]
        
        # 過濾掉None值並解析路徑
        for path_candidate in potential_paths:
            if path_candidate:
                try:
                    resolved_path = path_candidate.resolve()
                    if resolved_path not in embedded_paths:
                        embedded_paths.append(resolved_path)
                except (OSError, ValueError):
                    # 路徑解析失敗，跳過
                    continue
        
        for python_path in embedded_paths:
            if python_path.exists():
                try:
                    result = subprocess.run(
                        [str(python_path), '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        ai_ready = self._check_ai_dependencies(str(python_path))
                        
                        return {
                            'path': str(python_path),
                            'version': version,
                            'priority': 2,
                            'type': 'embedded',
                            'ai_ready': ai_ready
                        }
                        
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    continue
                    
        return None
        
    def _check_ai_dependencies(self, python_path: str) -> bool:
        """檢查 AI 依賴項是否可用"""
        required_packages = ['numpy', 'faster_whisper']
        
        try:
            for package in required_packages:
                result = subprocess.run(
                    [python_path, '-c', f'import {package}'],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode != 0:
                    return False
            return True
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False
            
    def select_best_backend(self) -> Tuple[str, Dict[str, Any]]:
        """選擇最佳的後端環境"""
        if not self.available_pythons:
            raise RuntimeError("未找到可用的 Python 環境")
            
        # 按優先級和 AI 能力排序
        sorted_envs = sorted(
            self.available_pythons.items(),
            key=lambda x: (x[1]['priority'], not x[1].get('ai_ready', False))
        )
        
        for env_name, env_info in sorted_envs:
            logger.info(f"嘗試使用 {env_name} 環境: {env_info['version']}")
            
            if env_info.get('ai_ready', False):
                logger.info(f"✅ 選擇 {env_name} 環境（具備 AI 能力）")
                return env_name, env_info
            else:
                logger.warning(f"⚠️ {env_name} 環境缺少 AI 依賴項")
                
        # 如果沒有 AI 就緒的環境，選擇優先級最高的
        best_env_name, best_env_info = sorted_envs[0]
        logger.warning(f"使用 {best_env_name} 環境（無 AI 能力）")
        return best_env_name, best_env_info
        
    def get_backend_config(self, env_name: str, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """獲取後端配置"""
        config = {
            'python_path': env_info['path'],
            'python_version': env_info['version'],
            'environment_type': env_info['type'],
            'ai_ready': env_info.get('ai_ready', False),
            'backend_script': 'electron_backend.py'
        }
        
        # 根據環境類型調整配置
        if env_info['type'] == 'system':
            config.update({
                'working_directory': str(self.current_dir),
                'python_path_args': ['-u']  # 無緩衝輸出
            })
        elif env_info['type'] == 'embedded':
            config.update({
                'working_directory': str(self.current_dir),
                'python_path_args': ['-u'],
                'environment_vars': {
                    'PYTHONPATH': str(self.current_dir)
                }
            })
            
        return config
        
    def test_backend_functionality(self, config: Dict[str, Any]) -> bool:
        """測試後端功能"""
        try:
            python_path = config['python_path']
            working_dir = config.get('working_directory', str(self.current_dir))
            
            # 測試基本 Python 功能
            test_script = '''
import sys
import json
print(json.dumps({
    "status": "ok",
    "python_version": sys.version,
    "python_path": sys.executable
}))
'''
            
            result = subprocess.run(
                [python_path, '-c', test_script],
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=10
            )
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    return response.get('status') == 'ok'
                except json.JSONDecodeError:
                    pass
                    
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
            
        return False
        
    def get_environment_info(self) -> Dict[str, Any]:
        """獲取環境資訊摘要"""
        return {
            'total_environments': len(self.available_pythons),
            'ai_ready_environments': sum(
                1 for env in self.available_pythons.values() 
                if env.get('ai_ready', False)
            ),
            'environments': self.available_pythons
        }

def test_full_backend() -> Tuple[bool, str]:
    """測試完整後端功能"""
    try:
        selector = SmartBackendSelector()
        env_name, env_info = selector.select_best_backend()
        config = selector.get_backend_config(env_name, env_info)
        
        if selector.test_backend_functionality(config):
            return True, f"後端就緒 ({env_name})"
        else:
            return False, f"後端測試失敗 ({env_name})"
            
    except Exception as e:
        return False, f"後端選擇失敗: {str(e)}"

def main():
    """主函數 - 用於測試"""
    logging.basicConfig(level=logging.INFO)
    
    print("🤖 Smart Backend Selector v2.2.1")
    print("=" * 40)
    
    selector = SmartBackendSelector()
    
    # 顯示環境資訊
    env_info = selector.get_environment_info()
    print(f"發現 {env_info['total_environments']} 個 Python 環境")
    print(f"其中 {env_info['ai_ready_environments']} 個具備 AI 能力")
    
    # 選擇最佳後端
    try:
        env_name, env_data = selector.select_best_backend()
        config = selector.get_backend_config(env_name, env_data)
        
        print(f"\n✅ 選擇的後端: {env_name}")
        print(f"Python 版本: {env_data['version']}")
        print(f"AI 就緒: {'是' if env_data.get('ai_ready', False) else '否'}")
        
        # 測試功能
        if selector.test_backend_functionality(config):
            print("✅ 後端功能測試通過")
        else:
            print("❌ 後端功能測試失敗")
            
    except Exception as e:
        print(f"❌ 後端選擇失敗: {e}")
        
if __name__ == "__main__":
    main()