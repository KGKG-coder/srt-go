const builder = require('electron-builder');
const path = require('path');

async function buildExecutable() {
  try {
    console.log('🚀 Building standalone SRT GO Enhanced v2.0 executable...');
    
    const result = await builder.build({
      targets: builder.Platform.WINDOWS.createTarget('dir', builder.Arch.x64),
      config: {
        appId: 'com.srtgo.enhanced-v2',
        productName: 'SRT GO Enhanced v2.0',
        copyright: 'Copyright © 2025 SRT GO AI Technologies',
        directories: {
          buildResources: 'build',
          output: 'dist_exe'
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
          },
          {
            from: 'models',
            to: 'resources/models',
            filter: ['**/*']
          }
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
          'resources/python/**/*',
          'resources/models/**/*'
        ]
      }
    });
    
    console.log('✅ Build completed successfully!');
    console.log('📁 Executable location: dist_exe/win-unpacked/');
    
  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

buildExecutable();