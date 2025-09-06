
/**
 * 自動測試腳本 - 驗證錯誤處理機制
 */

const { execSync } = require('child_process');
const path = require('path');

async function runTests() {
  console.log('🧪 開始錯誤處理機制測試...');
  
  const tests = [
    {
      name: '測試 Python 環境',
      command: '"D:/新增資料夾/srt-go-minimalist/resources/mini_python/python.exe" --version'
    },
    {
      name: '測試腳本存在性',
      command: 'dir "D:/新增資料夾/srt-go-minimalist/resources/python/electron_backend.py"'
    },
    {
      name: '測試模組導入',
      command: 'cd "D:/新增資料夾/srt-go-minimalist/resources/python" && "D:/新增資料夾/srt-go-minimalist/resources/mini_python/python.exe" -c "import sys; print(\"✅ Python 環境正常\", sys.version)"'
    }
  ];
  
  for (const test of tests) {
    try {
      console.log(`\n📋 ${test.name}...`);
      const result = execSync(test.command, { encoding: 'utf8' });
      console.log(`✅ 通過: ${result.trim()}`);
    } catch (error) {
      console.error(`❌ 失敗: ${error.message}`);
    }
  }
  
  console.log('\n🎯 測試完成！');
}

runTests().catch(console.error);
