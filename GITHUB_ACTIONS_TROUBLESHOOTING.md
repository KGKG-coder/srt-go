# GitHub Actions Troubleshooting Guide

## Current Status
- **Repository**: https://github.com/zzxxcc0805/srt-go
- **Issue**: Actions page shows 404 error
- **Workflow Files**: 8 files successfully pushed
- **Last Push**: 17cfe32 (Actions Initialization)

## Immediate Action Required

### Step 1: Check Repository Visibility
1. Visit: https://github.com/zzxxcc0805/srt-go/settings
2. Scroll to "Danger Zone"
3. Ensure repository is set to **Public** (not Private)

### Step 2: Enable Actions
1. Visit: https://github.com/zzxxcc0805/srt-go/settings/actions
2. Under "Actions permissions", select:
   - ✅ "Allow all actions and reusable workflows"
3. Under "Workflow permissions", ensure:
   - ✅ "Read and write permissions" is selected

### Step 3: Manual Trigger
1. Wait 2-3 minutes after enabling Actions
2. Visit: https://github.com/zzxxcc0805/srt-go/actions
3. If still 404, try: https://github.com/zzxxcc0805/srt-go/actions/workflows/init-actions.yml
4. Click "Run workflow" button

## Deployed Workflows
- `init-actions.yml` - Simple initialization workflow
- `quick-start.yml` - Quick start test
- `ci-cd-pipeline.yml` - Full 7-stage CI/CD pipeline
- `force-enable.yml` - Force enable Actions
- `manual-trigger.yml` - Manual trigger test
- `simple-test.yml` - Basic test
- `test-minimal.yml` - Minimal test
- `test.yml` - Legacy test

## Backup Solution
If GitHub Actions continues to have issues, use local testing:

```bash
# Run local CI/CD pipeline
run_local_ci.bat

# Run specific tests
cd tests
python -m pytest unit/ -v
```

## Contact Information
- Repository Owner: zzxxcc0805
- Testing Framework: Complete commercial-grade implementation
- Status: Ready for activation pending Actions enablement