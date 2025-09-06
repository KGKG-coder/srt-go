# PowerShell 腳本：安裝嵌入式 Python 依賴
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "嵌入式 Python 依賴安裝" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 檢查 mini_python 是否存在
if (!(Test-Path "mini_python\python.exe")) {
    Write-Host "[錯誤] 找不到 mini_python\python.exe" -ForegroundColor Red
    exit 1
}

Write-Host "[1/6] 檢查 Python 版本..." -ForegroundColor Green
& "mini_python\python.exe" --version

Write-Host "`n[2/6] 升級 pip..." -ForegroundColor Green
& "mini_python\python.exe" -m pip install --upgrade pip

Write-Host "`n[3/6] 安裝核心數值計算庫..." -ForegroundColor Green
& "mini_python\python.exe" -m pip install "numpy>=1.24.0,<2.0.0"
& "mini_python\python.exe" -m pip install "scipy>=1.10.0"

Write-Host "`n[4/6] 安裝 AI 核心依賴..." -ForegroundColor Green
& "mini_python\python.exe" -m pip install "faster-whisper>=1.0.0"
& "mini_python\python.exe" -m pip install "ctranslate2>=3.24.0"

Write-Host "`n[5/6] 安裝音頻和機器學習庫..." -ForegroundColor Green
& "mini_python\python.exe" -m pip install "librosa>=0.10.0"
& "mini_python\python.exe" -m pip install "soundfile>=0.12.0"
& "mini_python\python.exe" -m pip install "scikit-learn>=1.3.0"

Write-Host "`n[6/6] 安裝工具庫..." -ForegroundColor Green
& "mini_python\python.exe" -m pip install "tqdm>=4.65.0"
& "mini_python\python.exe" -m pip install "requests>=2.31.0"
& "mini_python\python.exe" -m pip install "tokenizers>=0.15.0"

Write-Host "`n驗證安裝..." -ForegroundColor Yellow
Write-Host "核心模組檢查:" -ForegroundColor Yellow

$modules = @(
    @("numpy", "NumPy"),
    @("faster_whisper", "Faster-Whisper"),
    @("ctranslate2", "CTranslate2"),
    @("librosa", "Librosa"),
    @("soundfile", "SoundFile"),
    @("sklearn", "Scikit-learn"),
    @("tqdm", "TQDM"),
    @("requests", "Requests")
)

$successCount = 0
foreach ($module in $modules) {
    $moduleName = $module[0]
    $displayName = $module[1]
    
    $result = & "mini_python\python.exe" -c "import $moduleName; print('OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  $displayName : OK" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  $displayName : 失敗" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "安裝結果: $successCount/$($modules.Length) 個模組可用" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if ($successCount -ge ($modules.Length * 0.8)) {
    Write-Host "`n[成功] 嵌入式環境設置完成！" -ForegroundColor Green
    Write-Host "`n下一步:" -ForegroundColor White
    Write-Host "1. 執行: test_simplified_backend.bat" -ForegroundColor White
    Write-Host "2. 執行: npm run dev:simplified" -ForegroundColor White
} else {
    Write-Host "`n[警告] 部分依賴安裝失敗" -ForegroundColor Yellow
    Write-Host "請檢查網路連接並重試" -ForegroundColor White
}

Read-Host "`n按 Enter 鍵繼續"