#!/usr/bin/env python3
"""
GitHub Actions 診斷工具
用於檢查 Actions 狀態和問題排查
"""

import subprocess
import os
from pathlib import Path

def run_command(cmd):
    """執行命令並返回結果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return None, str(e)

def main():
    print("GitHub Actions Diagnostic Report")
    print("=" * 40)
    
    # Check git status
    print("\nGit Repository Status:")
    stdout, stderr = run_command("git remote -v")
    print(f"Remote: {stdout}")
    
    stdout, stderr = run_command("git branch")
    print(f"Branch: {stdout}")
    
    stdout, stderr = run_command("git status --porcelain")
    print(f"Status: {'Clean' if not stdout else 'Modified files present'}")
    
    # Check workflow files
    print("\nWorkflow Files:")
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        for yml_file in workflows_dir.glob("*.yml"):
            print(f"OK {yml_file.name}")
    else:
        print("ERROR: .github/workflows directory not found")
    
    # Check recent commits
    print("\nRecent Commits:")
    stdout, stderr = run_command("git log --oneline -3")
    print(stdout)
    
    # Troubleshooting suggestions
    print("\nTroubleshooting Suggestions:")
    print("1. Ensure repository is Public")
    print("2. Check GitHub account has Actions enabled")
    print("3. Visit: https://github.com/zzxxcc0805/srt-go/settings/actions")
    print("4. Wait 2-5 minutes for Actions to initialize")
    print("5. Revisit: https://github.com/zzxxcc0805/srt-go/actions")
    
    print(f"\nRepository Actions URL: https://github.com/zzxxcc0805/srt-go/actions")
    print(f"Repository Settings URL: https://github.com/zzxxcc0805/srt-go/settings")

if __name__ == "__main__":
    main()