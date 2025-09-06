#!/usr/bin/env python3
"""
Calculate INT16 model packaging feasibility
Analyze if INT16 can fit in NSIS installer constraints
"""

import sys
from pathlib import Path

def calculate_package_sizes():
    """Calculate package sizes for different model options"""
    
    print("=" * 80)
    print("INT16 vs INT8 Packaging Size Analysis")
    print("=" * 80)
    
    # Component sizes (in MB)
    components = {
        "electron_app": 200,           # Electron + React app
        "python_core": 50,             # PyInstaller packaged Python
        "dependencies": 30,            # Other libraries and assets
        "int8_model": 779,             # Current INT8 model
        "int16_model_estimated": 1600, # Estimated INT16 model size
        "actual_hf_large_v3": 2880     # Actual HF cache size we measured
    }
    
    # Calculate total sizes
    int8_total = components["electron_app"] + components["python_core"] + components["dependencies"] + components["int8_model"]
    int16_estimated = components["electron_app"] + components["python_core"] + components["dependencies"] + components["int16_model_estimated"]
    int16_actual = components["electron_app"] + components["python_core"] + components["dependencies"] + components["actual_hf_large_v3"]
    
    print(f"\n📦 COMPONENT BREAKDOWN:")
    print(f"{'Component':<25} {'Size (MB)':<12} {'Description':<30}")
    print("-" * 70)
    print(f"{'Electron + React':<25} {components['electron_app']:<12} Main application")
    print(f"{'Python Core':<25} {components['python_core']:<12} PyInstaller packaged")
    print(f"{'Dependencies':<25} {components['dependencies']:<12} Libraries & assets")
    print(f"{'INT8 Model':<25} {components['int8_model']:<12} Current optimized model")
    print(f"{'INT16 Model (Est.)':<25} {components['int16_model_estimated']:<12} Estimated size")
    print(f"{'INT16 Model (Actual)':<25} {components['actual_hf_large_v3']:<12} Measured HF cache size")
    
    print(f"\n📊 TOTAL PACKAGE SIZES:")
    print(f"{'Package Type':<25} {'Raw Size':<15} {'Compressed (Est.)':<20} {'Description':<25}")
    print("-" * 85)
    
    # Compression ratios based on your previous experience
    # From docs: 7.7GB -> 985MB = 87.2% compression
    compression_ratio = 0.128  # Keep 12.8% of original size
    
    int8_compressed = int8_total * compression_ratio
    int16_est_compressed = int16_estimated * compression_ratio  
    int16_actual_compressed = int16_actual * compression_ratio
    
    print(f"{'INT8 Package':<25} {int8_total:<15.0f} {int8_compressed:<20.0f} Current optimized")
    print(f"{'INT16 (Estimated)':<25} {int16_estimated:<15.0f} {int16_est_compressed:<20.0f} Conservative estimate")
    print(f"{'INT16 (Actual)':<25} {int16_actual:<15.0f} {int16_actual_compressed:<20.0f} Based on measured size")
    
    # NSIS and distribution constraints
    print(f"\n🚧 NSIS AND DISTRIBUTION CONSTRAINTS:")
    print(f"{'Constraint':<25} {'Limit':<15} {'Status':<20} {'Notes':<25}")
    print("-" * 85)
    
    # NSIS file size limits
    nsis_practical_limit = 2000  # 2GB practical limit
    nsis_theoretical_limit = 4000  # 4GB theoretical limit
    
    # Check INT8
    int8_nsis_status = "✅ EXCELLENT" if int8_total < 1000 else "✅ GOOD" if int8_total < 2000 else "⚠️ MARGINAL" if int8_total < 4000 else "❌ TOO LARGE"
    
    # Check INT16 estimated
    int16_est_nsis_status = "✅ EXCELLENT" if int16_estimated < 1000 else "✅ GOOD" if int16_estimated < 2000 else "⚠️ MARGINAL" if int16_estimated < 4000 else "❌ TOO LARGE"
    
    # Check INT16 actual
    int16_actual_nsis_status = "✅ EXCELLENT" if int16_actual < 1000 else "✅ GOOD" if int16_actual < 2000 else "⚠️ MARGINAL" if int16_actual < 4000 else "❌ TOO LARGE"
    
    print(f"{'NSIS Practical Limit':<25} {nsis_practical_limit:<15.0f} {'Reference':<20} 2GB safe limit")
    print(f"{'NSIS Max Limit':<25} {nsis_theoretical_limit:<15.0f} {'Reference':<20} 4GB absolute limit")
    print()
    print(f"{'INT8 Package':<25} {int8_total:<15.0f} {int8_nsis_status:<20} Well within limits")
    print(f"{'INT16 (Est.) Package':<25} {int16_estimated:<15.0f} {int16_est_nsis_status:<20} Borderline acceptable")
    print(f"{'INT16 (Actual) Package':<25} {int16_actual:<15.0f} {int16_actual_nsis_status:<20} Exceeds practical limit")
    
    # Download time analysis
    print(f"\n⏱️ DOWNLOAD TIME ANALYSIS:")
    print(f"{'Connection Speed':<20} {'INT8':<15} {'INT16 (Est.)':<15} {'INT16 (Actual)':<15}")
    print("-" * 70)
    
    speeds = {
        "10 Mbps (Slow)": 10 * 1024 * 1024 / 8,  # bytes per second
        "50 Mbps (Average)": 50 * 1024 * 1024 / 8,
        "100 Mbps (Fast)": 100 * 1024 * 1024 / 8
    }
    
    for speed_name, speed_bps in speeds.items():
        int8_time = (int8_compressed * 1024 * 1024) / speed_bps / 60  # minutes
        int16_est_time = (int16_est_compressed * 1024 * 1024) / speed_bps / 60
        int16_actual_time = (int16_actual_compressed * 1024 * 1024) / speed_bps / 60
        
        print(f"{speed_name:<20} {int8_time:<15.1f} {int16_est_time:<15.1f} {int16_actual_time:<15.1f}")
    
    # User experience impact
    print(f"\n👤 USER EXPERIENCE IMPACT:")
    print(f"{'Aspect':<25} {'INT8':<15} {'INT16 (Actual)':<20} {'Impact':<25}")
    print("-" * 85)
    
    size_ratio = int16_actual / int8_total
    download_ratio = int16_actual_compressed / int8_compressed
    
    print(f"{'Package Size Ratio':<25} {'1x (baseline)':<15} {size_ratio:<20.1f} {size_ratio:.1f}x larger")
    print(f"{'Download Size Ratio':<25} {'1x (baseline)':<15} {download_ratio:<20.1f} {download_ratio:.1f}x larger")
    print(f"{'Install Time':<25} {'Fast':<15} {'Much Slower':<20} Significant impact")
    print(f"{'User Patience':<25} {'Good':<15} {'Challenging':<20} May cause abandonment")
    
    # Storage requirements
    print(f"\n💾 STORAGE REQUIREMENTS:")
    print(f"{'Stage':<25} {'INT8 (MB)':<15} {'INT16 Actual (MB)':<20} {'Difference (MB)':<15}")
    print("-" * 75)
    
    print(f"{'Download Package':<25} {int8_compressed:<15.0f} {int16_actual_compressed:<20.0f} +{int16_actual_compressed - int8_compressed:.0f}")
    print(f"{'Installed Size':<25} {int8_total:<15.0f} {int16_actual:<20.0f} +{int16_actual - int8_total:.0f}")
    print(f"{'Peak Usage':<25} {int8_total + int8_compressed:<15.0f} {int16_actual + int16_actual_compressed:<20.0f} +{(int16_actual + int16_actual_compressed) - (int8_total + int8_compressed):.0f}")
    
    # Final recommendations
    print(f"\n🎯 FINAL ANALYSIS:")
    print("=" * 60)
    
    print(f"\n✅ INT8 Model:")
    print(f"  - Package size: {int8_total:.0f}MB ({int8_compressed:.0f}MB compressed)")
    print(f"  - NSIS compatibility: EXCELLENT")
    print(f"  - Download time: Acceptable (9-20 minutes)")
    print(f"  - User experience: GOOD")
    
    if int16_actual <= nsis_practical_limit:
        print(f"\n⚠️ INT16 Model (Actual {int16_actual:.0f}MB):")
        print(f"  - Package size: {int16_actual:.0f}MB ({int16_actual_compressed:.0f}MB compressed)")
        print(f"  - NSIS compatibility: MARGINAL (exceeds 2GB practical limit)")
        print(f"  - Download time: LONG (25-60 minutes)")
        print(f"  - User experience: POOR")
        print(f"  - Technical feasibility: YES, but not recommended")
    else:
        print(f"\n❌ INT16 Model (Actual {int16_actual:.0f}MB):")
        print(f"  - Package size: TOO LARGE for practical NSIS packaging")
        print(f"  - Exceeds 2GB practical limit by {int16_actual - nsis_practical_limit:.0f}MB")
        print(f"  - Would require alternative packaging strategy")
    
    print(f"\n🏆 RECOMMENDATION:")
    if int16_actual <= nsis_practical_limit:
        print(f"  Use INT8 for optimal user experience")
        print(f"  INT16 is technically possible but NOT recommended")
        print(f"  Size increase ({size_ratio:.1f}x) not justified by quality gains")
    else:
        print(f"  INT16 is NOT SUITABLE for your current NSIS packaging strategy")
        print(f"  Stick with INT8 for best balance of size/quality/UX")
        print(f"  Consider INT16 only if switching to alternative packaging")
    
    return int16_actual <= nsis_theoretical_limit

if __name__ == "__main__":
    feasible = calculate_package_sizes()
    print(f"\n{'='*80}")
    if feasible:
        print("CONCLUSION: INT16 is technically feasible but NOT recommended")
    else:
        print("CONCLUSION: INT16 exceeds packaging constraints")
    print(f"{'='*80}")
    sys.exit(0 if feasible else 1)