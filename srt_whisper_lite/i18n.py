#!/usr/bin/env python3
"""
國際化支援模組
支援多語言界面
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class I18nManager:
    """國際化管理器"""
    
    def __init__(self):
        self.current_language = "zh-TW"
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """載入翻譯文件"""
        # 內建翻譯數據
        self.translations = {
            "zh-TW": {
                # 主界面
                "app_title": "SRT GO",
                "subtitle_description": "基於 AI 的高效語音轉文字工具",
                "file_selection": "文件選擇",
                "no_files_selected": "沒有選擇檔案",
                "drag_drop_hint": "拖曳檔案到此處或點擊瀏覽（支援多個檔案）",
                "browse_files": "瀏覽文件",
                "selected_files": "已選擇 {} 個檔案（總計 {:.1f} MB）",
                "single_file_selected": "檔案：{} ({:.1f} MB)",
                
                # 設置
                "output_settings": "輸出設置",
                "model_speed": "處理速度",
                "fast": "快速",
                "medium": "中等", 
                "accurate": "精確",
                "language": "語言",
                "auto_detect": "自動檢測",
                "chinese_traditional": "中文(繁)",
                "chinese_simplified": "中文(簡)",
                "english": "英文",
                "japanese": "日文",
                "korean": "韓文",
                "output_format": "輸出格式",
                "output_directory": "輸出目錄",
                "same_as_source": "與原文件相同位置",
                "choose_directory": "選擇目錄",
                "choose_output_directory": "選擇字幕輸出目錄",
                "select_audio_video_files": "選擇音頻或視頻檔案",
                "custom_directory": "自定義目錄",
                "browse": "瀏覽",
                "processing_progress": "處理進度",
                "waiting_to_start": "等待開始...",
                "correction_description": "設置字幕中需要替換的詞彙",
                
                # 自定義修正
                "custom_corrections": "自定義修正規則",
                "corrections_description": "設置字幕中需要替換的詞彙",
                "wrong_word": "錯誤詞彙:",
                "correct_word": "正確詞彙:",
                "add_rule": "添加規則",
                "delete_selected": "刪除選中",
                "rule_added": "已添加修正規則：{} → {}",
                "confirm_delete": "確定要刪除規則「{}」嗎？",
                "rule_deleted": "規則已刪除",
                
                # 操作按鈕
                "start_processing": "開始生成字幕",
                "stop_processing": "停止處理",
                "processing": "處理中...",
                
                # 進度消息
                "loading_model": "正在載入 AI 模型...",
                "model_loaded": "AI 模型載入完成",
                "processing_audio": "開始處理音頻文件...",
                "language_detected": "識別語言: {}, 處理中...",
                "processing_segments": "處理段落 {}...",
                "semantic_optimization": "獲得 {} 個字幕段落，正在優化語意斷句...",
                "semantic_complete": "語意優化完成，共 {} 個段落",
                "post_processing": "智能後處理優化中...",
                "saving_subtitle": "正在保存字幕文件...",
                "generation_complete": "字幕生成完成！",
                "stopping_process": "正在停止處理...",
                "process_stopped": "處理已停止，已完成 {} 個文件",
                
                # 錯誤消息
                "please_select_files": "請先選擇檔案",
                "confirm_stop": "確定要停止當前處理嗎？\\n已處理的文件將保留。",
                "input_complete_words": "請輸入完整的錯誤詞彙和正確詞彙",
                "words_cannot_same": "錯誤詞彙和正確詞彙不能相同",
                "select_rule_to_delete": "請先選擇要刪除的規則",
                
                # 結果消息
                "all_files_completed": "所有 {} 個文件處理完成！",
                "partial_success": "處理完成\\n\\n成功: {} 個\\n失敗: {} 個\\n\\n失敗文件:\\n{}",
                "all_files_failed": "所有 {} 個文件處理失敗",
                
                # 界面語言
                "interface_language": "界面語言",
                
                # 新增錯誤和狀態消息
                "error": "錯誤",
                "warning": "警告",
                "success": "成功",
                "completed": "完成",
                "stopped": "已停止",
                "confirm": "確認",
                "interface_rebuild_failed": "界面重建失敗",
                "please_select_files_first": "請先選擇檔案",
                "processing_stopped_and_reset": "處理已停止並回到初始狀態",
                "subtitle_generation_success": "字幕生成成功！",
                "file_location": "檔案位置",
                "processing_failed": "處理失敗",
                "wrong_word": "錯誤詞彙",
                "please_enter_complete_correction": "請輸入完整的錯誤詞彙和正確詞彙",
                "wrong_and_correct_cannot_be_same": "錯誤詞彙和正確詞彙不能相同",
                "correction_rule_added": "已添加修正規則",
                "add_failed": "添加失敗",
                "please_select_rule_to_delete": "請先選擇要刪除的規則",
                "confirm_delete_rule": "確定要刪除規則嗎",
                "rule_deleted": "規則已刪除",
                "delete_failed": "刪除失敗",
                "app_start_failed": "應用程式啟動失敗"
            },
            
            "zh-CN": {
                # 主界面
                "app_title": "SRT GO",
                "subtitle_description": "基于 AI 的高效语音转文字工具",
                "file_selection": "文件选择",
                "no_files_selected": "没有选择文件",
                "drag_drop_hint": "拖拽文件到此处或点击浏览（支持多个文件）",
                "browse_files": "浏览文件",
                "selected_files": "已选择 {} 个文件（总计 {:.1f} MB）",
                "single_file_selected": "文件：{} ({:.1f} MB)",
                
                # 设置
                "output_settings": "输出设置",
                "model_speed": "处理速度",
                "fast": "快速",
                "medium": "中等",
                "accurate": "精确",
                "language": "语言",
                "auto_detect": "自动检测",
                "chinese_traditional": "中文(繁)",
                "chinese_simplified": "中文(简)",
                "english": "英文",
                "japanese": "日文",
                "korean": "韩文",
                "output_format": "输出格式",
                "output_directory": "输出目录",
                "same_as_source": "与原文件相同位置",
                "custom_directory": "自定义目录",
                "browse": "浏览",
                "processing_progress": "处理进度",
                "waiting_to_start": "等待开始...",
                "correction_description": "设置字幕中需要替换的词汇",
                "choose_output_directory": "选择字幕输出目录",
                "select_audio_video_files": "选择音频或视频文件",
                
                # 自定义修正
                "custom_corrections": "自定义修正规则",
                "corrections_description": "设置字幕中需要替换的词汇",
                "wrong_word": "错误词汇:",
                "correct_word": "正确词汇:",
                "add_rule": "添加规则",
                "delete_selected": "删除选中",
                "rule_added": "已添加修正规则：{} → {}",
                "confirm_delete": "确定要删除规则「{}」吗？",
                "rule_deleted": "规则已删除",
                
                # 操作按钮
                "start_processing": "开始生成字幕",
                "stop_processing": "停止处理",
                "processing": "处理中...",
                
                # 进度消息
                "loading_model": "正在载入 AI 模型...",
                "model_loaded": "AI 模型载入完成",
                "processing_audio": "开始处理音频文件...",
                "language_detected": "识别语言: {}, 处理中...",
                "processing_segments": "处理段落 {}...",
                "semantic_optimization": "获得 {} 个字幕段落，正在优化语意断句...",
                "semantic_complete": "语意优化完成，共 {} 个段落",
                "post_processing": "智能后处理优化中...",
                "saving_subtitle": "正在保存字幕文件...",
                "generation_complete": "字幕生成完成！",
                "stopping_process": "正在停止处理...",
                "process_stopped": "处理已停止，已完成 {} 个文件",
                
                # 错误消息
                "please_select_files": "请先选择文件",
                "confirm_stop": "确定要停止当前处理吗？\\n已处理的文件将保留。",
                "input_complete_words": "请输入完整的错误词汇和正确词汇",
                "words_cannot_same": "错误词汇和正确词汇不能相同",
                "select_rule_to_delete": "请先选择要删除的规则",
                
                # 结果消息
                "all_files_completed": "所有 {} 个文件处理完成！",
                "partial_success": "处理完成\\n\\n成功: {} 个\\n失败: {} 个\\n\\n失败文件:\\n{}",
                "all_files_failed": "所有 {} 个文件处理失败",
                
                # 界面语言
                "interface_language": "界面语言",
                
                # 新增错误和状态消息
                "error": "错误",
                "warning": "警告",
                "success": "成功",
                "completed": "完成",
                "stopped": "已停止",
                "confirm": "确认",
                "interface_rebuild_failed": "界面重建失败",
                "please_select_files_first": "请先选择文件",
                "processing_stopped_and_reset": "处理已停止并回到初始状态",
                "subtitle_generation_success": "字幕生成成功！",
                "file_location": "文件位置",
                "processing_failed": "处理失败",
                "wrong_word": "错误词汇",
                "please_enter_complete_correction": "请输入完整的错误词汇和正确词汇",
                "wrong_and_correct_cannot_be_same": "错误词汇和正确词汇不能相同",
                "correction_rule_added": "已添加修正规则",
                "add_failed": "添加失败",
                "please_select_rule_to_delete": "请先选择要删除的规则",
                "confirm_delete_rule": "确定要删除规则吗",
                "rule_deleted": "规则已删除",
                "delete_failed": "删除失败",
                "app_start_failed": "应用程序启动失败"
            },
            
            "en": {
                # Main interface
                "app_title": "SRT GO",
                "subtitle_description": "Efficient AI-powered speech-to-text tool",
                "file_selection": "File Selection",
                "no_files_selected": "No files selected",
                "drag_drop_hint": "Drag files here or click browse (multiple files supported)",
                "browse_files": "Browse Files",
                "selected_files": "{} files selected (Total: {:.1f} MB)",
                "single_file_selected": "File: {} ({:.1f} MB)",
                
                # Settings
                "output_settings": "Output Settings",
                "model_speed": "Processing Speed",
                "fast": "Fast",
                "medium": "Medium",
                "accurate": "Accurate",
                "language": "Language",
                "auto_detect": "Auto Detect",
                "chinese_traditional": "Chinese (Traditional)",
                "chinese_simplified": "Chinese (Simplified)",
                "english": "English",
                "japanese": "Japanese",
                "korean": "Korean",
                "output_format": "Output Format",
                "output_directory": "Output Directory",
                "same_as_source": "Same as source file",
                "custom_directory": "Custom Directory",
                "browse": "Browse",
                "processing_progress": "Processing Progress",
                "waiting_to_start": "Waiting to start...",
                "correction_description": "Set words to replace in subtitles",
                "choose_output_directory": "Choose subtitle output directory",
                "select_audio_video_files": "Select audio or video files",
                
                # Custom corrections
                "custom_corrections": "Custom Correction Rules",
                "corrections_description": "Set words to replace in subtitles",
                "wrong_word": "Wrong Word:",
                "correct_word": "Correct Word:",
                "add_rule": "Add Rule",
                "delete_selected": "Delete Selected",
                "rule_added": "Correction rule added: {} → {}",
                "confirm_delete": "Delete rule \"{}\"?",
                "rule_deleted": "Rule deleted",
                
                # Action buttons
                "start_processing": "Start Generation",
                "stop_processing": "Stop Processing",
                "processing": "Processing...",
                
                # Progress messages
                "loading_model": "Loading AI model...",
                "model_loaded": "AI model loaded",
                "processing_audio": "Processing audio file...",
                "language_detected": "Language detected: {}, processing...",
                "processing_segments": "Processing segment {}...",
                "semantic_optimization": "Got {} subtitle segments, optimizing semantic segmentation...",
                "semantic_complete": "Semantic optimization complete, {} segments total",
                "post_processing": "Smart post-processing...",
                "saving_subtitle": "Saving subtitle file...",
                "generation_complete": "Subtitle generation complete!",
                "stopping_process": "Stopping process...",
                "process_stopped": "Process stopped, {} files completed",
                
                # Error messages
                "please_select_files": "Please select files first",
                "confirm_stop": "Stop current processing?\\nProcessed files will be kept.",
                "input_complete_words": "Please enter both wrong and correct words",
                "words_cannot_same": "Wrong and correct words cannot be the same",
                "select_rule_to_delete": "Please select a rule to delete",
                
                # Result messages
                "all_files_completed": "All {} files completed!",
                "partial_success": "Processing complete\\n\\nSuccess: {} files\\nFailed: {} files\\n\\nFailed files:\\n{}",
                "all_files_failed": "All {} files failed",
                
                # Interface language
                "interface_language": "Interface Language",
                
                # New error and status messages
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "completed": "Completed",
                "stopped": "Stopped",
                "confirm": "Confirm",
                "interface_rebuild_failed": "Interface rebuild failed",
                "please_select_files_first": "Please select files first",
                "processing_stopped_and_reset": "Processing stopped and reset to initial state",
                "subtitle_generation_success": "Subtitle generation successful!",
                "file_location": "File location",
                "processing_failed": "Processing failed",
                "wrong_word": "Wrong word",
                "please_enter_complete_correction": "Please enter complete wrong and correct words",
                "wrong_and_correct_cannot_be_same": "Wrong and correct words cannot be the same",
                "correction_rule_added": "Correction rule added",
                "add_failed": "Add failed",
                "please_select_rule_to_delete": "Please select a rule to delete first",
                "confirm_delete_rule": "Confirm to delete rule",
                "rule_deleted": "Rule deleted",
                "delete_failed": "Delete failed",
                "app_start_failed": "Application startup failed"
            },
            
            "ja": {
                # メインインターフェース
                "app_title": "SRT GO",
                "subtitle_description": "AIベースの高効率音声テキスト変換ツール",
                "file_selection": "ファイル選択",
                "no_files_selected": "ファイルが選択されていません",
                "drag_drop_hint": "ファイルをここにドラッグするかブラウズをクリック（複数ファイル対応）",
                "browse_files": "ファイルを参照",
                "selected_files": "{}個のファイルを選択（合計：{:.1f} MB）",
                "single_file_selected": "ファイル：{} ({:.1f} MB)",
                
                # 設定
                "output_settings": "出力設定",
                "model_speed": "処理速度",
                "fast": "高速",
                "medium": "中程度",
                "accurate": "精密",
                "language": "言語",
                "auto_detect": "自動検出",
                "chinese_traditional": "中国語（繁体字）",
                "chinese_simplified": "中国語（簡体字）",
                "english": "英語",
                "japanese": "日本語",
                "korean": "韓国語",
                "output_format": "出力形式",
                "output_directory": "出力ディレクトリ",
                "same_as_source": "元ファイルと同じ場所",
                "custom_directory": "カスタムディレクトリ",
                "browse": "参照",
                "processing_progress": "処理進度",
                "waiting_to_start": "開始待機中...",
                "correction_description": "字幕で置換する単語を設定",
                "choose_output_directory": "字幕出力ディレクトリ選択",
                "select_audio_video_files": "音声またはビデオファイル選択",
                
                # カスタム修正
                "custom_corrections": "カスタム修正ルール",
                "corrections_description": "字幕で置き換える単語を設定",
                "wrong_word": "間違った単語：",
                "correct_word": "正しい単語：",
                "add_rule": "ルールを追加",
                "delete_selected": "選択を削除",
                "rule_added": "修正ルールを追加：{} → {}",
                "confirm_delete": "ルール「{}」を削除しますか？",
                "rule_deleted": "ルールを削除しました",
                
                # アクションボタン
                "start_processing": "生成開始",
                "stop_processing": "処理停止",
                "processing": "処理中...",
                
                # 進行メッセージ
                "loading_model": "AIモデルを読み込み中...",
                "model_loaded": "AIモデルの読み込み完了",
                "processing_audio": "音声ファイルを処理中...",
                "language_detected": "言語検出：{}、処理中...",
                "processing_segments": "セグメント{}を処理中...",
                "semantic_optimization": "{}個の字幕セグメントを取得、意味分割を最適化中...",
                "semantic_complete": "意味最適化完了、合計{}セグメント",
                "post_processing": "スマート後処理中...",
                "saving_subtitle": "字幕ファイルを保存中...",
                "generation_complete": "字幕生成完了！",
                "stopping_process": "処理を停止中...",
                "process_stopped": "処理が停止されました、{}ファイル完了",
                
                # エラーメッセージ
                "please_select_files": "まずファイルを選択してください",
                "confirm_stop": "現在の処理を停止しますか？\\n処理済みファイルは保持されます。",
                "input_complete_words": "間違った単語と正しい単語の両方を入力してください",
                "words_cannot_same": "間違った単語と正しい単語は同じにできません",
                "select_rule_to_delete": "削除するルールを選択してください",
                
                # 結果メッセージ
                "all_files_completed": "全{}ファイル完了！",
                "partial_success": "処理完了\\n\\n成功：{}ファイル\\n失敗：{}ファイル\\n\\n失敗ファイル：\\n{}",
                "all_files_failed": "全{}ファイル失敗",
                
                # インターフェース言語
                "interface_language": "インターフェース言語",
                
                # 新しいエラーとステータスメッセージ
                "error": "エラー",
                "warning": "警告",
                "success": "成功",
                "completed": "完了",
                "stopped": "停止済み",
                "confirm": "確認",
                "interface_rebuild_failed": "インターフェース再構築失敗",
                "please_select_files_first": "まずファイルを選択してください",
                "processing_stopped_and_reset": "処理が停止され、初期状態に戻りました",
                "subtitle_generation_success": "字幕生成成功！",
                "file_location": "ファイル場所",
                "processing_failed": "処理失敗",
                "wrong_word": "間違った単語",
                "please_enter_complete_correction": "間違った単語と正しい単語を完全に入力してください",
                "wrong_and_correct_cannot_be_same": "間違った単語と正しい単語は同じにできません",
                "correction_rule_added": "修正ルール追加済み",
                "add_failed": "追加失敗",
                "please_select_rule_to_delete": "まず削除するルールを選択してください",
                "confirm_delete_rule": "ルールの削除を確認",
                "rule_deleted": "ルール削除済み",
                "delete_failed": "削除失敗",
                "app_start_failed": "アプリケーション起動失敗"
            },
            
            "ko": {
                # 메인 인터페이스
                "app_title": "SRT GO",
                "subtitle_description": "AI 기반 고효율 음성-텍스트 변환 도구",
                "file_selection": "파일 선택",
                "no_files_selected": "선택된 파일이 없습니다",
                "drag_drop_hint": "파일을 여기에 드래그하거나 찾아보기 클릭 (다중 파일 지원)",
                "browse_files": "파일 찾아보기",
                "selected_files": "{}개 파일 선택됨 (총 {:.1f} MB)",
                "single_file_selected": "파일: {} ({:.1f} MB)",
                
                # 설정
                "output_settings": "출력 설정",
                "model_speed": "처리 속도",
                "fast": "빠름",
                "medium": "보통",
                "accurate": "정확",
                "language": "언어",
                "auto_detect": "자동 감지",
                "chinese_traditional": "중국어(번체)",
                "chinese_simplified": "중국어(간체)",
                "english": "영어",
                "japanese": "일본어",
                "korean": "한국어",
                "output_format": "출력 형식",
                "output_directory": "출력 디렉토리",
                "same_as_source": "원본 파일과 동일한 위치",
                "custom_directory": "사용자 정의 디렉토리",
                "browse": "찾아보기",
                "processing_progress": "처리 진행률",
                "waiting_to_start": "시작 대기 중...",
                "correction_description": "자막에서 교체할 단어 설정",
                "choose_output_directory": "자막 출력 디렉토리 선택",
                "select_audio_video_files": "오디오 또는 비디오 파일 선택",
                
                # 사용자 정의 수정
                "custom_corrections": "사용자 정의 수정 규칙",
                "corrections_description": "자막에서 교체할 단어 설정",
                "wrong_word": "잘못된 단어:",
                "correct_word": "올바른 단어:",
                "add_rule": "규칙 추가",
                "delete_selected": "선택 삭제",
                "rule_added": "수정 규칙 추가됨: {} → {}",
                "confirm_delete": "규칙 \"{}\"을(를) 삭제하시겠습니까?",
                "rule_deleted": "규칙이 삭제되었습니다",
                
                # 액션 버튼
                "start_processing": "생성 시작",
                "stop_processing": "처리 중지",
                "processing": "처리 중...",
                
                # 진행 메시지
                "loading_model": "AI 모델 로딩 중...",
                "model_loaded": "AI 모델 로딩 완료",
                "processing_audio": "오디오 파일 처리 중...",
                "language_detected": "언어 감지됨: {}, 처리 중...",
                "processing_segments": "세그먼트 {} 처리 중...",
                "semantic_optimization": "{}개 자막 세그먼트 획득, 의미 분할 최적화 중...",
                "semantic_complete": "의미 최적화 완료, 총 {}개 세그먼트",
                "post_processing": "스마트 후처리 중...",
                "saving_subtitle": "자막 파일 저장 중...",
                "generation_complete": "자막 생성 완료!",
                "stopping_process": "처리 중지 중...",
                "process_stopped": "처리가 중지됨, {}개 파일 완료",
                
                # 오류 메시지
                "please_select_files": "먼저 파일을 선택하세요",
                "confirm_stop": "현재 처리를 중지하시겠습니까?\\n처리된 파일은 유지됩니다.",
                "input_complete_words": "잘못된 단어와 올바른 단어를 모두 입력하세요",
                "words_cannot_same": "잘못된 단어와 올바른 단어는 같을 수 없습니다",
                "select_rule_to_delete": "삭제할 규칙을 선택하세요",
                
                # 결과 메시지
                "all_files_completed": "모든 {}개 파일 완료!",
                "partial_success": "처리 완료\\n\\n성공: {}개\\n실패: {}개\\n\\n실패 파일:\\n{}",
                "all_files_failed": "모든 {}개 파일 실패",
                
                # 인터페이스 언어
                "interface_language": "인터페이스 언어",
                
                # 새로운 오류 및 상태 메시지
                "error": "오류",
                "warning": "경고",
                "success": "성공",
                "completed": "완료",
                "stopped": "중지됨",
                "confirm": "확인",
                "interface_rebuild_failed": "인터페이스 재구축 실패",
                "please_select_files_first": "먼저 파일을 선택하세요",
                "processing_stopped_and_reset": "처리가 중지되고 초기 상태로 돌아갔습니다",
                "subtitle_generation_success": "자막 생성 성공!",
                "file_location": "파일 위치",
                "processing_failed": "처리 실패",
                "wrong_word": "잘못된 단어",
                "please_enter_complete_correction": "잘못된 단어와 올바른 단어를 완전히 입력하세요",
                "wrong_and_correct_cannot_be_same": "잘못된 단어와 올바른 단어는 같을 수 없습니다",
                "correction_rule_added": "수정 규칙 추가됨",
                "add_failed": "추가 실패",
                "please_select_rule_to_delete": "먼저 삭제할 규칙을 선택하세요",
                "confirm_delete_rule": "규칙 삭제 확인",
                "rule_deleted": "규칙 삭제됨",
                "delete_failed": "삭제 실패",
                "app_start_failed": "애플리케이션 시작 실패"
            }
        }
    
    def set_language(self, language_code: str):
        """設置當前語言"""
        if language_code in self.translations:
            self.current_language = language_code
            logger.info(f"語言切換到: {language_code}")
            return True
        else:
            logger.warning(f"不支援的語言代碼: {language_code}")
            return False
    
    def get_text(self, key: str, *args, **kwargs) -> str:
        """獲取翻譯文本"""
        try:
            text = self.translations[self.current_language].get(key, key)
            if args or kwargs:
                return text.format(*args, **kwargs)
            return text
        except Exception as e:
            logger.warning(f"翻譯失敗 {key}: {e}")
            return key
    
    def get_available_languages(self) -> Dict[str, str]:
        """獲取可用語言列表"""
        return {
            "zh-TW": "中文(繁體)",
            "zh-CN": "中文(简体)", 
            "en": "English",
            "ja": "日本語",
            "ko": "한국어"
        }

# 全局實例
_i18n_manager = None

def get_i18n() -> I18nManager:
    """獲取國際化管理器實例"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager

def _(key: str, *args, **kwargs) -> str:
    """翻譯快捷函數"""
    return get_i18n().get_text(key, *args, **kwargs)