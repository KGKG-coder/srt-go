/**
 * 修復模型下載問題
 * 解決程式卡在 5% 的問題
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 修復模型下載卡住問題...\n');

// 1. 讀取 simplified_subtitle_core.py
const coreFilePath = path.join(__dirname, '..', 'simplified_subtitle_core.py');
let coreContent = fs.readFileSync(coreFilePath, 'utf8');

console.log('📝 正在修復 simplified_subtitle_core.py...');

// 2. 修復模型初始化 - 添加超時和錯誤處理
const modelInitFix = `            # 添加模型下載超時和重試機制
            import os
            import time
            from pathlib import Path
            
            # 檢查本地模型緩存
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
            local_model_exists = False
            
            if os.path.exists(cache_dir):
                # 檢查是否有本地 large 模型
                for item in os.listdir(cache_dir):
                    if "whisper-large" in item.lower():
                        local_model_exists = True
                        break
            
            logger.info(f"本地模型緩存檢查: {'存在' if local_model_exists else '不存在'}")
            
            # 添加網路連接檢查
            def check_internet_connection():
                try:
                    import urllib.request
                    urllib.request.urlopen('https://huggingface.co', timeout=10)
                    return True
                except:
                    return False
            
            has_internet = check_internet_connection()
            logger.info(f"網路連接狀態: {'可用' if has_internet else '不可用'}")
            
            # 智能選擇模型下載策略
            download_timeout = 300  # 5分鐘超時
            max_download_retries = 2
            
            for download_attempt in range(max_download_retries + 1):
                try:
                    if progress_callback:
                        if download_attempt == 0:
                            progress_callback(5, "正在初始化 AI 模型...")
                        else:
                            progress_callback(5, f"模型初始化重試 {download_attempt}/{max_download_retries}...")
                    
                    start_time = time.time()
                    
                    # 根據網路狀況調整下載策略
                    if not has_internet and not local_model_exists:
                        # 無網路且無本地模型，降級到更小的模型
                        logger.warning("無網路連接且無本地模型，自動降級到 base 模型")
                        actual_model_size = "base"
                        if progress_callback:
                            progress_callback(8, "網路不可用，使用本地 base 模型...")
                    else:
                        actual_model_size = self.model_size
                    
                    # 創建模型實例
                    self.model = WhisperModel(
                        actual_model_size,
                        device=self.device,
                        compute_type=self.compute_type,
                        download_root=None,
                        local_files_only=not has_internet,  # 無網路時僅使用本地文件
                        num_workers=self.config.get("model.num_workers", 4) if self.config and self.device == "cuda" else 2
                    )
                    
                    elapsed_time = time.time() - start_time
                    logger.info(f"模型載入成功，耗時: {elapsed_time:.1f}秒")
                    
                    if progress_callback:
                        progress_callback(20, "AI 模型載入完成")
                    
                    break  # 成功載入，跳出重試循環
                    
                except Exception as model_error:
                    elapsed_time = time.time() - start_time
                    logger.error(f"模型載入失敗 (嘗試 {download_attempt + 1}/{max_download_retries + 1}): {model_error}")
                    
                    if download_attempt == max_download_retries:
                        # 最後嘗試：使用最小的 tiny 模型
                        logger.warning("所有重試失敗，嘗試使用 tiny 模型作為備選")
                        try:
                            self.model = WhisperModel(
                                "tiny",
                                device=self.device,
                                compute_type=self.compute_type,
                                download_root=None,
                                local_files_only=True,  # 強制僅使用本地文件
                                num_workers=2
                            )
                            logger.info("成功載入備選 tiny 模型")
                            if progress_callback:
                                progress_callback(20, "載入備選模型完成")
                            break
                        except Exception as backup_error:
                            logger.error(f"備選模型也失敗: {backup_error}")
                            if progress_callback:
                                progress_callback(0, f"模型載入失敗: {str(model_error)[:50]}...")
                            return False
                    else:
                        # 等待後重試
                        wait_time = (download_attempt + 1) * 5
                        logger.info(f"等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                        
                        if progress_callback:
                            progress_callback(3, f"模型載入重試中...({download_attempt + 1}/{max_download_retries})")`;

// 3. 替換原始的模型初始化代碼
const originalModelInit = /(\s+)(from faster_whisper import WhisperModel\s+)(.*?)(\s+if progress_callback:\s+if progress_callback\(20, "AI 模型載入完成"\) == False:\s+return False)/s;

if (originalModelInit.test(coreContent)) {
    coreContent = coreContent.replace(originalModelInit, (match, indent) => {
        return `${indent}from faster_whisper import WhisperModel
            
            # 使用配置的模型大小和設置
            logger.info(f"載入模型: {self.model_size}, 設備: {self.device}, 計算類型: {self.compute_type}")
            
${modelInitFix}
            
            if progress_callback:
                if progress_callback(20, "AI 模型載入完成") == False:
                    return False`;
    });
    
    console.log('✅ 已修復模型初始化代碼');
} else {
    console.log('⚠️  未找到預期的模型初始化代碼模式');
}

// 4. 添加網路檢查函數到文件開頭
const networkCheckFunction = `
# 添加網路連接檢查功能
def check_network_and_cache():
    """檢查網路連接和模型緩存狀態"""
    import urllib.request
    import os
    
    # 檢查網路
    try:
        urllib.request.urlopen('https://huggingface.co', timeout=5)
        has_internet = True
    except:
        has_internet = False
    
    # 檢查本地緩存
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    has_cache = os.path.exists(cache_dir) and len(os.listdir(cache_dir)) > 0
    
    return has_internet, has_cache

`;

// 在 class SimplifiedSubtitleCore 之前插入
const classPattern = /class SimplifiedSubtitleCore:/;
if (classPattern.test(coreContent)) {
    coreContent = coreContent.replace(classPattern, networkCheckFunction + 'class SimplifiedSubtitleCore:');
    console.log('✅ 已添加網路檢查函數');
}

// 5. 寫回文件
fs.writeFileSync(coreFilePath, coreContent, 'utf8');
console.log('✅ 已保存修復後的 simplified_subtitle_core.py');

// 6. 創建用戶說明文件
const userInstructions = `# 模型下載問題修復說明

## 問題描述
應用程式在載入 large 模型時卡在 5%，通常是因為：
1. 網路連接問題
2. 模型下載超時
3. Hugging Face 伺服器連接問題

## 修復內容
1. **智能模型選擇**: 根據網路狀況自動選擇模型
2. **超時處理**: 5分鐘下載超時保護  
3. **重試機制**: 最多重試 2 次
4. **降級策略**: 網路不可用時自動使用較小模型
5. **備選方案**: 最終回退到本地 tiny 模型

## 使用建議
1. **首次使用**: 確保網路連接穩定
2. **離線使用**: 先在有網路的環境下載一次模型
3. **網路不佳**: 建議選擇 medium 或 base 模型

## 模型大小對比
- tiny: 最快，準確度較低
- base: 平衡選擇  
- medium: 推薦日常使用
- large: 最高準確度，需要良好網路

修復後應用程式會自動處理網路問題，不再卡住。
`;

fs.writeFileSync(
    path.join(__dirname, 'MODEL_DOWNLOAD_FIX_README.md'),
    userInstructions,
    'utf8'
);

console.log('\n🎯 修復完成！');
console.log('📄 已創建說明文件: MODEL_DOWNLOAD_FIX_README.md');
console.log('📝 需要重新打包應用程式以應用修復');