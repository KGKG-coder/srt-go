const builder = require('electron-builder');
const path = require('path');

async function buildLightweightExecutable() {
  try {
    console.log('🚀 Building lightweight SRT GO Enhanced v2.0 executable...');
    console.log('📝 Models will be downloaded on first run');
    
    const result = await builder.build({
      targets: builder.Platform.WINDOWS.createTarget('dir', builder.Arch.x64),
      config: {
        appId: 'com.srtgo.enhanced-v2-lightweight',
        productName: 'SRT GO Enhanced v2.0',
        copyright: 'Copyright © 2025 SRT GO AI Technologies',
        directories: {
          buildResources: 'build',
          output: 'dist_lightweight'
        },
        compression: 'maximum',
        removePackageScripts: true,
        files: [
          'main.js',
          'preload.js',
          'environment-manager.js',
          'react-app/build/**/*',
          'icon.ico',
          '!react-app/build/static/**/*.map',
          '!**/node_modules/**/test/**',
          '!**/node_modules/**/*.md'
        ],
        extraResources: [
          {
            from: 'python',
            to: 'resources/python',
            filter: ['**/*', '!**/*.pyc', '!**/__pycache__/**']
          },
          {
            from: 'mini_python',
            to: 'resources/mini_python',
            filter: ['**/*', '!**/*.pyc', '!**/__pycache__/**']
          }
          // 不包含 models 目錄 - 將在首次運行時下載
        ],
        win: {
          target: {
            target: 'dir',
            arch: 'x64'
          },
          icon: 'icon.ico',
          publisherName: 'SRT GO AI Technologies',
          requestedExecutionLevel: 'asInvoker'
        },
        asar: {
          smartUnpack: true
        },
        asarUnpack: [
          'resources/mini_python/**/*',
          'resources/python/**/*'
        ]
      }
    });
    
    console.log('✅ Lightweight build completed successfully!');
    console.log('📁 Executable location: dist_lightweight/win-unpacked/');
    console.log('📝 Note: AI models will be downloaded automatically on first run');
    
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

buildLightweightExecutable();