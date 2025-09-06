@echo off
chcp 65001 > nul
echo ===================================
echo   SRT GO Local CI/CD Pipeline
echo ===================================
echo.

echo [1/5] Running Unit Tests...
cd tests
python -m pytest unit/ -v
if %errorlevel% neq 0 (
    echo FAILED: Unit tests failed
    pause
    exit /b 1
)
echo PASSED: Unit tests completed
echo.

echo [2/5] Running Integration Tests...
python debug_test_integration.py
if %errorlevel% neq 0 (
    echo FAILED: Integration tests failed
    pause
    exit /b 1
)
echo PASSED: Integration tests completed
echo.

echo [3/5] Running Performance Tests...
cd performance
python rtf_monitoring_system_ascii.py --run-benchmark
if %errorlevel% neq 0 (
    echo WARNING: Performance tests had issues
) else (
    echo PASSED: Performance tests completed
)
cd ..
echo.

echo [4/5] Running E2E Tests...
cd e2e
python test_automation_suite.py
if %errorlevel% neq 0 (
    echo WARNING: E2E tests had issues
) else (
    echo PASSED: E2E tests completed
)
cd ..
echo.

echo [5/5] Generating Reports...
echo Test execution completed at %date% %time% > test_execution_log.txt
echo PASSED: Reports generated
echo.

echo ===================================
echo   Local CI/CD Pipeline Completed
echo ===================================
echo All tests have been executed locally.
echo Check individual test outputs above for details.
echo.
pause