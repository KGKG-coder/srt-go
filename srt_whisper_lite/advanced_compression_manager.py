#!/usr/bin/env python3
"""
高級壓縮管理器
實現多重壓縮策略以最小化模型大小
"""

import os
import sys
import lzma
import bz2
import gzip
import zipfile
import tarfile
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class AdvancedCompressionManager:
    """高級壓縮管理器"""
    
    def __init__(self):
        self.models_dir = Path(__file__).parent / "models"
        self.compressed_dir = self.models_dir / "compressed"
        self.compressed_dir.mkdir(exist_ok=True)
        
        # 壓縮配置
        self.compression_configs = {
            "ultra_lzma": {
                "preset": 9,
                "check": lzma.CHECK_CRC64,
                "extension": ".xz",
                "description": "LZMA2 最高壓縮"
            },
            "balanced_bz2": {
                "compresslevel": 9,
                "extension": ".bz2", 
                "description": "BZ2 平衡壓縮"
            },
            "fast_gzip": {
                "compresslevel": 9,
                "extension": ".gz",
                "description": "GZIP 快速解壓"
            },
            "zip_deflate": {
                "compression": zipfile.ZIP_DEFLATED,
                "compresslevel": 9,
                "extension": ".zip",
                "description": "ZIP 通用格式"
            }
        }
    
    def compress_with_lzma(self, input_file: Path, output_file: Path) -> bool:
        """使用 LZMA2 進行超高壓縮"""
        try:
            logger.info(f"LZMA2 壓縮: {input_file.name} -> {output_file.name}")
            
            with open(input_file, 'rb') as f_in:
                with lzma.LZMAFile(
                    output_file, 
                    'wb',
                    preset=9,
                    check=lzma.CHECK_CRC64
                ) as f_out:
                    # 分塊處理以避免內存問題
                    chunk_size = 8192 * 1024  # 8MB chunks
                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
            
            # 計算壓縮率
            original_size = input_file.stat().st_size
            compressed_size = output_file.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"LZMA2 壓縮完成: {original_size/1024/1024:.1f}MB -> {compressed_size/1024/1024:.1f}MB ({ratio:.1f}%)")
            return True
            
        except Exception as e:
            logger.error(f"LZMA2 壓縮失敗: {e}")
            return False
    
    def compress_with_7z(self, input_file: Path, output_file: Path) -> bool:
        """使用 7-Zip 進行極限壓縮"""
        try:
            # 檢查是否有 7z 命令
            seven_z_paths = [
                "C:\\Program Files\\7-Zip\\7z.exe",
                "C:\\Program Files (x86)\\7-Zip\\7z.exe",
                "7z"
            ]
            
            seven_z = None
            for path in seven_z_paths:
                if os.path.exists(path) or path == "7z":
                    try:
                        subprocess.run([path], capture_output=True, timeout=5)
                        seven_z = path
                        break
                    except:
                        continue
            
            if not seven_z:
                logger.warning("7-Zip 未安裝，跳過 7z 壓縮")
                return False
            
            logger.info(f"7-Zip 極限壓縮: {input_file.name}")
            
            cmd = [
                seven_z, "a", "-t7z", "-m0=lzma2", "-mx=9", 
                "-mfb=273", "-ms=on", "-mmt=on", "-aoa",
                str(output_file), str(input_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                original_size = input_file.stat().st_size
                compressed_size = output_file.stat().st_size
                ratio = (1 - compressed_size / original_size) * 100
                
                logger.info(f"7-Zip 壓縮完成: {original_size/1024/1024:.1f}MB -> {compressed_size/1024/1024:.1f}MB ({ratio:.1f}%)")
                return True
            else:
                logger.error(f"7-Zip 壓縮失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"7-Zip 壓縮異常: {e}")
            return False
    
    def multi_stage_compression(self, input_file: Path) -> Tuple[Path, float]:
        """多階段壓縮：測試多種算法並選擇最佳結果"""
        best_file = None
        best_ratio = 0.0
        temp_files = []
        
        try:
            base_name = input_file.stem
            original_size = input_file.stat().st_size
            
            logger.info(f"開始多階段壓縮: {input_file.name} ({original_size/1024/1024:.1f}MB)")
            
            # 階段1: LZMA2 超高壓縮
            lzma_file = self.compressed_dir / f"{base_name}_ultra.xz"
            if self.compress_with_lzma(input_file, lzma_file):
                temp_files.append(lzma_file)
                lzma_size = lzma_file.stat().st_size
                lzma_ratio = (1 - lzma_size / original_size) * 100
                
                if lzma_ratio > best_ratio:
                    best_file = lzma_file
                    best_ratio = lzma_ratio
            
            # 階段2: 7-Zip 極限壓縮
            seven_z_file = self.compressed_dir / f"{base_name}_extreme.7z"
            if self.compress_with_7z(input_file, seven_z_file):
                temp_files.append(seven_z_file)
                seven_z_size = seven_z_file.stat().st_size
                seven_z_ratio = (1 - seven_z_size / original_size) * 100
                
                if seven_z_ratio > best_ratio:
                    best_file = seven_z_file
                    best_ratio = seven_z_ratio
            
            # 階段3: 如果沒有更好的壓縮，使用原始 ZIP
            if best_ratio < 10:  # 如果壓縮率太低
                logger.info("使用原始 ZIP 格式")
                best_file = input_file
                best_ratio = 0.0
            
            # 清理臨時文件（保留最佳結果）
            for temp_file in temp_files:
                if temp_file != best_file and temp_file.exists():
                    temp_file.unlink()
            
            logger.info(f"最佳壓縮結果: {best_file.name if best_file else 'None'} (壓縮率: {best_ratio:.1f}%)")
            return best_file, best_ratio
            
        except Exception as e:
            logger.error(f"多階段壓縮失敗: {e}")
            # 清理所有臨時文件
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            return input_file, 0.0
    
    def create_optimized_model_package(self, model_names: List[str]) -> Path:
        """創建優化的模型包"""
        try:
            logger.info(f"創建優化模型包，包含: {model_names}")
            
            # 移除 tiny 模型，添加 large 模型
            if "tiny" in model_names:
                model_names.remove("tiny")
            if "large" not in model_names:
                model_names.append("large")
            
            package_name = f"whisper-complete-optimized-{'_'.join(model_names)}.pkg"
            package_path = self.compressed_dir / package_name
            
            total_original_size = 0
            compression_results = []
            
            # 對每個模型進行最佳壓縮
            for model_name in model_names:
                model_file = self.models_dir / f"whisper-{model_name}-model.zip"
                if not model_file.exists():
                    logger.warning(f"模型文件不存在: {model_file}")
                    continue
                
                total_original_size += model_file.stat().st_size
                
                # 多階段壓縮
                best_compressed, ratio = self.multi_stage_compression(model_file)
                compression_results.append({
                    "model": model_name,
                    "file": best_compressed,
                    "ratio": ratio
                })
            
            # 創建最終包
            with tarfile.open(package_path, "w:xz") as tar:
                for result in compression_results:
                    tar.add(result["file"], arcname=f"{result['model']}.compressed")
                
                # 添加解壓腳本
                decompressor_script = self.create_decompressor_script(compression_results)
                tar.add(decompressor_script, arcname="decompress.py")
            
            # 計算總體壓縮效果
            final_size = package_path.stat().st_size
            total_ratio = (1 - final_size / total_original_size) * 100
            
            logger.info(f"優化包創建完成:")
            logger.info(f"  - 原始大小: {total_original_size/1024/1024:.1f}MB")
            logger.info(f"  - 壓縮後: {final_size/1024/1024:.1f}MB")
            logger.info(f"  - 總壓縮率: {total_ratio:.1f}%")
            
            return package_path
            
        except Exception as e:
            logger.error(f"創建優化模型包失敗: {e}")
            return None
    
    def create_decompressor_script(self, compression_results: List[dict]) -> Path:
        """創建解壓腳本"""
        script_path = self.compressed_dir / "decompress.py"
        
        script_content = '''#!/usr/bin/env python3
"""
模型解壓腳本
在運行時自動解壓最優化的模型文件
"""

import os
import sys
import lzma
import subprocess
from pathlib import Path

def decompress_models():
    """解壓模型文件"""
    print("正在解壓優化模型...")
    
    current_dir = Path(__file__).parent
    models_dir = current_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # 模型文件映射
    model_files = {
        "base": "base.compressed",
        "medium": "medium.compressed", 
        "large": "large.compressed"
    }
    
    for model_name, compressed_file in model_files.items():
        compressed_path = current_dir / compressed_file
        if not compressed_path.exists():
            continue
            
        output_path = models_dir / f"whisper-{model_name}-model.zip"
        
        try:
            # 檢測壓縮格式並解壓
            if compressed_file.endswith('.xz'):
                with lzma.LZMAFile(compressed_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        f_out.write(f_in.read())
            elif compressed_file.endswith('.7z'):
                # 使用 7z 解壓
                subprocess.run(['7z', 'e', str(compressed_path), f'-o{models_dir}'], check=True)
            else:
                # 直接複製
                with open(compressed_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        f_out.write(f_in.read())
            
            print(f"✅ {model_name} 模型解壓完成")
            
        except Exception as e:
            print(f"❌ {model_name} 模型解壓失敗: {e}")
    
    print("模型解壓完成！")

if __name__ == "__main__":
    decompress_models()
'''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def optimize_all_models(self) -> dict:
        """優化所有模型"""
        results = {}
        
        # 要包含的模型（移除 tiny，包含 large）
        models_to_compress = ["base", "medium", "large"]
        
        logger.info("開始全面模型優化...")
        
        for model_name in models_to_compress:
            model_file = self.models_dir / f"whisper-{model_name}-model.zip"
            if not model_file.exists():
                logger.warning(f"模型文件不存在: {model_file}")
                results[model_name] = {"success": False, "reason": "file_not_found"}
                continue
            
            # 進行多階段壓縮
            best_file, ratio = self.multi_stage_compression(model_file)
            
            results[model_name] = {
                "success": True,
                "original_size_mb": model_file.stat().st_size / 1024 / 1024,
                "compressed_size_mb": best_file.stat().st_size / 1024 / 1024 if best_file else 0,
                "compression_ratio": ratio,
                "compressed_file": str(best_file) if best_file else None
            }
        
        return results


def test_compression():
    """測試壓縮功能"""
    manager = AdvancedCompressionManager()
    
    print("=== 高級壓縮測試 ===")
    
    # 測試單個模型壓縮
    large_model = Path("models/whisper-large-model.zip")
    if large_model.exists():
        print(f"測試 LARGE 模型壓縮: {large_model}")
        best_file, ratio = manager.multi_stage_compression(large_model)
        print(f"最佳壓縮結果: {ratio:.1f}%")
    
    # 測試完整優化
    results = manager.optimize_all_models()
    
    print("\n=== 優化結果 ===")
    for model, result in results.items():
        if result["success"]:
            print(f"{model}: {result['original_size_mb']:.1f}MB -> {result['compressed_size_mb']:.1f}MB ({result['compression_ratio']:.1f}%)")
        else:
            print(f"{model}: 失敗 - {result.get('reason', 'unknown')}")


if __name__ == "__main__":
    test_compression()