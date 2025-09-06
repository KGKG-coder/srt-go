const builder = require('electron-builder');

async function buildFinalExecutable() {
  try {
    console.log('Building final SRT GO Enhanced v2.0 executable...');
    
    const result = await builder.build({
      targets: builder.Platform.WINDOWS.createTarget('dir'),
      config: {
        appId: 'com.srtgo.enhanced-final',
        productName: 'SRT GO Enhanced v2.0',
        directories: {
          output: 'dist_final'
        },
        files: [
          'main.js',
          'preload.js', 
          'environment-manager.js',
          'react-app/build/**/*',
          'icon.ico',
          '!react-app/build/static/**/*.map'
        ],
        extraResources: [
          {
            from: 'python',
            to: 'resources/python'
          },
          {
            from: 'mini_python', 
            to: 'resources/mini_python'
          }
        ],
        win: {
          target: 'dir',
          icon: 'icon.ico'
        },
        asar: true,
        asarUnpack: [
          'resources/**/*'
        ]
      }
    });
    
    console.log('Build completed! Check dist_final/win-unpacked/');
    
  } catch (error) {
    console.error('Build failed:', error.message);
  }
}

buildFinalExecutable();