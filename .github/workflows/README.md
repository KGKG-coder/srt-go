# GitHub Actions Workflows

This directory contains the streamlined CI/CD pipeline configuration for SRT GO v2.2.1.

## 🚀 Optimized Workflows (5 Essential)

### 1. `ci-cd-pipeline.yml` - Complete CI/CD Pipeline
**Trigger**: Push to main/develop branches, Pull requests, Nightly schedule
**Duration**: ~60-90 minutes

**7-Stage Pipeline**:
1. **Unit Tests** (5 min) - Python component testing
2. **Integration Tests** (10 min) - Workflow validation  
3. **Performance Tests** (15 min) - RTF benchmarks
4. **E2E Tests** (20 min) - Complete automation suite
5. **Build Application** (25 min) - Installer + Portable
6. **Security Scan** (10 min) - CodeQL + dependency audit
7. **Deploy Release** (5 min) - GitHub release creation

### 2. `quick-test.yml` - Fast Testing
**Trigger**: Manual dispatch, Push to develop branch
**Duration**: ~5-20 minutes

**Test Levels**:
- `basic`: Core functionality validation
- `full`: Complete test suite in quick mode  
- `performance`: RTF benchmarks only

### 3. `performance-monitoring.yml` - Continuous Monitoring
**Trigger**: Daily schedule (2 AM UTC), Manual dispatch
**Duration**: ~60-120 minutes

**Monitoring Types**:
- `standard`: Daily performance benchmarks
- `intensive`: Comprehensive system stress testing
- `regression`: Performance comparison with baseline

### 4. `manual-testing.yml` - Component Testing
**Trigger**: Manual dispatch only
**Duration**: ~20-60 minutes

**Test Components**:
- `fp16-model` - FP16 model manager testing
- `voice-detection` - Adaptive voice detection
- `backend-selector` - Smart Python environment selection
- `performance-monitor` - RTF monitoring system
- `ui-integration` - Electron + React integration

### 5. `release-builder.yml` - Release Creation
**Trigger**: Manual dispatch only
**Duration**: ~60 minutes

**Options**:
- Version specification (e.g., v2.2.1)
- Release type (stable/beta/alpha)
- AI models bundling toggle

## 📊 Workflow Status Badges

Add these badges to your README.md:

```markdown
[![CI/CD Pipeline](https://github.com/your-repo/srt-go/actions/workflows/ci-cd-pipeline.yml/badge.svg)](https://github.com/your-repo/srt-go/actions/workflows/ci-cd-pipeline.yml)
[![Quick Tests](https://github.com/your-repo/srt-go/actions/workflows/quick-test.yml/badge.svg)](https://github.com/your-repo/srt-go/actions/workflows/quick-test.yml)
[![Performance Monitoring](https://github.com/your-repo/srt-go/actions/workflows/performance-monitoring.yml/badge.svg)](https://github.com/your-repo/srt-go/actions/workflows/performance-monitoring.yml)
```

## 🔧 Workflow Configuration

### Environment Variables
```yaml
PYTHON_VERSION: '3.11'
NODE_VERSION: '18'  
ELECTRON_CACHE: ${{ github.workspace }}/.cache/electron
HUGGINGFACE_HUB_CACHE: ${{ github.workspace }}/.cache/huggingface
```

### Cache Strategy
- **Python packages**: pip cache based on requirements.txt
- **Node packages**: npm cache based on package-lock.json
- **AI models**: HuggingFace cache (persistent across runs)
- **Electron binaries**: Version-based caching

### Secrets Required
```yaml
GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Automatic
# No additional secrets required for basic functionality
```

## 📈 Performance Baselines

### Target Metrics
- **RTF Performance**: < 0.8 for CPU, < 0.15 for GPU
- **Test Success Rate**: 100% for E2E suite
- **Build Time**: < 30 minutes for complete pipeline
- **Security**: Zero critical vulnerabilities

### Quality Gates
- **Unit Tests**: Must pass before integration tests
- **Performance**: RTF regression detection (>20% slower fails)
- **Security**: Critical vulnerabilities block release
- **E2E**: 100% success rate required for deployment

## 🛠️ Local Development

### Run Tests Locally
```bash
# Quick validation
cd tests/performance
python quick_rtf_test.py --basic-only

# E2E tests
cd tests/e2e  
python test_automation_suite.py --quick-mode

# Performance suite
cd tests/performance
python comprehensive_performance_suite.py --standard
```

### Build Locally
```bash
cd srt_whisper_lite/electron-react-app
npm run build:with-models
npm run dist:nsis
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Download Failures**
   - Check network connectivity
   - Verify HuggingFace hub access
   - Clear cache: `~/.cache/huggingface/`

2. **Build Timeouts**
   - Increase timeout in workflow file
   - Check resource usage (Windows runners limited)
   - Consider splitting builds

3. **Test Failures**
   - Check test file paths (use absolute paths)
   - Verify Python environment setup
   - Review test logs in Actions output

4. **Security Scan Issues**
   - Update dependencies: `npm audit fix`
   - Check Python security: `safety check`
   - Review CodeQL findings

### Debug Commands
```bash
# Check workflow syntax
yaml-lint .github/workflows/*.yml

# Validate GitHub Actions locally
act -n  # Dry run
act     # Full run (requires Docker)

# Check Python environment
python -c "import sys; print(sys.version, sys.executable)"
pip list | grep -E "(faster-whisper|torch|numpy)"
```

## 📚 Documentation

- **CLAUDE.md**: Development guidelines
- **README.md**: Project overview
- **RELEASE_NOTES_v2.2.1.md**: Detailed release information
- **USER_MANUAL_v2.2.1.md**: Complete user documentation

---

**📧 Support**: For workflow issues, create an issue with:
- Workflow name and run ID
- Error logs from Actions output  
- System information and configuration
- Steps to reproduce the issue

**🔄 Updates**: Workflows are automatically validated on push to `.github/workflows/` directory.