#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動生成的性能測試腳本: stress_test
壓力測試和極限情況
預估執行時間: 2-4小時
"""

import sys
import os
import time
import subprocess
import json
from pathlib import Path

# 添加父目錄到路徑以便導入
sys.path.append(str(Path(__file__).parent.parent))

def run_performance_test():
    """執行性能測試"""
    print("=== stress_test 性能測試 ===")
    print("描述: 壓力測試和極限情況")
    print("預估時間: 2-4小時")
    print()
    
    test_files = [
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\SRTGO\\srt_whisper_lite\\electron-react-app\\test_VIDEO\\C0485.MP4",
        "name": "C0485.MP4",
        "size": 302037223,
        "size_mb": 288.05,
        "estimated_duration": 576.0902843475342,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\20250319 張育成2025中職球星-幕後花絮 包框_工作區域 1.mp4",
        "name": "20250319 張育成2025中職球星-幕後花絮 包框_工作區域 1.mp4",
        "size": 218025783,
        "size_mb": 207.93,
        "estimated_duration": 415.8511791229248,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\240206_諾貝爾眼科＿兩位女兒手術訪談＿Bcopy.mp4",
        "name": "240206_諾貝爾眼科＿兩位女兒手術訪談＿Bcopy.mp4",
        "size": 1686067393,
        "size_mb": 1607.96,
        "estimated_duration": 1800,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\【近視與老花雷射手術】專訪 張朝凱｜趙少康時間 2024.02.05 (1080p).mp4",
        "name": "【近視與老花雷射手術】專訪 張朝凱｜趙少康時間 2024.02.05 (1080p).mp4",
        "size": 446455687,
        "size_mb": 425.77,
        "estimated_duration": 851.5466442108154,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\連祐暘醫師\\C0047.MP4",
        "name": "C0047.MP4",
        "size": 679579134,
        "size_mb": 648.1,
        "estimated_duration": 1296.1943321228027,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\連祐暘醫師\\C0048.MP4",
        "name": "C0048.MP4",
        "size": 276868354,
        "size_mb": 264.04,
        "estimated_duration": 528.0844764709473,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\連祐暘醫師\\C0412.MP4",
        "name": "C0412.MP4",
        "size": 906179667,
        "size_mb": 864.2,
        "estimated_duration": 1728.4005489349365,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\醫管\\SILK\\PP2023RF4074_SILK 患者形象影片 中文字幕.mp4",
        "name": "PP2023RF4074_SILK 患者形象影片 中文字幕.mp4",
        "size": 269399232,
        "size_mb": 256.92,
        "estimated_duration": 513.8382568359375,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0109.MP4",
        "name": "C0109.MP4",
        "size": 503492675,
        "size_mb": 480.17,
        "estimated_duration": 960.3360652923584,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0111.MP4",
        "name": "C0111.MP4",
        "size": 469935303,
        "size_mb": 448.17,
        "estimated_duration": 896.3304576873779,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0112.MP4",
        "name": "C0112.MP4",
        "size": 335706991,
        "size_mb": 320.16,
        "estimated_duration": 640.3102703094482,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0113.MP4",
        "name": "C0113.MP4",
        "size": 335706695,
        "size_mb": 320.15,
        "estimated_duration": 640.3097057342529,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0114.MP4",
        "name": "C0114.MP4",
        "size": 771949591,
        "size_mb": 736.19,
        "estimated_duration": 1472.3769969940186,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0115.MP4",
        "name": "C0115.MP4",
        "size": 738393983,
        "size_mb": 704.19,
        "estimated_duration": 1408.3747539520264,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0116.MP4",
        "name": "C0116.MP4",
        "size": 167918955,
        "size_mb": 160.14,
        "estimated_duration": 320.2799892425537,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0120.MP4",
        "name": "C0120.MP4",
        "size": 201476327,
        "size_mb": 192.14,
        "estimated_duration": 384.2855968475342,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0124.MP4",
        "name": "C0124.MP4",
        "size": 167919247,
        "size_mb": 160.14,
        "estimated_duration": 320.2805461883545,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0125.MP4",
        "name": "C0125.MP4",
        "size": 167920423,
        "size_mb": 160.14,
        "estimated_duration": 320.2827892303467,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0127.MP4",
        "name": "C0127.MP4",
        "size": 167920423,
        "size_mb": 160.14,
        "estimated_duration": 320.2827892303467,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0129.MP4",
        "name": "C0129.MP4",
        "size": 872621707,
        "size_mb": 832.2,
        "estimated_duration": 1664.39381980896,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0130.MP4",
        "name": "C0130.MP4",
        "size": 503490911,
        "size_mb": 480.17,
        "estimated_duration": 960.3327007293701,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0132.MP4",
        "name": "C0132.MP4",
        "size": 335705519,
        "size_mb": 320.15,
        "estimated_duration": 640.3074626922607,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0134.MP4",
        "name": "C0134.MP4",
        "size": 537049672,
        "size_mb": 512.17,
        "estimated_duration": 1024.3409576416016,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0138.MP4",
        "name": "C0138.MP4",
        "size": 201477716,
        "size_mb": 192.14,
        "estimated_duration": 384.28824615478516,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0139.MP4",
        "name": "C0139.MP4",
        "size": 906178708,
        "size_mb": 864.2,
        "estimated_duration": 1728.3987197875977,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0140.MP4",
        "name": "C0140.MP4",
        "size": 235033620,
        "size_mb": 224.15,
        "estimated_duration": 448.29105377197266,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0146.MP4",
        "name": "C0146.MP4",
        "size": 302147559,
        "size_mb": 288.15,
        "estimated_duration": 576.3007335662842,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1080.MP4",
        "name": "C1080.MP4",
        "size": 201477207,
        "size_mb": 192.14,
        "estimated_duration": 384.28727531433105,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1081.MP4",
        "name": "C1081.MP4",
        "size": 335705227,
        "size_mb": 320.15,
        "estimated_duration": 640.30690574646,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1082.MP4",
        "name": "C1082.MP4",
        "size": 335706148,
        "size_mb": 320.15,
        "estimated_duration": 640.3086624145508,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1083.MP4",
        "name": "C1083.MP4",
        "size": 201478383,
        "size_mb": 192.14,
        "estimated_duration": 384.28951835632324,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1084.MP4",
        "name": "C1084.MP4",
        "size": 939735904,
        "size_mb": 896.2,
        "estimated_duration": 1792.4039916992188,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1085.MP4",
        "name": "C1085.MP4",
        "size": 469934419,
        "size_mb": 448.16,
        "estimated_duration": 896.3287715911865,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1087.MP4",
        "name": "C1087.MP4",
        "size": 335704639,
        "size_mb": 320.15,
        "estimated_duration": 640.3057842254639,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1088.MP4",
        "name": "C1088.MP4",
        "size": 402821147,
        "size_mb": 384.16,
        "estimated_duration": 768.3203639984131,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1089.MP4",
        "name": "C1089.MP4",
        "size": 369262932,
        "size_mb": 352.16,
        "estimated_duration": 704.3131484985352,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1090.MP4",
        "name": "C1090.MP4",
        "size": 436376755,
        "size_mb": 416.16,
        "estimated_duration": 832.3226070404053,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1095.MP4",
        "name": "C1095.MP4",
        "size": 235033699,
        "size_mb": 224.15,
        "estimated_duration": 448.29120445251465,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1096.MP4",
        "name": "C1096.MP4",
        "size": 805506124,
        "size_mb": 768.19,
        "estimated_duration": 1536.381004333496,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1097.MP4",
        "name": "C1097.MP4",
        "size": 268592247,
        "size_mb": 256.15,
        "estimated_duration": 512.2990550994873,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1099.MP4",
        "name": "C1099.MP4",
        "size": 235033403,
        "size_mb": 224.15,
        "estimated_duration": 448.29063987731934,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1106.MP4",
        "name": "C1106.MP4",
        "size": 369263187,
        "size_mb": 352.16,
        "estimated_duration": 704.3136348724365,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1109.MP4",
        "name": "C1109.MP4",
        "size": 805505787,
        "size_mb": 768.19,
        "estimated_duration": 1536.3803615570068,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1110.MP4",
        "name": "C1110.MP4",
        "size": 201476248,
        "size_mb": 192.14,
        "estimated_duration": 384.2854461669922,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1111.MP4",
        "name": "C1111.MP4",
        "size": 704836023,
        "size_mb": 672.18,
        "estimated_duration": 1344.3680248260498,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1112.MP4",
        "name": "C1112.MP4",
        "size": 671276595,
        "size_mb": 640.18,
        "estimated_duration": 1280.3584957122803,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1114.MP4",
        "name": "C1114.MP4",
        "size": 469933580,
        "size_mb": 448.16,
        "estimated_duration": 896.3271713256836,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1115.MP4",
        "name": "C1115.MP4",
        "size": 268591951,
        "size_mb": 256.15,
        "estimated_duration": 512.298490524292,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1116.MP4",
        "name": "C1116.MP4",
        "size": 201478424,
        "size_mb": 192.14,
        "estimated_duration": 384.2895965576172,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1119.MP4",
        "name": "C1119.MP4",
        "size": 369263775,
        "size_mb": 352.16,
        "estimated_duration": 704.3147563934326,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\SRTGO\\srt_whisper_lite\\electron-react-app\\test_VIDEO\\C0485.MP4",
        "name": "C0485.MP4",
        "size": 302037223,
        "size_mb": 288.05,
        "estimated_duration": 576.0902843475342,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\C1317.MP4",
        "name": "C1317.MP4",
        "size": 3389413148,
        "size_mb": 3232.4,
        "estimated_duration": 6464.792533874512,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\240112_諾貝爾Ｘ大師兄手術紀錄＿Acopy.mp4",
        "name": "240112_諾貝爾Ｘ大師兄手術紀錄＿Acopy.mp4",
        "size": 2510779329,
        "size_mb": 2394.47,
        "estimated_duration": 4788.931520462036,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\240123_諾貝爾眼科Ｘ大師兄_雷射手術紀錄 Final.mp4",
        "name": "240123_諾貝爾眼科Ｘ大師兄_雷射手術紀錄 Final.mp4",
        "size": 2513500591,
        "size_mb": 2397.06,
        "estimated_duration": 4794.121915817261,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\連祐暘醫師\\C0411.MP4",
        "name": "C0411.MP4",
        "size": 2282022513,
        "size_mb": 2176.31,
        "estimated_duration": 4352.6125202178955,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0131.MP4",
        "name": "C0131.MP4",
        "size": 3120955637,
        "size_mb": 2976.38,
        "estimated_duration": 5952.750467300415,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\桌面\\20240127 小珍奶_SMILE PRO\\C0148.MP4",
        "name": "C0148.MP4",
        "size": 973294119,
        "size_mb": 928.21,
        "estimated_duration": 1856.4112071990967,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1094.MP4",
        "name": "C1094.MP4",
        "size": 1308865822,
        "size_mb": 1248.23,
        "estimated_duration": 2496.463436126709,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1103.MP4",
        "name": "C1103.MP4",
        "size": 1208192487,
        "size_mb": 1152.22,
        "estimated_duration": 2304.444288253784,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1104.MP4",
        "name": "C1104.MP4",
        "size": 973293276,
        "size_mb": 928.2,
        "estimated_duration": 1856.4095993041992,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1105.MP4",
        "name": "C1105.MP4",
        "size": 2013565301,
        "size_mb": 1920.29,
        "estimated_duration": 3840.57102394104,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1107.MP4",
        "name": "C1107.MP4",
        "size": 1644437445,
        "size_mb": 1568.26,
        "estimated_duration": 3136.5155124664307,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\C1108.MP4",
        "name": "C1108.MP4",
        "size": 1107521547,
        "size_mb": 1056.21,
        "estimated_duration": 2112.429708480835,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1120.MP4",
        "name": "C1120.MP4",
        "size": 1745108130,
        "size_mb": 1664.26,
        "estimated_duration": 3328.5296058654785,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1121.MP4",
        "name": "C1121.MP4",
        "size": 1409536642,
        "size_mb": 1344.24,
        "estimated_duration": 2688.4777870178223,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1122.MP4",
        "name": "C1122.MP4",
        "size": 6308908329,
        "size_mb": 6016.64,
        "estimated_duration": 12033.287675857544,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\少鹽\\20241203 少鹽 PS啦啦隊 101 SILK 呂醫師\\術後\\C1123.MP4",
        "name": "C1123.MP4",
        "size": 1476651974,
        "size_mb": 1408.25,
        "estimated_duration": 2816.4901237487793,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\C0475.MP4",
        "name": "C0475.MP4",
        "size": 12605849906,
        "size_mb": 12021.88,
        "estimated_duration": 24043.75058364868,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\C0488.MP4",
        "name": "C0488.MP4",
        "size": 8863954446,
        "size_mb": 8453.33,
        "estimated_duration": 16906.65139389038,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\C0489.MP4",
        "name": "C0489.MP4",
        "size": 23437233426,
        "size_mb": 22351.49,
        "estimated_duration": 44702.975131988525,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\C0490.MP4",
        "name": "C0490.MP4",
        "size": 6518968828,
        "size_mb": 6216.97,
        "estimated_duration": 12433.946281433105,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\吳明穎 醫師.mp4",
        "name": "吳明穎 醫師.mp4",
        "size": 4744560922,
        "size_mb": 4524.77,
        "estimated_duration": 9049.531787872314,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\徐昊 醫師.mp4",
        "name": "徐昊 醫師.mp4",
        "size": 4961299650,
        "size_mb": 4731.46,
        "estimated_duration": 9462.928104400635,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\曾俊夫 醫師.mp4",
        "name": "曾俊夫 醫師.mp4",
        "size": 3246508742,
        "size_mb": 3096.11,
        "estimated_duration": 6192.224010467529,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\林世強 醫師.mp4",
        "name": "林世強 醫師.mp4",
        "size": 5002444445,
        "size_mb": 4770.7,
        "estimated_duration": 9541.405572891235,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\林君曄 醫師.mp4",
        "name": "林君曄 醫師.mp4",
        "size": 5398832785,
        "size_mb": 5148.73,
        "estimated_duration": 10297.456331253052,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\梁仲斌 醫師.mp4",
        "name": "梁仲斌 醫師.mp4",
        "size": 4453445687,
        "size_mb": 4247.14,
        "estimated_duration": 8494.273542404175,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\王修含 醫師.mp4",
        "name": "王修含 醫師.mp4",
        "size": 3839960488,
        "size_mb": 3662.07,
        "estimated_duration": 7324.14338684082,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\王興良 醫師.mp4",
        "name": "王興良 醫師.mp4",
        "size": 5360643566,
        "size_mb": 5112.31,
        "estimated_duration": 10224.616176605225,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\莊子毅醫師(中間有斷).mp4",
        "name": "莊子毅醫師(中間有斷).mp4",
        "size": 5882446554,
        "size_mb": 5609.94,
        "estimated_duration": 11219.876392364502,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\鄭煜斌 醫師.mp4",
        "name": "鄭煜斌 醫師.mp4",
        "size": 6058457239,
        "size_mb": 5777.8,
        "estimated_duration": 11555.590131759644,
        "extension": ".mp4"
    },
    {
        "path": "C:\\Users\\USER-ART0\\Desktop\\0713微整\\錄影\\713錄影分段\\陳昱璁 醫師.mp4",
        "name": "陳昱璁 醫師.mp4",
        "size": 4933660725,
        "size_mb": 4705.11,
        "estimated_duration": 9410.211038589478,
        "extension": ".mp4"
    }
]
    performance_modes = ['auto', 'gpu', 'cpu']
    
    results = []
    
    for file_info in test_files:
        file_path = file_info['path']
        if not Path(file_path).exists():
            print(f"警告: 檔案不存在 {file_path}")
            continue
            
        print(f"測試檔案: {file_info['name']} ({file_info['estimated_duration']:.1f}s)")
        
        for mode in performance_modes:
            print(f"  測試模式: {mode}")
            
            # 構建測試命令
            cmd = [
                "python",
                str(Path(__file__).parent.parent / "electron_backend.py"),
                "--files", f'["{file_path}"]',
                "--settings", f'{"model":"large","language":"auto","performanceMode":"{mode}","outputFormat":"srt","customDir":"C:/temp/test_results","enable_gpu":{"true" if mode=="gpu" else "false"}}',
                "--corrections", "[]"
            ]
            
            # 執行測試
            start_time = time.time()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                end_time = time.time()
                
                processing_time = end_time - start_time
                rtf = processing_time / file_info['estimated_duration']
                
                test_result = {
                    'file': file_info['name'],
                    'mode': mode,
                    'processing_time': processing_time,
                    'audio_duration': file_info['estimated_duration'],
                    'rtf': rtf,
                    'success': result.returncode == 0,
                    'stdout': result.stdout[:500],  # 前500字符
                    'stderr': result.stderr[:500] if result.stderr else None
                }
                
                results.append(test_result)
                
                print(f"    處理時間: {processing_time:.1f}s")
                print(f"    RTF: {rtf:.3f}")
                print(f"    狀態: {'成功' if test_result['success'] else '失敗'}")
                
                if not test_result['success']:
                    print(f"    錯誤: {result.stderr[:200]}")
                
            except subprocess.TimeoutExpired:
                print(f"    超時 (>10分鐘)")
                results.append({'file': file_info['name'], 'mode': mode, 'status': 'timeout'})
            except Exception as e:
                print(f"    異常: {e}")
                results.append({'file': file_info['name'], 'mode': mode, 'status': 'error', 'error': str(e)})
            
            print()
    
    # 保存結果
    result_file = Path(__file__).parent / "stress_test_results.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({'test_name': 'stress_test', 'results': results, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}, f, ensure_ascii=False, indent=2)
    
    print(f"測試結果已保存至: {result_file}")
    return results

if __name__ == "__main__":
    results = run_performance_test()
    print(f"\nstress_test 測試完成，共執行 {len(results)} 個測試案例")
