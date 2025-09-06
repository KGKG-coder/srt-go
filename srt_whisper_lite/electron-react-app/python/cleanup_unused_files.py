#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cleanup Script for Unused Files and Dependencies
Based on comprehensive code analysis results
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectCleanup:
    """Clean up unused files and dependencies from the project"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "cleanup_backup"
        
        # Files identified as unused by code analysis
        self.unused_files = [
            "calculate_int16_package_size.py",
            "check_model_sizes.py", 
            "compare_results.py",
            "create_ultimate_pr_version.py",
            "direct_srt_comparison.py",
            "download_standard_int8.py",
            "enhanced_detector_comparison_analysis.py",
            "final_comparison_report.py",
            "segment_12_analysis_simple.py",
            "simple_interlude_corrector.py", 
            "simple_srt_analysis.py",
            "subtitle_comparison_analysis.py",
            "subtitle_comparison_simple.py",
            "threshold_optimization_analysis.py",
            # Test files that are no longer needed
            "test_existing_model.py",
            "test_fixed_timestamps.py",
            "test_int16_comparison.py",
            "test_int8_model.py",
            "test_large_video.py",
            "test_real_differences.py",
            "test_standard_model.py",
            "test_video_processing.py",
            "test_video_simple.py"
        ]
        
        # Keep essential files for the working system
        self.essential_files = [
            "electron_backend.py",  # Main backend
            "simplified_subtitle_core.py",  # Core engine
            "enhanced_lightweight_voice_detector.py",  # Enhanced v2.0 detector
            "adaptive_voice_detector.py",  # Adaptive voice detection
            "subeasy_multilayer_filter.py",  # SubEasy filtering
            "large_v3_int8_model_manager.py",  # Model management
            "lightweight_voice_detector.py",  # Basic detector (fallback)
            "subtitle_formatter.py",  # Output formatting
            "semantic_processor.py",  # Language processing
            "config_manager.py",  # Configuration
            "i18n.py",  # Internationalization
            "audio_processor.py",  # Audio preprocessing (may be used)
            "intelligent_interlude_filter.py",  # Advanced filtering
            "official_model_manager.py"  # Model management alternative
        ]
        
        self.cleanup_results = {
            "files_removed": [],
            "files_backed_up": [],
            "space_saved_mb": 0,
            "errors": []
        }
    
    def create_backup_directory(self):
        """Create backup directory for safety"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            logger.info(f"Created backup directory: {self.backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            return False
    
    def backup_and_remove_file(self, file_path: Path) -> bool:
        """Backup and remove a single file"""
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return True  # Consider as success if file doesn't exist
            
            # Calculate file size for tracking
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            
            # Backup the file
            backup_path = self.backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)
            self.cleanup_results["files_backed_up"].append(str(file_path.relative_to(self.project_root)))
            
            # Remove the original file
            file_path.unlink()
            self.cleanup_results["files_removed"].append(str(file_path.relative_to(self.project_root)))
            self.cleanup_results["space_saved_mb"] += file_size
            
            logger.info(f"Removed unused file: {file_path.name} ({file_size:.2f} MB)")
            return True
            
        except Exception as e:
            error_msg = f"Failed to remove {file_path}: {e}"
            logger.error(error_msg)
            self.cleanup_results["errors"].append(error_msg)
            return False
    
    def clean_unused_files(self) -> bool:
        """Clean up all unused files"""
        logger.info("Starting cleanup of unused files...")
        
        success_count = 0
        for filename in self.unused_files:
            file_path = self.project_root / filename
            if self.backup_and_remove_file(file_path):
                success_count += 1
        
        logger.info(f"Cleanup complete: {success_count}/{len(self.unused_files)} files processed")
        return success_count == len(self.unused_files)
    
    def clean_redundant_test_directories(self):
        """Clean up redundant test directories and temporary files"""
        redundant_patterns = [
            "**/test_*_backup*",
            "**/test_comparison*", 
            "**/analysis_*",
            "**/temp_*",
            "**/*_temp.py",
            "**/*_backup.py",
            "**/comparison_test"
        ]
        
        for pattern in redundant_patterns:
            for path in self.project_root.glob(pattern):
                if path.is_file():
                    self.backup_and_remove_file(path)
                elif path.is_dir() and path.name != "test_VIDEO":  # Keep test videos
                    try:
                        shutil.move(str(path), str(self.backup_dir / path.name))
                        logger.info(f"Moved directory to backup: {path}")
                    except Exception as e:
                        logger.error(f"Failed to backup directory {path}: {e}")
    
    def optimize_remaining_files(self):
        """Optimize remaining essential files by removing debug prints"""
        essential_paths = [self.project_root / f for f in self.essential_files if (self.project_root / f).exists()]
        
        for file_path in essential_paths:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Count debug statements
                debug_lines = content.count('print(') + content.count('logger.debug')
                
                if debug_lines > 10:  # Only optimize files with many debug statements
                    logger.info(f"File {file_path.name} has {debug_lines} debug statements - consider optimization")
                
            except Exception as e:
                logger.warning(f"Could not analyze {file_path}: {e}")
    
    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        report = {
            "cleanup_timestamp": str(Path().absolute()),
            "project_cleanup_results": self.cleanup_results,
            "summary": {
                "files_removed": len(self.cleanup_results["files_removed"]),
                "space_saved_mb": round(self.cleanup_results["space_saved_mb"], 2),
                "backup_location": str(self.backup_dir),
                "essential_files_preserved": len(self.essential_files),
                "errors_encountered": len(self.cleanup_results["errors"])
            },
            "next_steps": [
                "Test the system to ensure functionality is preserved",
                "Run integration tests to verify Enhanced Voice Detector v2.0",
                "Package the cleaned system for distribution",
                "Remove backup directory after confirming system works"
            ]
        }
        
        # Save report
        report_path = self.project_root / "cleanup_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Cleanup report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save cleanup report: {e}")
        
        return report
    
    def run_complete_cleanup(self) -> Dict:
        """Execute complete cleanup process"""
        logger.info("Starting complete project cleanup...")
        
        # Step 1: Create backup directory
        if not self.create_backup_directory():
            logger.error("Failed to create backup directory, aborting cleanup")
            return {"status": "failed", "reason": "backup_creation_failed"}
        
        # Step 2: Clean unused files
        unused_success = self.clean_unused_files()
        
        # Step 3: Clean redundant test directories  
        self.clean_redundant_test_directories()
        
        # Step 4: Optimize remaining files
        self.optimize_remaining_files()
        
        # Step 5: Generate report
        report = self.generate_cleanup_report()
        
        # Final status
        if unused_success and len(self.cleanup_results["errors"]) == 0:
            status = "success"
        elif unused_success:
            status = "partial_success" 
        else:
            status = "failed"
        
        logger.info(f"Cleanup completed with status: {status}")
        logger.info(f"Space saved: {self.cleanup_results['space_saved_mb']:.2f} MB")
        logger.info(f"Files removed: {len(self.cleanup_results['files_removed'])}")
        
        return {
            "status": status,
            "report": report,
            "space_saved_mb": self.cleanup_results['space_saved_mb'],
            "files_removed": len(self.cleanup_results['files_removed'])
        }

def main():
    """Main cleanup execution"""
    cleaner = ProjectCleanup()
    
    print("Project Cleanup Tool - Enhanced Voice Detector v2.0")
    print("=" * 55)
    print("This will remove unused files and optimize the project structure.")
    print("All files will be backed up before removal.")
    print()
    
    # Execute cleanup
    result = cleaner.run_complete_cleanup()
    
    print(f"\nCleanup Status: {result['status'].upper()}")
    print(f"Space Saved: {result['space_saved_mb']:.2f} MB")
    print(f"Files Processed: {result['files_removed']}")
    
    if result['status'] == 'success':
        print("\n✅ Cleanup completed successfully!")
        print("Next steps:")
        print("1. Test the system: python final_integration_test.py")
        print("2. Verify Enhanced Voice Detector v2.0 functionality")
        print("3. Package for distribution")
    else:
        print(f"\n⚠️ Cleanup completed with status: {result['status']}")
        print("Please check the cleanup report for details.")

if __name__ == "__main__":
    main()