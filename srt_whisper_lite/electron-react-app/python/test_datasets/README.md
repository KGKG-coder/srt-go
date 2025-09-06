# 綜合測試數據集

建立時間: 2025-08-25 18:30:00
總檔案數: 370 個

## 檔案分類

### SHORT (205 個檔案)
- 總時長: 262.4秒 (4.4分鐘)
- 總大小: 130.2MB
- 測試重點: latency_optimization
- 預期RTF範圍: 0.05-0.2
- 建議模式: auto, gpu, cpu

代表性檔案:
- C0485.MP4_temp.wav (0.4s, 4.29MB)
- DRLIN.mp4_temp.wav (0.1s, 1.23MB)
- hutest.mp4 (30.0s, 13.87MB)

### MEDIUM (65 個檔案)
- 總時長: 8603.2秒 (143.4分鐘)
- 總大小: 4011.6MB
- 測試重點: standard_performance
- 預期RTF範圍: 0.1-0.5
- 建議模式: auto, gpu

代表性檔案:
- DRLIN.mp4 (178.7s, 89.34MB)
- DRLIN.mp4 (178.7s, 89.34MB)
- C1317.MP4 (208.0s, 104.02MB)

### LONG (51 個檔案)
- 總時長: 41771.6秒 (696.2分鐘)
- 總大小: 21593.8MB
- 測試重點: memory_management
- 預期RTF範圍: 0.2-0.8
- 建議模式: gpu, cpu

代表性檔案:
- C0485.MP4 (576.1s, 288.05MB)
- 20250319 張育成2025中職球星-幕後花絮 包框_工作區域 1.mp4 (415.9s, 207.93MB)
- 240206_諾貝爾眼科＿兩位女兒手術訪談＿Bcopy.mp4 (1800.0s, 1607.96MB)

### VERY_LONG (31 個檔案)
- 總時長: 265682.8秒 (4428.0分鐘)
- 總大小: 132841.4MB
- 測試重點: stress_testing
- 預期RTF範圍: 0.5-1.5
- 建議模式: cpu

代表性檔案:
- C1317.MP4 (6464.8s, 3232.4MB)
- 240112_諾貝爾Ｘ大師兄手術紀錄＿Acopy.mp4 (4788.9s, 2394.47MB)
- 240123_諾貝爾眼科Ｘ大師兄_雷射手術紀錄 Final.mp4 (4794.1s, 2397.06MB)

### MULTILINGUAL (16 個檔案)
- 總時長: 244.9秒 (4.1分鐘)
- 總大小: 36.9MB
- 測試重點: specialized_scenarios
- 預期RTF範圍: 0.1-1.0
- 建議模式: auto

代表性檔案:
- Treatment_Animation_LASIK_EN_34_160_0032I.ogg (88.0s, 14.67MB)
- smart_robotics_centralign_animation_4x3.mp4 (1.7s, 0.86MB)
- smart_robotics_easy-patient-access_animation_4x3-1.mp4 (4.3s, 2.17MB)

### QUALITY_TESTS (1 個檔案)
- 總時長: 98.4秒 (1.6分鐘)
- 總大小: 49.2MB
- 測試重點: specialized_scenarios
- 預期RTF範圍: 0.1-1.0
- 建議模式: auto

代表性檔案:
- VM800 完整的workflow.mp4 (98.4s, 49.19MB)

### SPECIAL_CASES (1 個檔案)
- 總時長: 24.2秒 (0.4分鐘)
- 總大小: 12.1MB
- 測試重點: specialized_scenarios
- 預期RTF範圍: 0.1-1.0
- 建議模式: auto

代表性檔案:
- TV NoiseWB.mp4 (24.2s, 12.09MB)

## 測試計劃

### QUICK_VALIDATION
- 快速驗證所有性能模式
- 預估時間: 5-10分鐘
- 測試檔案: 2 個

### STANDARD_BENCHMARK
- 標準性能基準測試
- 預估時間: 15-30分鐘
- 測試檔案: 3 個

### COMPREHENSIVE_TEST
- 全面性能和穩定性測試
- 預估時間: 1-2小時
- 測試檔案: 6 個

### STRESS_TEST
- 壓力測試和極限情況
- 預估時間: 2-4小時
- 測試檔案: 82 個

## 推薦測試順序

1. **SMOKE_TEST** - 快速煙霧測試 - 驗證基本功能
   - 預估時間: 1-2分鐘
   - 測試檔案: 1 個
   - 性能模式: auto

2. **PERFORMANCE_MODES** - 性能模式驗證 - 測試所有模式
   - 預估時間: 5-10分鐘
   - 測試檔案: 1 個
   - 性能模式: auto, gpu, cpu

3. **DURATION_RANGE** - 時長範圍測試 - 不同時長檔案
   - 預估時間: 10-20分鐘
   - 測試檔案: 3 個
   - 性能模式: auto

4. **QUALITY_SPECIAL** - 品質和特殊情況測試
   - 預估時間: 5-15分鐘
   - 測試檔案: 2 個
   - 性能模式: auto

5. **MULTILINGUAL** - 多語言支援測試
   - 預估時間: 10-30分鐘
   - 測試檔案: 3 個
   - 性能模式: auto

## 使用方法

### 執行快速驗證測試
```bash
python run_quick_validation_test.py
```

### 執行標準基準測試
```bash
python run_standard_benchmark_test.py
```

### 執行全面性能測試
```bash
python run_comprehensive_test_test.py
```

### 執行壓力測試
```bash
python run_stress_test_test.py
```

## 結果分析

測試結果將保存為JSON格式，包含：
- 處理時間和RTF值
- 性能等級分類
- 成功/失敗狀態
- 詳細的錯誤信息（如有）

結果檔案位置：
- quick_validation_results.json
- standard_benchmark_results.json
- comprehensive_test_results.json
- stress_test_results.json
