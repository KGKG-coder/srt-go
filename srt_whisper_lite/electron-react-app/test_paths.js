
const path = require('path');

// 測試路徑處理
function testPaths() {
  const testCases = [
    'C:\\Program Files\\MyApp\\resources',
    'C:/Program Files/MyApp/resources',
    '/usr/local/bin/app',
    './relative/path',
    '../parent/path'
  ];
  
  console.log('路徑處理測試：');
  testCases.forEach(p => {
    console.log(`原始: ${p}`);
    console.log(`標準化: ${p.replace(/\\\\/g, '/')}`);
    console.log(`path.join: ${path.join(p, 'test.py')}`);
    console.log('---');
  });
}

testPaths();
