/**
 * DLL依賴診斷工具 - 識別error code 3221225781的根本原因
 */

const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

/**
 * 檢查DLL依賴
 */
function checkDllDependencies() {
    console.log('=== DLL依賴診斷 ===')
    
    const workingPython = path.resolve('mini_python/python.exe')
    const brokenPython = path.resolve('dist/SRT-GO-Enhanced-v2.0-Complete/resources/mini_python/python.exe')
    
    console.log(`工作版本: ${workingPython}`)
    console.log(`問題版本: ${brokenPython}`)
    
    // 檢查文件是否存在
    console.log('\n=== 文件存在性檢查 ===')
    console.log(`工作版本存在: ${fs.existsSync(workingPython)}`)
    console.log(`問題版本存在: ${fs.existsSync(brokenPython)}`)
    
    if (fs.existsSync(workingPython)) {
        const workingStats = fs.statSync(workingPython)
        console.log(`工作版本大小: ${workingStats.size} bytes`)
        console.log(`工作版本修改時間: ${workingStats.mtime}`)
    }
    
    if (fs.existsSync(brokenPython)) {
        const brokenStats = fs.statSync(brokenPython)
        console.log(`問題版本大小: ${brokenStats.size} bytes`)
        console.log(`問題版本修改時間: ${brokenStats.mtime}`)
    }
    
    // 使用Windows dependency walker替代品 - dumpbin
    console.log('\n=== 嘗試執行最簡單的Python命令 ===')
    
    // 測試工作版本
    console.log('\n1. 測試工作版本...')
    testPythonExecution(workingPython, '工作版本')
    
    // 測試問題版本
    console.log('\n2. 測試問題版本...')
    testPythonExecution(brokenPython, '問題版本')
}

/**
 * 測試Python執行
 */
function testPythonExecution(pythonPath, label) {
    try {
        console.log(`${label} - 啟動Python進程...`)
        
        const proc = spawn(pythonPath, ['-c', 'print("Hello")'], {
            stdio: ['pipe', 'pipe', 'pipe'],
            windowsHide: false,
            shell: false
        })
        
        let output = ''
        let error = ''
        
        proc.stdout.on('data', (data) => {
            output += data.toString()
        })
        
        proc.stderr.on('data', (data) => {
            error += data.toString()
        })
        
        proc.on('close', (code) => {
            console.log(`${label} - 退出代碼: ${code}`)
            if (output) console.log(`${label} - 輸出: ${output.trim()}`)
            if (error) console.log(`${label} - 錯誤: ${error.trim()}`)
            
            if (code === 3221225781) {
                console.log(`${label} - 確認Access Violation錯誤！`)
                console.log(`${label} - 十六進制碼: 0x${code.toString(16).toUpperCase()}`)
            } else if (code === 0) {
                console.log(`${label} - 正常運行！`)
            } else {
                console.log(`${label} - 其他錯誤碼: ${code}`)
            }
        })
        
        proc.on('error', (err) => {
            console.error(`${label} - 進程啟動失敗: ${err.message}`)
            console.error(`${label} - 錯誤代碼: ${err.code}`)
        })
        
        // 3秒超時
        setTimeout(() => {
            if (!proc.killed) {
                console.log(`${label} - 超時，終止進程`)
                proc.kill()
            }
        }, 3000)
        
    } catch (error) {
        console.error(`${label} - 測試失敗: ${error.message}`)
    }
}

/**
 * 檢查Python環境變數
 */
function checkPythonEnvironment() {
    console.log('\n=== Python環境變數檢查 ===')
    
    const workingDir = path.resolve('mini_python')
    const brokenDir = path.resolve('dist/SRT-GO-Enhanced-v2.0-Complete/resources/mini_python')
    
    console.log(`工作目錄: ${workingDir}`)
    console.log(`問題目錄: ${brokenDir}`)
    
    // 檢查關鍵DLL
    const dlls = ['python311.dll', 'vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll']
    
    console.log('\n=== 關鍵DLL檢查 ===')
    for (const dll of dlls) {
        const workingDll = path.join(workingDir, dll)
        const brokenDll = path.join(brokenDir, dll)
        
        const workingExists = fs.existsSync(workingDll)
        const brokenExists = fs.existsSync(brokenDll)
        
        console.log(`${dll}:`)
        console.log(`  工作版本: ${workingExists ? '存在' : '缺失'}`)
        console.log(`  問題版本: ${brokenExists ? '存在' : '缺失'}`)
        
        if (workingExists && brokenExists) {
            const workingSize = fs.statSync(workingDll).size
            const brokenSize = fs.statSync(brokenDll).size
            
            if (workingSize !== brokenSize) {
                console.log(`  ❌ 大小不匹配: ${workingSize} vs ${brokenSize}`)
            } else {
                console.log(`  ✅ 大小匹配: ${workingSize} bytes`)
            }
        }
    }
}

/**
 * 主要診斷函數
 */
async function main() {
    console.log('Python DLL 依賴診斷工具')
    console.log('用於解決 error code 3221225781 (Access Violation)')
    console.log('='.repeat(50))
    
    checkDllDependencies()
    
    setTimeout(() => {
        checkPythonEnvironment()
    }, 5000)
}

// 執行診斷
main().catch(console.error)