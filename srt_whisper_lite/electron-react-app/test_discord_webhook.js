// 測試Discord webhook
const fetch = require('node-fetch');

async function testDiscordWebhook() {
  const webhookUrl = 'https://discord.com/api/webhooks/1413541953316065382/-WyvN6D6EsZ3kgXsLyxxyX_-mHy14a13hcbFDwcDsZ6dfBMeKlkqNklnTfPll7qGcb13';
  
  const testPayload = {
    embeds: [{
      title: '🧪 SRT GO 測試訊息',
      color: 3447003, // 藍色
      fields: [
        {
          name: '📝 標題',
          value: '測試回報功能',
          inline: false
        },
        {
          name: '👤 測試者',
          value: 'Claude Code Assistant',
          inline: true
        },
        {
          name: '📧 聯絡信箱',
          value: 'test@example.com',
          inline: true
        },
        {
          name: '💬 詳細內容',
          value: '這是一個測試訊息，用於驗證SRT GO的Discord webhook回報功能是否正常運作。\n\n測試項目：\n✅ Webhook連接\n✅ Embed格式化\n✅ 中文顯示\n✅ 系統整合',
          inline: false
        },
        {
          name: '⚙️ 系統資訊',
          value: `測試時間: ${new Date().toLocaleString('zh-TW')}\n版本: SRT GO v2.2.1\n測試環境: Node.js`,
          inline: false
        }
      ],
      timestamp: new Date().toISOString(),
      footer: {
        text: 'SRT GO v2.2.1 用戶回報系統 - 測試模式'
      }
    }]
  };

  try {
    console.log('🚀 開始測試Discord webhook...');
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    });

    if (response.ok) {
      console.log('✅ 測試訊息發送成功！');
      console.log('📊 回應狀態:', response.status);
      console.log('🎯 Discord頻道應該已收到測試訊息');
      return true;
    } else {
      console.error('❌ 發送失敗');
      console.error('狀態碼:', response.status);
      console.error('錯誤訊息:', await response.text());
      return false;
    }
  } catch (error) {
    console.error('❌ 網路錯誤:', error.message);
    return false;
  }
}

// 執行測試
testDiscordWebhook();