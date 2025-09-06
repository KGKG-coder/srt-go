const builder = require('electron-builder');
const path = require('path');

// 超輕量級打包配置
const config = {
  appId: 'com.srtgo.minimalist',
  productName: 'SRT GO - AI 字幕生成工具',
  copyright: 'Copyright © 2025 SRT GO Team',
  
  directories: {
    buildResources: 'build',
    output: 'dist'
  },
  
  compression: 'maximum',
  removePackageScripts: true,
  
  files: [
    'main.js',
    'preload.js',
    'environment-manager.js',
    'setup_environment.bat',
    'refresh_path.bat',
    'react-app/build/index.html',
    'react-app/build/static/css/*.css',
    'react-app/build/static/js/*.js',
    'icon.ico',
    // 排除所有不必要的文件
    '!react-app/build/static/**/*.map',
    '!react-app/build/static/**/*.txt',
    '!react-app/build/asset-manifest.json',
    '!react-app/build/manifest.json',
    '!react-app/build/robots.txt',
    '!**/node_modules/**/test/**',
    '!**/node_modules/**/tests/**',
    '!**/node_modules/**/*.md',
    '!**/node_modules/**/README*',
    '!**/node_modules/**/LICENSE*',
    '!**/node_modules/**/CHANGELOG*',
    '!**/node_modules/**/*.d.ts',
    '!**/node_modules/**/examples/**',
    '!**/node_modules/**/docs/**',
    '!**/node_modules/**/.github/**'
  ],
  
  extraFiles: [
    {
      from: '../',
      to: 'resources/python',
      filter: [
        'electron_backend.py',
        'simplified_subtitle_core.py',
        'audio_processor.py',
        'semantic_processor.py', 
        'subtitle_formatter.py',
        'custom_corrections.json',
        'requirements.txt'
      ]
    }
  ],
  
  win: {
    target: [{
      target: 'nsis',
      arch: ['x64']
    }],
    icon: 'icon.ico',
    publisherName: 'SRT GO Team',
    requestedExecutionLevel: 'asInvoker',
    artifactName: '${productName}-${version}-Lite.${ext}',
    verifyUpdateCodeSignature: false
  },
  
  nsis: {
    oneClick: false,
    allowToChangeInstallationDirectory: true,
    allowElevation: true,
    installerIcon: 'icon.ico',
    uninstallerIcon: 'icon.ico',
    installerHeaderIcon: 'icon.ico',
    createDesktopShortcut: true,
    createStartMenuShortcut: true,
    shortcutName: 'SRT GO - AI 字幕生成工具',
    differentialPackage: false,
    packElevateHelper: false
  }
};

async function buildLite() {
  try {
    console.log('Building lite version...');
    await builder.build({
      targets: builder.Platform.WINDOWS.createTarget(),
      config: config
    });
    console.log('Lite build completed!');
  } catch (error) {
    console.error('Build failed:', error);
  }
}

buildLite();