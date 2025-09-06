# GitHub 認證指南 - KGKG-coder 倉庫推送

## 當前問題
已配置 git 為 KGKG-coder 身份，但需要認證憑據來推送到倉庫。

## 解決方案選項

### 方案1：Personal Access Token（推薦）
KGKG-coder 需要：

1. **創建 Personal Access Token**
   - 前往：https://github.com/settings/tokens
   - 點擊 "Generate new token (classic)"
   - 選擇權限：`repo` (完整倉庫權限)
   - 複製生成的 token

2. **使用 Token 推送**
   ```bash
   git remote set-url origin https://KGKG-coder:TOKEN@github.com/KGKG-coder/srt-go.git
   git push -u origin main
   ```

### 方案2：SSH 金鑰（更安全）
1. 生成 SSH 金鑰
2. 添加到 GitHub 帳戶
3. 使用 SSH URL 推送

### 方案3：GitHub CLI（最簡單）
```bash
gh auth login
gh repo clone KGKG-coder/srt-go
# 複製文件到新的目錄
# git add, commit, push
```

## 準備推送的內容
✅ 完整測試架構（Unit, Integration, Performance, E2E）
✅ GitHub Actions 工作流程（8 個文件）  
✅ 性能基準和監控系統
✅ 項目配置文件（requirements.txt, setup.py）

## 推送後即可激活
- GitHub Actions 自動觸發
- CI/CD 流水線開始運行
- 性能監控系統啟動

請提供 Personal Access Token 或告知偏好的認證方式！