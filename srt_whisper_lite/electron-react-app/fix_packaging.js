/**
 * 打包修復腳本 - 確保所有依賴都被正確包含
 */

const fs = require('fs');
const path = require('path');

// 讀取現有的 package.json
const packagePath = path.join(__dirname, 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

// 更新 extraFiles 配置，確保包含所有必要文件
packageJson.build.extraFiles = [
  // Python 腳本文件
  {
    "from": "../",
    "to": "resources/python",
    "filter": [
      "electron_backend.py",
      "simplified_subtitle_core.py",
      "audio_processor.py", 
      "semantic_processor.py",
      "subtitle_formatter.py",
      "config_manager.py",
      "i18n.py",
      "logo_manager.py",
      "custom_corrections.json",
      "user_config.json",
      "requirements.txt"
    ]
  },
  // 完整的 mini_python 環境
  {
    "from": "../mini_python",
    "to": "resources/mini_python",
    "filter": ["**/*"]  // 包含所有文件
  }
];

// 添加 asar 解包配置（確保 Python 可執行）
packageJson.build.asarUnpack = [
  "resources/mini_python/**/*",
  "resources/python/**/*"
];

// 寫回 package.json
fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2));

console.log('✅ 打包配置已修復！');
console.log('📝 已更新 extraFiles 配置');
console.log('📝 已添加 asarUnpack 配置');
console.log('\n下一步：執行 npm run build 重新打包');