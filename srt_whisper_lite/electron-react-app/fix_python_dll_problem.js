/**
 * 修復Python DLL問題 - 下載並安裝缺失的python311.dll
 */

const fs = require('fs')
const path = require('path')
const https = require('https')
const { execSync } = require('child_process')

/**
 * 下載python311.dll從系統或網路源
 */
async function fixPythonDll() {
    console.log('=== 修復Python DLL問題 ===')
    
    const targetDirs = [
        path.resolve('mini_python'),
        path.resolve('dist/SRT-GO-Enhanced-v2.0-Complete/resources/mini_python')
    ]
    
    // 首先嘗試從系統Python複製
    const systemPython311Paths = [
        'C:\\Windows\\System32\\python311.dll',
        'C:\\Python311\\python311.dll',
        'C:\\Program Files\\Python311\\python311.dll',
        'C:\\Users\\' + process.env.USERNAME + '\\AppData\\Local\\Programs\\Python\\Python311\\python311.dll',
        process.env.LOCALAPPDATA + '\\Programs\\Python\\Python311\\python311.dll'
    ]
    
    let foundSystemDll = null
    
    console.log('搜索系統Python 3.11 DLL...')
    for (const dllPath of systemPython311Paths) {
        if (fs.existsSync(dllPath)) {
            console.log(`✅ 找到系統DLL: ${dllPath}`)
            foundSystemDll = dllPath
            break
        }
    }
    
    if (foundSystemDll) {
        console.log('從系統複製python311.dll...')
        for (const targetDir of targetDirs) {
            if (fs.existsSync(targetDir)) {
                const targetFile = path.join(targetDir, 'python311.dll')
                try {
                    fs.copyFileSync(foundSystemDll, targetFile)
                    console.log(`✅ 複製到: ${targetFile}`)
                } catch (error) {
                    console.error(`❌ 複製失敗: ${error.message}`)
                }
            }
        }
    } else {
        console.log('❌ 未找到系統Python 3.11 DLL')
        console.log('需要下載Python 3.11 embeddable package...')
        await downloadPythonEmbeddable()
    }
    
    // 檢查其他可能缺失的DLL
    await checkAdditionalDlls()
    
    // 測試修復結果
    console.log('\n=== 測試修復結果 ===')
    for (const targetDir of targetDirs) {
        if (fs.existsSync(targetDir)) {
            await testPythonExecution(path.join(targetDir, 'python.exe'), path.basename(targetDir))
        }
    }
}

/**
 * 下載Python嵌入式包
 */
async function downloadPythonEmbeddable() {
    console.log('下載Python 3.11 embeddable package...')
    
    // 檢查是否已經有python311.zip
    const mini_python = path.resolve('mini_python')
    const python311zip = path.join(mini_python, 'python311.zip')
    
    if (fs.existsSync(python311zip)) {
        console.log('已有python311.zip，嘗試提取python311.dll...')
        
        try {
            // 使用PowerShell解壓
            const extractCmd = `powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('${python311zip}', '${mini_python}/temp_extract')"`
            execSync(extractCmd, { stdio: 'inherit' })
            
            // 尋找解壓後的DLL
            const tempDir = path.join(mini_python, 'temp_extract')
            const extractedDll = path.join(tempDir, 'python311.dll')
            
            if (fs.existsSync(extractedDll)) {
                // 複製到所有目標目錄
                const targetDirs = [
                    path.resolve('mini_python'),
                    path.resolve('dist/SRT-GO-Enhanced-v2.0-Complete/resources/mini_python')
                ]
                
                for (const targetDir of targetDirs) {
                    if (fs.existsSync(targetDir)) {
                        const targetFile = path.join(targetDir, 'python311.dll')
                        fs.copyFileSync(extractedDll, targetFile)
                        console.log(`✅ 提取並複製到: ${targetFile}`)
                    }
                }
            }
            
            // 清理臨時目錄
            if (fs.existsSync(tempDir)) {
                fs.rmSync(tempDir, { recursive: true })
            }
            
        } catch (error) {
            console.error('❌ 解壓失敗:', error.message)
        }
    }
}

/**
 * 檢查其他可能缺失的DLL
 */
async function checkAdditionalDlls() {
    console.log('\n=== 檢查其他可能缺失的DLL ===')
    
    const requiredDlls = [
        'python311.dll',
        'python311._pth',
        'vcruntime140.dll',
        'vcruntime140_1.dll'
    ]
    
    const mini_python = path.resolve('mini_python')
    
    for (const dll of requiredDlls) {
        const dllPath = path.join(mini_python, dll)
        if (fs.existsSync(dllPath)) {
            console.log(`✅ ${dll}: 存在`)
        } else {
            console.log(`❌ ${dll}: 缺失`)
            
            if (dll === 'vcruntime140.dll') {
                console.log('  搜索系統vcruntime140.dll...')
                const systemPaths = [
                    'C:\\Windows\\System32\\vcruntime140.dll',
                    'C:\\Windows\\SysWOW64\\vcruntime140.dll'
                ]
                
                for (const sysPath of systemPaths) {
                    if (fs.existsSync(sysPath)) {
                        try {
                            fs.copyFileSync(sysPath, dllPath)
                            console.log(`  ✅ 複製系統DLL: ${sysPath}`)
                            break
                        } catch (error) {
                            console.log(`  ❌ 複製失敗: ${error.message}`)
                        }
                    }
                }
            }
        }
    }
}

/**
 * 測試Python執行
 */
function testPythonExecution(pythonPath, label) {
    return new Promise((resolve) => {
        console.log(`測試 ${label}...`)
        
        const { spawn } = require('child_process')
        const proc = spawn(pythonPath, ['-c', 'import sys; print(f"Python {sys.version[:10]} OK")'], {
            stdio: ['pipe', 'pipe', 'pipe'],
            windowsHide: false
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
            if (code === 0) {
                console.log(`✅ ${label}: ${output.trim()}`)
            } else {
                console.log(`❌ ${label}: 退出碼 ${code}`)
                if (error) console.log(`   錯誤: ${error.trim()}`)
            }
            resolve(code)
        })
        
        proc.on('error', (err) => {
            console.log(`❌ ${label}: 進程錯誤 ${err.message}`)
            resolve(-1)
        })
        
        // 5秒超時
        setTimeout(() => {
            if (!proc.killed) {
                proc.kill()
                console.log(`❌ ${label}: 超時`)
                resolve(-2)
            }
        }, 5000)
    })
}

// 執行修復
fixPythonDll().catch(console.error)