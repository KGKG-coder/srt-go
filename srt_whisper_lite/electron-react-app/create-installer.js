const { MSICreator } = require('electron-wix-msi');
const path = require('path');

// 安裝檔配置
const msiCreator = new MSICreator({
  appDirectory: path.join(__dirname, 'dist', 'win-unpacked'),
  outputDirectory: path.join(__dirname, 'dist', 'installer'),
  
  // 基本信息
  description: 'SRT GO - Professional AI Subtitle Generator',
  exe: 'SRT GO - AI Subtitle Generator',
  name: 'SRT GO',
  manufacturer: 'SRT GO Team',
  version: '2.0.0',
  
  // UI 配置
  ui: {
    chooseDirectory: true,
    images: {
      background: path.join(__dirname, 'assets', 'installer-bg.jpg'),
      banner: path.join(__dirname, 'assets', 'installer-banner.jpg')
    }
  },
  
  // 快捷方式
  shortcutName: 'SRT GO',
  shortcutFolderName: 'SRT GO',
  
  // 升級代碼（用於版本更新）
  upgradeCode: 'A1B2C3D4-E5F6-7890-ABCD-EF1234567890'
});

// 創建安裝檔
async function createInstaller() {
  console.log('Creating MSI installer...');
  
  try {
    await msiCreator.create();
    
    const msiPath = await msiCreator.compile();
    console.log(`✅ Installer created successfully at: ${msiPath}`);
    
  } catch (error) {
    console.error('❌ Error creating installer:', error);
    process.exit(1);
  }
}

createInstaller();