#!/usr/bin/env python3
"""
首次運行嚮導 - 引導用戶選擇和安裝模型
"""

import sys
import json
import logging
from pathlib import Path
from model_manager import ModelManager

logger = logging.getLogger(__name__)

class FirstRunGuide:
    """首次運行嚮導"""
    
    def __init__(self):
        self.model_manager = ModelManager()
        
    def show_model_selection_dialog(self):
        """顯示模型選擇對話框（由前端調用）"""
        status = self.model_manager.get_model_status()
        
        # 準備選項資料
        options = []
        for model_name, info in status.items():
            option = {
                "name": model_name,
                "size_mb": info["size_mb"],
                "description": info["description"],
                "available_locally": info["available_locally"],
                "bundled_available": info["bundled_package_available"],
                "recommended": model_name == "medium"  # 推薦中等模型
            }
            options.append(option)
            
        return {
            "type": "model_selection",
            "options": options,
            "message": "選擇要使用的 AI 模型",
            "details": "首次使用需要安裝 AI 模型。您可以選擇預置模型（快速）或下載最新版本（需要網路）。"
        }
        
    def install_selected_model(self, model_name, progress_callback=None):
        """安裝選定的模型"""
        try:
            success, path, source = self.model_manager.download_model_if_needed(
                model_name, 
                progress_callback=progress_callback
            )
            
            if success:
                return {
                    "success": True,
                    "model": model_name,
                    "source": source,
                    "path": path,
                    "message": f"{model_name} 模型安裝完成"
                }
            else:
                return {
                    "success": False,
                    "model": model_name,
                    "error": path,
                    "message": f"{model_name} 模型安裝失敗"
                }
                
        except Exception as e:
            return {
                "success": False,
                "model": model_name,
                "error": str(e),
                "message": "模型安裝過程中發生錯誤"
            }


def main():
    """CLI 接口"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        guide = FirstRunGuide()
        
        if command == "list":
            # 列出模型選項
            result = guide.show_model_selection_dialog()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
        elif command == "install" and len(sys.argv) > 2:
            # 安裝指定模型
            model_name = sys.argv[2]
            
            def progress_callback(percent, message):
                print(f"PROGRESS:{json.dumps({'percent': percent, 'message': message}, ensure_ascii=False)}")
                
            result = guide.install_selected_model(model_name, progress_callback)
            print(f"RESULT:{json.dumps(result, ensure_ascii=False)}")
            
        else:
            print("Usage: python first_run_guide.py [list|install <model_name>]")
    else:
        # 交互模式
        guide = FirstRunGuide()
        options = guide.show_model_selection_dialog()
        
        print("=== SRT GO 首次運行嚮導 ===")
        print(options["details"])
        print()
        
        for i, option in enumerate(options["options"]):
            status = "✅本地可用" if option["available_locally"] else ("📦有預置包" if option["bundled_available"] else "🌐需要下載")
            recommended = " [推薦]" if option["recommended"] else ""
            print(f"{i+1}. {option['name'].upper()}{recommended}")
            print(f"   大小: {option['size_mb']}MB | {option['description']}")
            print(f"   狀態: {status}")
            print()
            
        choice = input("請選擇模型 (1-4): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options["options"]):
                selected_model = options["options"][idx]["name"]
                print(f"正在安裝 {selected_model} 模型...")
                
                def progress_callback(percent, message):
                    print(f"[{percent:3d}%] {message}")
                    
                result = guide.install_selected_model(selected_model, progress_callback)
                
                if result["success"]:
                    print(f"\n✅ {result['message']}")
                else:
                    print(f"\n❌ {result['message']}")
            else:
                print("無效的選擇")
        except ValueError:
            print("請輸入數字")


if __name__ == "__main__":
    main()
