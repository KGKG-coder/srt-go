// 多語言翻譯資源
export const translations = {
  'zh-TW': {
    // 繁體中文
    app: {
      title: 'SRT GO',
      subtitle: 'AI 字幕生成工具',
      startProcessing: '開始生成字幕',
      pauseProcessing: '暫停處理',
      resumeProcessing: '繼續處理',
      processing: '處理中...',
      paused: '已暫停'
    },
    tabs: {
      files: '檔案選擇',
      corrections: '文字修正', 
      settings: '設定'
    },
    fileSelection: {
      title: '檔案選擇',
      subtitle: '選擇要生成字幕的音訊或影片檔案，支援拖拽上傳',
      dropzone: '拖拽檔案到此處或點擊選擇',
      dropzoneActive: '放開以上傳檔案',
      supportedFormats: '支援 MP4, MP3, WAV, AVI, MOV, MKV, M4A, FLAC, OGG 格式',
      selectedFiles: '已選擇的檔案',
      noFiles: '尚未選擇任何檔案',
      startUpload: '開始上傳您的音訊或影片檔案',
      removeFile: '移除檔案',
      unknownSize: '未知大小',
      filesSelected: '已選擇檔案',
      totalSize: '總大小'
    },
    corrections: {
      title: '自定義文字修正',
      subtitle: '設定常見的語音識別錯誤修正規則，提升字幕品質',
      addRule: '添加修正規則',
      originalText: '原文字',
      replacementText: '替換文字',
      replaceHint: '替換後的文字（空白表示刪除）',
      enable: '啟用此規則',
      save: '保存',
      cancel: '取消',
      add: '添加',
      edit: '編輯',
      delete: '刪除',
      noRules: '尚未設定任何修正規則',
      addRulesHint: '添加規則來自動修正常見的語音識別錯誤',
      ruleCount: '修正規則',
      suggestions: '建議規則',
      suggestionsHint: '點擊下方建議快速添加常用的修正規則',
      empty: '(空)',
      remove: '(刪除)'
    },
    settings: {
      title: '設定',
      subtitle: '調整 AI 模型、語言和輸出設定來優化字幕生成效果',
      aiModel: 'AI 模型',
      modelDescription: '選擇不同的模型以平衡處理速度和準確度',
      professionalVersion: '專業版',
      language: '語言',
      languageDescription: '指定音訊語言可提高識別準確度',
      outputLanguage: '輸出語言',
      outputLanguageDescription: '翻譯字幕，或保持與原音訊相同',
      
      // 新的動態語言選擇標籤
      audioLanguage: '音訊語言',
      audioLanguageDesc: '指定音訊語言可提高識別準確度',
      chineseOptions: '中文輸出選項',
      chineseOptionsDesc: '選擇繁體、簡體或翻譯為英文',
      englishOptions: '輸出選項',
      englishOptionsDesc: '英文音訊只能保持原文（Whisper 不支援英文翻譯）',
      translationOptions: '翻譯選項',
      translationOptionsDesc: '選擇保持原文或翻譯為英文',
      outputOptions: '輸出選項',
      autoDetectOutput: '輸出選項',
      autoDetectDesc: '音訊語言自動檢測後的輸出選擇',
      keepOriginal: '保持原文',
      translateToEnglish: '翻譯為英文',
      
      outputFormat: '輸出格式', 
      formatDescription: '選擇字幕檔案的輸出格式',
      outputFolder: '輸出資料夾',
      folderDescription: '選擇字幕檔案的儲存位置，留空則儲存在原檔案相同位置',
      useDefault: '使用預設位置（與原檔案相同資料夾）',
      select: '選擇',
      advanced: '進階選項',
      enableCorrections: '啟用自定義文字修正',
      correctionsDescription: '使用您設定的修正規則來優化字幕文字',
      interfaceLanguage: '介面語言',
      interfaceLanguageDescription: '選擇應用程式的顯示語言',
      tip: '提示',
      modelDownloadTip: '第一次使用選定的模型時，系統會自動下載模型檔案，這可能需要一些時間。下載完成後，後續使用會更加快速。',
      
      // 建議與bug回報
      feedback: '建議與bug回報',
      feedbackSubtitle: '向開發團隊回報問題或提供改進建議，幫助我們改善產品',
      feedbackTitle: '標題',
      feedbackTitlePlaceholder: '請簡述您的問題或建議',
      feedbackName: '怎麼稱呼您',
      feedbackNamePlaceholder: '您的稱呼或暱稱',
      feedbackEmail: '聯絡信箱',
      feedbackEmailPlaceholder: '您的電子信箱',
      feedbackMessage: '詳細內容',
      feedbackMessagePlaceholder: '請詳細描述您遇到的問題或改進建議...',
      feedbackSubmit: '送出回報',
      feedbackSubmitting: '送出中...',
      feedbackSuccess: '回報已送出',
      feedbackSuccessMessage: '感謝您的回報！我們會盡快處理您的意見。',
      feedbackError: '送出失敗',
      feedbackErrorMessage: '送出過程中發生錯誤，請稍後再試。',
      feedbackRequired: '此欄位為必填',
      enableGpuAcceleration: '啟用GPU加速',
      gpuAccelerationDesc: '使用顯卡加速處理，需要支援CUDA的NVIDIA顯卡。如果GPU不可用，系統會自動降級到CPU模式。',
      submitAnotherReport: '送出另一個回報',
      retrySubmission: '重新嘗試',
      
      // 錯誤處理面板
      errorSeverity: {
        critical: '嚴重錯誤',
        high: '重要錯誤',
        medium: '警告',
        low: '提示',
        default: '一般錯誤'
      }
    },
    models: {
      base: {
        name: 'Base', 
        description: '平衡速度與準確度'
      },
      medium: {
        name: 'Medium',
        description: '高準確度，推薦選項'
      },
      large: {
        name: 'Large',
        description: '最高準確度，較慢速度'
      }
    },
    languages: {
      auto: '自動檢測',
      same: '與原語言相同',
      zh: '中文',
      'zh-TW': '繁體中文',
      'zh-CN': '簡體中文',
      en: 'English',
      ja: '日本語',
      ko: '한국어',
      es: 'Español',
      fr: 'Français',
      de: 'Deutsch',
      it: 'Italiano',
      pt: 'Português',
      ru: 'Русский',
      ar: 'العربية'
    },
    formats: {
      srt: {
        name: 'SRT',
        description: '最常用的字幕格式'
      },
      vtt: {
        name: 'WebVTT',
        description: '網頁字幕格式'
      },
      txt: {
        name: 'TXT',
        description: '純文字格式'
      }
    },
    progress: {
      processing: '正在處理字幕',
      completed: '處理完成',
      error: '處理失敗',
      paused: '處理已暫停',
      processingDesc: '處理中',
      completedDesc: '所有檔案已成功處理',
      errorDesc: '處理過程中發生錯誤',
      pausedDesc: '處理已暫停，點擊繼續按鈕恢復',
      estimatedTime: '預計剩餘',
      overallProgress: '整體進度',
      currentFile: '當前檔案',
      filesCompleted: '已完成',
      filesRemaining: '剩餘',
      filesTotal: '總計',
      keepOpen: '請保持程式開啟，處理時間取決於檔案大小和模型選擇',
      allCompleted: '所有字幕檔案已成功生成並儲存',
      errorOccurred: '處理過程中發生錯誤，請檢查檔案和設定'
    },
    toast: {
      success: '成功',
      error: '錯誤',
      warning: '警告',
      info: '提示',
      selectFiles: '請選擇要處理的檔案',
      processingFailed: '處理失敗：'
    }
  },
  'zh-CN': {
    // 简体中文
    app: {
      title: 'SRT GO',
      subtitle: 'AI 字幕生成工具',
      startProcessing: '开始生成字幕',
      pauseProcessing: '暂停处理',
      resumeProcessing: '继续处理',
      processing: '处理中...',
      paused: '已暂停'
    },
    tabs: {
      files: '文件选择',
      corrections: '文字修正',
      settings: '设置'
    },
    fileSelection: {
      title: '文件选择',
      subtitle: '选择要生成字幕的音频或视频文件，支持拖拽上传',
      dropzone: '拖拽文件到此处或点击选择',
      dropzoneActive: '放开以上传文件',
      supportedFormats: '支持 MP4, MP3, WAV, AVI, MOV, MKV, M4A, FLAC, OGG 格式',
      selectedFiles: '已选择的文件',
      noFiles: '尚未选择任何文件',
      startUpload: '开始上传您的音频或视频文件',
      removeFile: '移除文件',
      unknownSize: '未知大小',
      filesSelected: '已选择文件',
      totalSize: '总大小'
    },
    corrections: {
      title: '自定义文字修正',
      subtitle: '设置常见的语音识别错误修正规则，提升字幕质量',
      addRule: '添加修正规则',
      originalText: '原文字',
      replacementText: '替换文字',
      replaceHint: '替换后的文字（空白表示删除）',
      enable: '启用此规则',
      save: '保存',
      cancel: '取消',
      add: '添加',
      edit: '编辑',
      delete: '删除',
      noRules: '尚未设置任何修正规则',
      addRulesHint: '添加规则来自动修正常见的语音识别错误',
      ruleCount: '修正规则',
      suggestions: '建议规则',
      suggestionsHint: '点击下方建议快速添加常用的修正规则',
      empty: '(空)',
      remove: '(删除)'
    },
    settings: {
      title: '设置',
      subtitle: '调整 AI 模型、语言和输出设置来优化字幕生成效果',
      aiModel: 'AI 模型',
      modelDescription: '选择不同的模型以平衡处理速度和准确度',
      language: '语言',
      languageDescription: '指定音频语言可提高识别准确度',
      outputLanguage: '输出语言',
      outputLanguageDescription: '翻译字幕，或保持与原音频相同',
      
      // 新的动态语言选择标签
      audioLanguage: '音频语言',
      audioLanguageDesc: '指定音频语言可提高识别准确度',
      chineseOptions: '中文输出选项',
      chineseOptionsDesc: '选择繁体、简体或翻译为英文',
      englishOptions: '输出选项',
      englishOptionsDesc: '英文音频只能保持原文（Whisper 不支持英文翻译）',
      translationOptions: '翻译选项',
      translationOptionsDesc: '选择保持原文或翻译为英文',
      outputOptions: '输出选项',
      autoDetectOutput: '输出选项',
      autoDetectDesc: '音频语言自动检测后的输出选择',
      keepOriginal: '保持原文',
      translateToEnglish: '翻译为英文',
      
      outputFormat: '输出格式',
      formatDescription: '选择字幕文件的输出格式',
      outputFolder: '输出文件夹',
      folderDescription: '选择字幕文件的保存位置，留空则保存在原文件相同位置',
      useDefault: '使用默认位置（与原文件相同文件夹）',
      select: '选择',
      advanced: '高级选项',
      enableCorrections: '启用自定义文字修正',
      correctionsDescription: '使用您设置的修正规则来优化字幕文字',
      interfaceLanguage: '界面语言',
      interfaceLanguageDescription: '选择应用程序的显示语言',
      tip: '提示',
      modelDownloadTip: '第一次使用选定的模型时，系统会自动下载模型文件，这可能需要一些时间。下载完成后，后续使用会更加快速。',
      
      // 建议与bug回报
      feedback: '建议与bug回报',
      feedbackSubtitle: '向开发团队回报问题或提供改进建议，帮助我们改善产品',
      feedbackTitle: '标题',
      feedbackTitlePlaceholder: '请简述您的问题或建议',
      feedbackName: '怎么称呼您',
      feedbackNamePlaceholder: '您的称呼或昵称',
      feedbackEmail: '联系邮箱',
      feedbackEmailPlaceholder: '您的电子邮箱',
      feedbackMessage: '详细内容',
      feedbackMessagePlaceholder: '请详细描述您遇到的问题或改进建议...',
      feedbackSubmit: '提交回报',
      feedbackSubmitting: '提交中...',
      feedbackSuccess: '回报已提交',
      feedbackSuccessMessage: '感谢您的回报！我们会尽快处理您的意见。',
      feedbackError: '提交失败',
      feedbackErrorMessage: '提交过程中发生错误，请稍后再试。',
      feedbackRequired: '此字段为必填',
      enableGpuAcceleration: '启用GPU加速',
      gpuAccelerationDesc: '使用显卡加速处理，需要支持CUDA的NVIDIA显卡。如果GPU不可用，系统会自动降级到CPU模式。',
      submitAnotherReport: '提交另一个回报',
      retrySubmission: '重新尝试',
      
      // 错误处理面板
      errorSeverity: {
        critical: '严重错误',
        high: '重要错误',
        medium: '警告',
        low: '提示',
        default: '一般错误'
      }
    },
    models: {
      tiny: {
        name: 'Tiny',
        description: '最快速度，准确度较低'
      },
      base: {
        name: 'Base',
        description: '平衡速度与准确度'
      },
      small: {
        name: 'Small',
        description: '较好准确度，速度适中'
      },
      medium: {
        name: 'Medium',
        description: '高准确度，推荐选项'
      },
      large: {
        name: 'Large',
        description: '最高准确度，较慢速度'
      }
    },
    languages: {
      auto: '自动检测',
      same: '与原语言相同',
      zh: '中文',
      'zh-TW': '繁体中文',
      'zh-CN': '简体中文',
      en: 'English',
      ja: '日本語',
      ko: '한국어',
      es: 'Español',
      fr: 'Français',
      de: 'Deutsch',
      it: 'Italiano',
      pt: 'Português',
      ru: 'Русский',
      ar: 'العربية'
    },
    formats: {
      srt: {
        name: 'SRT',
        description: '最常用的字幕格式'
      },
      vtt: {
        name: 'WebVTT',
        description: '网页字幕格式'
      },
      txt: {
        name: 'TXT',
        description: '纯文本格式'
      }
    },
    progress: {
      processing: '正在处理字幕',
      completed: '处理完成',
      error: '处理失败',
      paused: '处理已暂停',
      processingDesc: '处理中',
      completedDesc: '所有文件已成功处理',
      errorDesc: '处理过程中发生错误',
      pausedDesc: '处理已暂停，点击继续按钮恢复',
      estimatedTime: '预计剩余',
      overallProgress: '整体进度',
      currentFile: '当前文件',
      filesCompleted: '已完成',
      filesRemaining: '剩余',
      filesTotal: '总计',
      keepOpen: '请保持程序开启，处理时间取决于文件大小和模型选择',
      allCompleted: '所有字幕文件已成功生成并保存',
      errorOccurred: '处理过程中发生错误，请检查文件和设置'
    },
    toast: {
      success: '成功',
      error: '错误',
      warning: '警告',
      info: '提示',
      selectFiles: '请选择要处理的文件',
      processingFailed: '处理失败：'
    }
  },
  'en': {
    // English
    app: {
      title: 'SRT GO',
      subtitle: 'AI Subtitle Generator',
      startProcessing: 'Generate Subtitles',
      pauseProcessing: 'Pause Processing',
      resumeProcessing: 'Resume Processing',
      processing: 'Processing...',
      paused: 'Paused'
    },
    tabs: {
      files: 'File Selection',
      corrections: 'Text Corrections',
      settings: 'Settings'
    },
    fileSelection: {
      title: 'File Selection',
      subtitle: 'Select audio or video files to generate subtitles, drag and drop supported',
      dropzone: 'Drag files here or click to select',
      dropzoneActive: 'Drop to upload files',
      supportedFormats: 'Supports MP4, MP3, WAV, AVI, MOV, MKV, M4A, FLAC, OGG formats',
      selectedFiles: 'Selected Files',
      noFiles: 'No files selected',
      startUpload: 'Start uploading your audio or video files',
      removeFile: 'Remove file',
      unknownSize: 'Unknown size',
      filesSelected: 'Files Selected',
      totalSize: 'Total Size'
    },
    corrections: {
      title: 'Custom Text Corrections',
      subtitle: 'Set common speech recognition error correction rules to improve subtitle quality',
      addRule: 'Add Correction Rule',
      originalText: 'Original Text',
      replacementText: 'Replacement Text',
      replaceHint: 'Replacement text (leave empty to delete)',
      enable: 'Enable this rule',
      save: 'Save',
      cancel: 'Cancel',
      add: 'Add',
      edit: 'Edit',
      delete: 'Delete',
      noRules: 'No correction rules set',
      addRulesHint: 'Add rules to automatically correct common speech recognition errors',
      ruleCount: 'Correction Rules',
      suggestions: 'Suggested Rules',
      suggestionsHint: 'Click suggestions below to quickly add common correction rules',
      empty: '(empty)',
      remove: '(delete)'
    },
    settings: {
      title: 'Settings',
      subtitle: 'Adjust AI model, language and output settings to optimize subtitle generation',
      aiModel: 'AI Model',
      modelDescription: 'Choose different models to balance processing speed and accuracy',
      language: 'Language',
      languageDescription: 'Specify audio language to improve recognition accuracy',
      outputLanguage: 'Output Language',
      outputLanguageDescription: 'Translate subtitles, or keep same as original',
      
      // New dynamic language selection labels
      audioLanguage: 'Audio Language',
      audioLanguageDesc: 'Specify audio language to improve recognition accuracy',
      chineseOptions: 'Chinese Output Options',
      chineseOptionsDesc: 'Choose Traditional, Simplified or translate to English',
      englishOptions: 'Output Options',
      englishOptionsDesc: 'English audio can only keep original text (Whisper does not support English translation)',
      translationOptions: 'Translation Options',
      translationOptionsDesc: 'Choose to keep original or translate to English',
      outputOptions: 'Output Options',
      autoDetectOutput: 'Output Options',
      autoDetectDesc: 'Output choice after automatic audio language detection',
      keepOriginal: 'Keep Original',
      translateToEnglish: 'Translate to English',
      
      outputFormat: 'Output Format',
      formatDescription: 'Choose subtitle file output format',
      outputFolder: 'Output Folder',
      folderDescription: 'Choose where to save subtitle files, leave empty to save in same location as source',
      useDefault: 'Use default location (same folder as source file)',
      select: 'Select',
      advanced: 'Advanced Options',
      enableCorrections: 'Enable Custom Text Corrections',
      correctionsDescription: 'Use your correction rules to optimize subtitle text',
      interfaceLanguage: 'Interface Language',
      interfaceLanguageDescription: 'Choose the display language for the application',
      tip: 'Tip',
      modelDownloadTip: 'When using a model for the first time, the system will automatically download the model files, which may take some time. Subsequent uses will be faster.',
      
      // Feedback & Bug Report
      feedback: 'Feedback & Bug Report',
      feedbackSubtitle: 'Report issues or suggestions to help us improve the product',
      feedbackTitle: 'Title',
      feedbackTitlePlaceholder: 'Brief description of your issue or suggestion',
      feedbackName: 'How to address you',
      feedbackNamePlaceholder: 'Your name or nickname',
      feedbackEmail: 'Contact Email',
      feedbackEmailPlaceholder: 'Your email address',
      feedbackMessage: 'Detailed Content',
      feedbackMessagePlaceholder: 'Please describe your issue or suggestion in detail...',
      feedbackSubmit: 'Submit Report',
      feedbackSubmitting: 'Submitting...',
      feedbackSuccess: 'Report Submitted',
      feedbackSuccessMessage: 'Thank you for your report! We will process your feedback as soon as possible.',
      feedbackError: 'Submission Failed',
      feedbackErrorMessage: 'An error occurred during submission. Please try again later.',
      feedbackRequired: 'This field is required',
      enableGpuAcceleration: 'Enable GPU Acceleration',
      gpuAccelerationDesc: 'Use GPU acceleration for processing. Requires CUDA-compatible NVIDIA GPU. If GPU is unavailable, system will automatically fall back to CPU mode.',
      submitAnotherReport: 'Submit another report',
      retrySubmission: 'Retry submission',
      
      // Error handling panel
      errorSeverity: {
        critical: 'Critical Error',
        high: 'High Priority Error',
        medium: 'Warning',
        low: 'Info',
        default: 'General Error'
      }
    },
    models: {
      tiny: {
        name: 'Tiny',
        description: 'Fastest speed, lower accuracy'
      },
      base: {
        name: 'Base',
        description: 'Balanced speed and accuracy'
      },
      small: {
        name: 'Small',
        description: 'Better accuracy, moderate speed'
      },
      medium: {
        name: 'Medium',
        description: 'High accuracy, recommended'
      },
      large: {
        name: 'Large',
        description: 'Highest accuracy, slower speed'
      }
    },
    languages: {
      auto: 'Auto Detect',
      same: 'Same as Original',
      zh: 'Chinese',
      'zh-TW': 'Traditional Chinese',
      'zh-CN': 'Simplified Chinese',
      en: 'English',
      ja: 'Japanese',
      ko: 'Korean',
      es: 'Spanish',
      fr: 'French',
      de: 'German',
      it: 'Italian',
      pt: 'Portuguese',
      ru: 'Russian',
      ar: 'Arabic'
    },
    formats: {
      srt: {
        name: 'SRT',
        description: 'Most common subtitle format'
      },
      vtt: {
        name: 'WebVTT',
        description: 'Web subtitle format'
      },
      txt: {
        name: 'TXT',
        description: 'Plain text format'
      }
    },
    progress: {
      processing: 'Processing Subtitles',
      completed: 'Processing Complete',
      error: 'Processing Failed',
      paused: 'Processing Paused',
      processingDesc: 'Processing',
      completedDesc: 'All files processed successfully',
      errorDesc: 'Error occurred during processing',
      pausedDesc: 'Processing paused, click resume to continue',
      estimatedTime: 'Time Remaining',
      overallProgress: 'Overall Progress',
      currentFile: 'Current File',
      filesCompleted: 'Completed',
      filesRemaining: 'Remaining',
      filesTotal: 'Total',
      keepOpen: 'Please keep the program open, processing time depends on file size and model selection',
      allCompleted: 'All subtitle files have been successfully generated and saved',
      errorOccurred: 'Error occurred during processing, please check files and settings'
    },
    toast: {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info',
      selectFiles: 'Please select files to process',
      processingFailed: 'Processing failed: '
    }
  },
  'ja': {
    // 日本語
    app: {
      title: 'SRT GO',
      subtitle: 'AI字幕生成ツール',
      startProcessing: '字幕を生成',
      pauseProcessing: '処理を一時停止',
      resumeProcessing: '処理を再開',
      processing: '処理中...',
      paused: '一時停止中'
    },
    tabs: {
      files: 'ファイル選択',
      corrections: 'テキスト修正',
      settings: '設定'
    },
    fileSelection: {
      title: 'ファイル選択',
      subtitle: '字幕を生成する音声・動画ファイルを選択してください。ドラッグ＆ドロップ対応',
      dropzone: 'ここにファイルをドラッグまたはクリックして選択',
      dropzoneActive: 'ドロップしてアップロード',
      supportedFormats: 'MP4, MP3, WAV, AVI, MOV, MKV, M4A, FLAC, OGG形式に対応',
      selectedFiles: '選択したファイル',
      noFiles: 'ファイルが選択されていません',
      startUpload: '音声・動画ファイルのアップロードを開始',
      removeFile: 'ファイルを削除',
      unknownSize: 'サイズ不明',
      filesSelected: '選択したファイル',
      totalSize: '合計サイズ'
    },
    corrections: {
      title: 'カスタムテキスト修正',
      subtitle: '音声認識の一般的なエラーを修正するルールを設定し、字幕の品質を向上',
      addRule: '修正ルールを追加',
      originalText: '元のテキスト',
      replacementText: '置換テキスト',
      replaceHint: '置換後のテキスト（空白で削除）',
      enable: 'このルールを有効化',
      save: '保存',
      cancel: 'キャンセル',
      add: '追加',
      edit: '編集',
      delete: '削除',
      noRules: '修正ルールが設定されていません',
      addRulesHint: '一般的な音声認識エラーを自動修正するルールを追加',
      ruleCount: '修正ルール',
      suggestions: '推奨ルール',
      suggestionsHint: '下の推奨をクリックして一般的な修正ルールを素早く追加',
      empty: '(空)',
      remove: '(削除)'
    },
    settings: {
      title: '設定',
      subtitle: 'AIモデル、言語、出力設定を調整して字幕生成を最適化',
      aiModel: 'AIモデル',
      modelDescription: '処理速度と精度のバランスを取るモデルを選択',
      language: '言語',
      languageDescription: '音声言語を指定して認識精度を向上',
      outputLanguage: '出力言語',
      outputLanguageDescription: '字幕を翻訳、または元の言語のまま',
      
      // 動的言語選択ラベル
      audioLanguage: '音声言語',
      audioLanguageDesc: '音声言語を指定して認識精度を向上',
      outputOptions: '出力オプション',
      autoDetectOutput: '出力オプション',
      autoDetectDesc: '音声言語の自動検出後の出力選択',
      keepOriginal: 'オリジナルを保持',
      translateToEnglish: '英語に翻訳',
      
      outputFormat: '出力形式',
      formatDescription: '字幕ファイルの出力形式を選択',
      outputFolder: '出力フォルダ',
      folderDescription: '字幕ファイルの保存場所を選択。空欄の場合は元ファイルと同じ場所に保存',
      useDefault: 'デフォルトの場所を使用（元ファイルと同じフォルダ）',
      select: '選択',
      advanced: '詳細オプション',
      enableCorrections: 'カスタムテキスト修正を有効化',
      correctionsDescription: '設定した修正ルールを使用して字幕テキストを最適化',
      interfaceLanguage: 'インターフェース言語',
      interfaceLanguageDescription: 'アプリケーションの表示言語を選択',
      tip: 'ヒント',
      modelDownloadTip: '選択したモデルを初めて使用する際、システムが自動的にモデルファイルをダウンロードします。これには時間がかかる場合があります。ダウンロード完了後は高速に動作します。',
      
      // フィードバック・バグレポート
      feedback: 'フィードバック・バグレポート',
      feedbackSubtitle: '問題や改善提案をご報告いただき、製品改善にご協力ください',
      feedbackTitle: 'タイトル',
      feedbackTitlePlaceholder: '問題や提案の概要をお書きください',
      feedbackName: 'お名前',
      feedbackNamePlaceholder: 'お名前またはニックネーム',
      feedbackEmail: '連絡先メール',
      feedbackEmailPlaceholder: 'メールアドレス',
      feedbackMessage: '詳細内容',
      feedbackMessagePlaceholder: '問題の詳細や改善提案を詳しくお書きください...',
      feedbackSubmit: 'レポート送信',
      feedbackSubmitting: '送信中...',
      feedbackSuccess: 'レポート送信完了',
      feedbackSuccessMessage: 'ご報告ありがとうございます！できるだけ早くご意見を処理いたします。',
      feedbackError: '送信失敗',
      feedbackErrorMessage: '送信中にエラーが発生しました。しばらくしてから再度お試しください。',
      feedbackRequired: 'この項目は必須です',
      enableGpuAcceleration: 'GPU加速を有効化',
      gpuAccelerationDesc: 'GPU加速処理を使用します。CUDA対応のNVIDIA GPUが必要です。GPUが利用できない場合、システムは自動的にCPUモードに切り替わります。',
      submitAnotherReport: '別のレポートを送信',
      retrySubmission: '再試行',
      
      // エラーハンドリングパネル
      errorSeverity: {
        critical: '重大エラー',
        high: '重要エラー',
        medium: '警告',
        low: '情報',
        default: '一般エラー'
      }
    },
    models: {
      tiny: {
        name: 'Tiny',
        description: '最速、精度は低い'
      },
      base: {
        name: 'Base',
        description: '速度と精度のバランス'
      },
      small: {
        name: 'Small',
        description: '高精度、適度な速度'
      },
      medium: {
        name: 'Medium',
        description: '高精度、推奨'
      },
      large: {
        name: 'Large',
        description: '最高精度、低速'
      }
    },
    languages: {
      auto: '自動検出',
      same: '元の言語と同じ',
      zh: '中国語',
      'zh-TW': '繁體中文',
      'zh-CN': '簡體中文',
      en: '英語',
      ja: '日本語',
      ko: '韓国語',
      es: 'スペイン語',
      fr: 'フランス語',
      de: 'ドイツ語',
      it: 'イタリア語',
      pt: 'ポルトガル語',
      ru: 'ロシア語',
      ar: 'アラビア語'
    },
    formats: {
      srt: {
        name: 'SRT',
        description: '最も一般的な字幕形式'
      },
      vtt: {
        name: 'WebVTT',
        description: 'ウェブ字幕形式'
      },
      txt: {
        name: 'TXT',
        description: 'プレーンテキスト形式'
      }
    },
    progress: {
      processing: '字幕を処理中',
      completed: '処理完了',
      error: '処理失敗',
      paused: '処理一時停止',
      processingDesc: '処理中',
      completedDesc: 'すべてのファイルが正常に処理されました',
      errorDesc: '処理中にエラーが発生しました',
      pausedDesc: '処理が一時停止されました。再開ボタンをクリックして続行',
      estimatedTime: '残り時間',
      overallProgress: '全体の進行状況',
      currentFile: '現在のファイル',
      filesCompleted: '完了',
      filesRemaining: '残り',
      filesTotal: '合計',
      keepOpen: 'プログラムを開いたままにしてください。処理時間はファイルサイズとモデル選択により異なります',
      allCompleted: 'すべての字幕ファイルが正常に生成され保存されました',
      errorOccurred: '処理中にエラーが発生しました。ファイルと設定を確認してください'
    },
    toast: {
      success: '成功',
      error: 'エラー',
      warning: '警告',
      info: '情報',
      selectFiles: '処理するファイルを選択してください',
      processingFailed: '処理に失敗しました: '
    }
  },
  'ko': {
    // 한국어
    app: {
      title: 'SRT GO',
      subtitle: 'AI 자막 생성 도구',
      startProcessing: '자막 생성',
      pauseProcessing: '처리 일시중지',
      resumeProcessing: '처리 재개',
      processing: '처리 중...',
      paused: '일시중지됨'
    },
    tabs: {
      files: '파일 선택',
      corrections: '텍스트 수정',
      settings: '설정'
    },
    fileSelection: {
      title: '파일 선택',
      subtitle: '자막을 생성할 오디오 또는 비디오 파일을 선택하세요. 드래그 앤 드롭 지원',
      dropzone: '여기에 파일을 드래그하거나 클릭하여 선택',
      dropzoneActive: '파일을 놓아 업로드',
      supportedFormats: 'MP4, MP3, WAV, AVI, MOV, MKV, M4A, FLAC, OGG 형식 지원',
      selectedFiles: '선택된 파일',
      noFiles: '선택된 파일이 없습니다',
      startUpload: '오디오 또는 비디오 파일 업로드 시작',
      removeFile: '파일 제거',
      unknownSize: '크기 알 수 없음',
      filesSelected: '선택된 파일',
      totalSize: '총 크기'
    },
    corrections: {
      title: '사용자 정의 텍스트 수정',
      subtitle: '일반적인 음성 인식 오류 수정 규칙을 설정하여 자막 품질 향상',
      addRule: '수정 규칙 추가',
      originalText: '원본 텍스트',
      replacementText: '대체 텍스트',
      replaceHint: '대체할 텍스트 (빈칸은 삭제)',
      enable: '이 규칙 활성화',
      save: '저장',
      cancel: '취소',
      add: '추가',
      edit: '편집',
      delete: '삭제',
      noRules: '설정된 수정 규칙이 없습니다',
      addRulesHint: '일반적인 음성 인식 오류를 자동으로 수정하는 규칙 추가',
      ruleCount: '수정 규칙',
      suggestions: '제안 규칙',
      suggestionsHint: '아래 제안을 클릭하여 일반적인 수정 규칙을 빠르게 추가',
      empty: '(비어있음)',
      remove: '(삭제)'
    },
    settings: {
      title: '설정',
      subtitle: 'AI 모델, 언어 및 출력 설정을 조정하여 자막 생성 최적화',
      aiModel: 'AI 모델',
      modelDescription: '처리 속도와 정확도의 균형을 맞추는 모델 선택',
      language: '언어',
      languageDescription: '오디오 언어를 지정하여 인식 정확도 향상',
      outputLanguage: '출력 언어',
      outputLanguageDescription: '자막 번역, 또는 원본 언어와 동일하게 유지',
      
      // 동적 언어 선택 라벨
      audioLanguage: '오디오 언어',
      audioLanguageDesc: '오디오 언어를 지정하여 인식 정확도 향상',
      outputOptions: '출력 옵션',
      autoDetectOutput: '출력 옵션',
      autoDetectDesc: '오디오 언어 자동 감지 후 출력 선택',
      keepOriginal: '원본 유지',
      translateToEnglish: '영어로 번역',
      
      outputFormat: '출력 형식',
      formatDescription: '자막 파일 출력 형식 선택',
      outputFolder: '출력 폴더',
      folderDescription: '자막 파일 저장 위치 선택. 비워두면 원본 파일과 같은 위치에 저장',
      useDefault: '기본 위치 사용 (원본 파일과 같은 폴더)',
      select: '선택',
      advanced: '고급 옵션',
      enableCorrections: '사용자 정의 텍스트 수정 활성화',
      correctionsDescription: '설정한 수정 규칙을 사용하여 자막 텍스트 최적화',
      interfaceLanguage: '인터페이스 언어',
      interfaceLanguageDescription: '애플리케이션 표시 언어 선택',
      tip: '팁',
      modelDownloadTip: '선택한 모델을 처음 사용할 때 시스템이 자동으로 모델 파일을 다운로드합니다. 이는 시간이 걸릴 수 있습니다. 다운로드 완료 후에는 더 빨라집니다.',
      
      // 피드백 및 버그 리포트
      feedback: '피드백 및 버그 리포트',
      feedbackSubtitle: '문제점이나 개선 제안을 신고하여 제품 개선에 도움을 주세요',
      feedbackTitle: '제목',
      feedbackTitlePlaceholder: '문제나 제안 사항을 간단히 설명해 주세요',
      feedbackName: '호칭',
      feedbackNamePlaceholder: '이름 또는 닉네임',
      feedbackEmail: '연락처 이메일',
      feedbackEmailPlaceholder: '이메일 주소',
      feedbackMessage: '상세 내용',
      feedbackMessagePlaceholder: '문제의 세부사항이나 개선 제안을 자세히 작성해 주세요...',
      feedbackSubmit: '리포트 제출',
      feedbackSubmitting: '제출 중...',
      feedbackSuccess: '리포트 제출 완료',
      feedbackSuccessMessage: '피드백을 주셔서 감사합니다! 가능한 한 빨리 의견을 처리하겠습니다.',
      feedbackError: '제출 실패',
      feedbackErrorMessage: '제출 중 오류가 발생했습니다. 나중에 다시 시도해 주세요.',
      feedbackRequired: '이 필드는 필수입니다',
      enableGpuAcceleration: 'GPU 가속 활성화',
      gpuAccelerationDesc: 'GPU 가속 처리를 사용합니다. CUDA 호환 NVIDIA GPU가 필요합니다. GPU를 사용할 수 없는 경우 시스템이 자동으로 CPU 모드로 전환됩니다.',
      submitAnotherReport: '다른 리포트 제출',
      retrySubmission: '다시 시도',
      
      // 오류 처리 패널
      errorSeverity: {
        critical: '심각한 오류',
        high: '중요 오류',
        medium: '경고',
        low: '정보',
        default: '일반 오류'
      }
    },
    models: {
      tiny: {
        name: 'Tiny',
        description: '가장 빠른 속도, 낮은 정확도'
      },
      base: {
        name: 'Base',
        description: '속도와 정확도의 균형'
      },
      small: {
        name: 'Small',
        description: '더 나은 정확도, 적당한 속도'
      },
      medium: {
        name: 'Medium',
        description: '높은 정확도, 권장'
      },
      large: {
        name: 'Large',
        description: '최고 정확도, 느린 속도'
      }
    },
    languages: {
      auto: '자동 감지',
      same: '원본과 동일',
      zh: '중국어',
      'zh-TW': '번체중국어',
      'zh-CN': '간체중국어',
      en: '영어',
      ja: '일본어',
      ko: '한국어',
      es: '스페인어',
      fr: '프랑스어',
      de: '독일어',
      it: '이탈리아어',
      pt: '포르투갈어',
      ru: '러시아어',
      ar: '아랍어'
    },
    formats: {
      srt: {
        name: 'SRT',
        description: '가장 일반적인 자막 형식'
      },
      vtt: {
        name: 'WebVTT',
        description: '웹 자막 형식'
      },
      txt: {
        name: 'TXT',
        description: '일반 텍스트 형식'
      }
    },
    progress: {
      processing: '자막 처리 중',
      completed: '처리 완료',
      error: '처리 실패',
      paused: '처리 일시중지',
      processingDesc: '처리 중',
      completedDesc: '모든 파일이 성공적으로 처리되었습니다',
      errorDesc: '처리 중 오류가 발생했습니다',
      pausedDesc: '처리가 일시중지되었습니다. 재개 버튼을 클릭하여 계속하세요',
      estimatedTime: '남은 시간',
      overallProgress: '전체 진행률',
      currentFile: '현재 파일',
      filesCompleted: '완료',
      filesRemaining: '남음',
      filesTotal: '전체',
      keepOpen: '프로그램을 열어두세요. 처리 시간은 파일 크기와 모델 선택에 따라 다릅니다',
      allCompleted: '모든 자막 파일이 성공적으로 생성되고 저장되었습니다',
      errorOccurred: '처리 중 오류가 발생했습니다. 파일과 설정을 확인하세요'
    },
    toast: {
      success: '성공',
      error: '오류',
      warning: '경고',
      info: '정보',
      selectFiles: '처리할 파일을 선택하세요',
      processingFailed: '처리 실패: '
    }
  }
}

// 獲取瀏覽器語言並設置英文為備用預設
export const getBrowserLanguage = () => {
  const lang = navigator.language || navigator.userLanguage
  
  // 映射瀏覽器語言到支援的語言
  if (lang.startsWith('zh')) {
    if (lang.includes('TW') || lang.includes('HK') || lang.includes('MO')) {
      return 'zh-TW'
    }
    return 'zh-CN'
  } else if (lang.startsWith('ja')) {
    return 'ja'
  } else if (lang.startsWith('ko')) {
    return 'ko'
  }
  
  // 預設英文（對於其他語言或無法識別的情況）
  return 'en'
}

// 翻譯函數
export const t = (key, locale) => {
  const keys = key.split('.')
  let value = translations[locale] || translations['en']
  
  for (const k of keys) {
    value = value?.[k]
  }
  
  return value || key
}