const { spawn, exec } = require('child_process');
const { dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const https = require('https');

class EnvironmentManager {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.isInstalling = false;
  }

  // 檢查 Python 環境
  async checkPythonEnvironment() {
    return new Promise((resolve) => {
      exec('python --version', (error, stdout, stderr) => {
        if (error) {
          resolve({ installed: false, error: 'Python not found' });
        } else {
          const version = stdout.trim();
          resolve({ installed: true, version });
        }
      });
    });
  }

  // 檢查必要的 Python 包
  async checkRequiredPackages() {
    const requiredPackages = [
      'faster_whisper',
      'librosa', 
      'soundfile',
      'numpy',
      'scipy'
    ];

    const results = {};
    
    for (const pkg of requiredPackages) {
      try {
        await this.checkPackage(pkg);
        results[pkg] = true;
      } catch (error) {
        results[pkg] = false;
      }
    }

    return results;
  }

  checkPackage(packageName) {
    return new Promise((resolve, reject) => {
      exec(`python -c "import ${packageName}"`, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve(true);
        }
      });
    });
  }

  // 首次啟動環境檢查
  async performFirstRunCheck() {
    console.log('Performing first run environment check...');
    
    const { app } = require('electron');
    const IS_PACKAGED = app.isPackaged;
    
    // 檢查是否使用內嵌 Python
    const embeddedPythonPath = path.join(process.resourcesPath, 'mini_python', 'python.exe');
    
    if (IS_PACKAGED && fs.existsSync(embeddedPythonPath)) {
      console.log('Using embedded Python environment in packaged app');
      return { firstRun: false, environmentReady: true, usingEmbedded: true };
    }
    
    // 檢查是否是首次運行 - 使用多個可能的路徑
    const possibleConfigPaths = [
      path.join(__dirname, 'first-run-complete.flag'),
      path.join(process.resourcesPath, 'first-run-complete.flag'),
      path.join(app.getPath('userData'), 'runtime', 'first-run-complete.flag'),
      path.join(app.getPath('userData'), 'first-run-complete.flag')
    ];
    
    for (const configPath of possibleConfigPaths) {
      if (fs.existsSync(configPath)) {
        console.log(`Found first-run flag at: ${configPath}`);
        return { firstRun: false, environmentReady: true };
      }
    }
    
    console.log('No first-run flag found, proceeding with environment setup...');

    // 檢查系統 Python（僅在開發模式或沒有內嵌 Python 時）
    const pythonCheck = await this.checkPythonEnvironment();
    
    if (!pythonCheck.installed) {
      const result = await this.showEnvironmentSetupDialog('Python');
      if (result === 'install') {
        await this.installPython();
      } else {
        return { firstRun: true, environmentReady: false, cancelled: true };
      }
    }

    // 檢查 Python 包
    const packageCheck = await this.checkRequiredPackages();
    const missingPackages = Object.entries(packageCheck)
      .filter(([pkg, installed]) => !installed)
      .map(([pkg]) => pkg);

    if (missingPackages.length > 0) {
      const result = await this.showPackageInstallDialog(missingPackages);
      if (result === 'install') {
        await this.installRequiredPackages(missingPackages);
      } else {
        return { firstRun: true, environmentReady: false, cancelled: true };
      }
    }

    // 標記首次運行完成 - 在用戶數據目錄創建標記文件
    const flagPath = IS_PACKAGED 
      ? path.join(app.getPath('userData'), 'runtime', 'first-run-complete.flag')
      : path.join(__dirname, 'first-run-complete.flag');
    
    fs.writeFileSync(flagPath, new Date().toISOString());
    console.log(`First-run flag created at: ${flagPath}`);
    
    return { firstRun: true, environmentReady: true };
  }

  async showEnvironmentSetupDialog(component) {
    const result = await dialog.showMessageBox(this.mainWindow, {
      type: 'question',
      buttons: ['Install Automatically', 'Install Manually', 'Cancel'],
      defaultId: 0,
      title: 'Environment Setup Required',
      message: `${component} Environment Required`,
      detail: `SRT GO requires ${component} to function properly.\n\n` +
              `• Install Automatically: We'll download and install ${component} for you\n` +
              `• Install Manually: We'll guide you through manual installation\n` +
              `• Cancel: Exit the application`
    });

    switch (result.response) {
      case 0: return 'install';
      case 1: return 'manual';
      case 2: return 'cancel';
    }
  }

  async showPackageInstallDialog(missingPackages) {
    const packageList = missingPackages.join(', ');
    
    const result = await dialog.showMessageBox(this.mainWindow, {
      type: 'question',
      buttons: ['Install Now', 'Cancel'],
      defaultId: 0,
      title: 'Required Packages Missing',
      message: 'Python Packages Required',
      detail: `The following packages are required for AI subtitle generation:\n\n` +
              `${packageList}\n\n` +
              `Click "Install Now" to automatically install these packages.\n` +
              `This process may take several minutes.`
    });

    return result.response === 0 ? 'install' : 'cancel';
  }

  async installPython() {
    return new Promise((resolve, reject) => {
      this.isInstalling = true;
      
      // 顯示安裝進度
      this.showInstallationProgress('Downloading and installing Python...');

      const setupScript = path.join(__dirname, 'setup_environment.bat');
      const installProcess = spawn('cmd', ['/c', setupScript], {
        stdio: ['pipe', 'pipe', 'pipe'],
        encoding: 'utf8'
      });

      installProcess.stdout.on('data', (data) => {
        console.log('Python install:', data.toString());
        this.updateInstallationProgress(data.toString());
      });

      installProcess.stderr.on('data', (data) => {
        console.error('Python install error:', data.toString());
      });

      installProcess.on('close', (code) => {
        this.isInstalling = false;
        this.hideInstallationProgress();
        
        if (code === 0) {
          resolve(true);
        } else {
          reject(new Error(`Python installation failed with code ${code}`));
        }
      });
    });
  }

  async installRequiredPackages(packages) {
    return new Promise((resolve, reject) => {
      this.isInstalling = true;
      
      this.showInstallationProgress('Installing Python packages...');

      const installCmd = `python -m pip install ${packages.join(' ')}`;
      const installProcess = spawn('cmd', ['/c', installCmd], {
        stdio: ['pipe', 'pipe', 'pipe'],
        encoding: 'utf8'
      });

      installProcess.stdout.on('data', (data) => {
        console.log('Package install:', data.toString());
        this.updateInstallationProgress(data.toString());
      });

      installProcess.stderr.on('data', (data) => {
        console.error('Package install error:', data.toString());
      });

      installProcess.on('close', (code) => {
        this.isInstalling = false;
        this.hideInstallationProgress();
        
        if (code === 0) {
          dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'Installation Complete',
            message: 'Environment Setup Successful!',
            detail: 'All required components have been installed. You can now use SRT GO to generate subtitles.'
          });
          resolve(true);
        } else {
          reject(new Error(`Package installation failed with code ${code}`));
        }
      });
    });
  }

  showInstallationProgress(message) {
    // 向渲染進程發送安裝進度
    this.mainWindow.webContents.send('installation-progress', {
      type: 'start',
      message: message
    });
  }

  updateInstallationProgress(message) {
    this.mainWindow.webContents.send('installation-progress', {
      type: 'update',
      message: message
    });
  }

  hideInstallationProgress() {
    this.mainWindow.webContents.send('installation-progress', {
      type: 'complete'
    });
  }

  async showManualInstallGuide() {
    const result = await dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      buttons: ['Open Guide', 'Open Python Website', 'OK'],
      title: 'Manual Installation Guide',
      message: 'Manual Installation Required',
      detail: 'Please follow these steps:\n\n' +
              '1. Download Python from python.org\n' +
              '2. Install Python with "Add to PATH" option checked\n' +
              '3. Restart this application\n\n' +
              'The application will automatically install required packages on next startup.'
    });

    if (result.response === 1) {
      shell.openExternal('https://www.python.org/downloads/');
    }
  }
}

module.exports = EnvironmentManager;