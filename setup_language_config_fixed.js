const fs = require('fs');
const path = require('path');

/**
 * SRT GO 語言配置設定工具 - 修復版本
 */

class LanguageConfigurator {
    constructor() {
        this.baseDir = __dirname;
        this.appDir = path.join(this.baseDir, 'srt_whisper_lite', 'electron-react-app');
        this.reactAppDir = path.join(this.appDir, 'react-app', 'src');
        this.pythonDir = path.join(this.appDir, 'python');
        
        this.supportedLanguages = {
            'en': 'English',
            'zh-TW': '繁體中文',
            'zh-CN': '简体中文',
            'ja': '日本語',
            'ko': '한국어'
        };
    }

    /**
     * 設置應用程式語言
     */
    async setupLanguage(language) {
        if (!this.supportedLanguages[language]) {
            throw new Error(`不支援的語言: ${language}`);
        }

        console.log(`🌐 設置語言為: ${this.supportedLanguages[language]} (${language})`);

        try {
            // 1. 創建語言配置檔
            await this.createLanguageConfig(language);
            
            // 2. 更新 Python 後端配置（簡化版本）
            await this.updatePythonConfig(language);
            
            console.log('✅ 語言配置設置完成！');
            
        } catch (error) {
            console.error('❌ 設置語言配置失敗:', error);
            throw error;
        }
    }

    /**
     * 創建語言配置檔
     */
    async createLanguageConfig(language) {
        const config = {
            selectedLanguage: language,
            supportedLanguages: this.supportedLanguages,
            setupTime: new Date().toISOString(),
            version: '2.2.1',
            languageChangeable: false
        };

        // 確保目錄存在
        if (!fs.existsSync(this.appDir)) {
            fs.mkdirSync(this.appDir, { recursive: true });
        }

        // 保存到應用目錄
        const configPath = path.join(this.appDir, 'language_config.json');
        await fs.promises.writeFile(configPath, JSON.stringify(config, null, 2), 'utf8');
        console.log(`💾 語言配置已保存: ${configPath}`);

        // 保存到 React public 目錄
        const publicDir = path.join(this.appDir, 'react-app', 'public');
        if (!fs.existsSync(publicDir)) {
            fs.mkdirSync(publicDir, { recursive: true });
        }
        
        const publicConfigPath = path.join(publicDir, 'language_config.json');
        await fs.promises.writeFile(publicConfigPath, JSON.stringify(config, null, 2), 'utf8');
        console.log(`💾 React public 配置已保存: ${publicConfigPath}`);
    }

    /**
     * 更新 Python 後端配置（簡化版本）
     */
    async updatePythonConfig(language) {
        console.log('🔧 更新 Python 後端配置...');

        const i18nPath = path.join(this.pythonDir, 'i18n.py');
        
        if (fs.existsSync(i18nPath)) {
            let content = await fs.promises.readFile(i18nPath, 'utf8');
            
            // 修改預設語言（更簡單的方式）
            if (content.includes("default_language: str = '")) {
                content = content.replace(
                    /default_language: str = '[^']*'/,
                    `default_language: str = '${language}'`
                );
            } else if (content.includes('default_language = \'')) {
                content = content.replace(
                    /default_language = '[^']*'/,
                    `default_language = '${language}'`
                );
            }
            
            await fs.promises.writeFile(i18nPath, content, 'utf8');
            console.log('✅ Python i18n 配置已更新');
        } else {
            console.log('⚠️ Python i18n 文件不存在，跳過更新');
        }
    }

    /**
     * 驗證語言設定
     */
    async validateLanguageSetup(language) {
        console.log('🔍 驗證語言設定...');

        const configPath = path.join(this.appDir, 'language_config.json');
        
        if (!fs.existsSync(configPath)) {
            throw new Error('語言配置檔不存在');
        }

        const config = JSON.parse(await fs.promises.readFile(configPath, 'utf8'));
        
        if (config.selectedLanguage !== language) {
            throw new Error('語言配置不匹配');
        }

        console.log('✅ 語言設定驗證成功');
        return true;
    }
}

// 命令行介面
if (require.main === module) {
    const args = process.argv.slice(2);
    const language = args[0];

    if (!language) {
        console.log(`
使用方法: node setup_language_config_fixed.js <language_code>

支援的語言:
  en     - English
  zh-TW  - 繁體中文  
  zh-CN  - 简体中文
  ja     - 日本語
  ko     - 한국어

範例:
  node setup_language_config_fixed.js zh-TW
  node setup_language_config_fixed.js en
        `);
        process.exit(1);
    }

    const configurator = new LanguageConfigurator();
    
    configurator.setupLanguage(language)
        .then(() => {
            console.log(`\n🎉 SRT GO 已成功設置為 ${configurator.supportedLanguages[language]} 介面！`);
            console.log('現在可以構建應用程式了。');
        })
        .catch(error => {
            console.error('\n❌ 設置失敗:', error.message);
            process.exit(1);
        });
}

module.exports = LanguageConfigurator;