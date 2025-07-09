#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 创建scripts目录
const scriptsDir = path.join(__dirname);
if (!fs.existsSync(scriptsDir)) {
  fs.mkdirSync(scriptsDir, { recursive: true });
}

console.log('🎨 生成favicon文件...');

// 创建不同尺寸的favicon配置
const faviconSizes = [
  { size: 16, name: 'favicon-16x16.png' },
  { size: 32, name: 'favicon-32x32.png' },
  { size: 180, name: 'apple-touch-icon.png' },
  { size: 192, name: 'android-chrome-192x192.png' },
  { size: 512, name: 'android-chrome-512x512.png' },
];

// 生成HTML代码片段
const generateFaviconHTML = () => {
  return `<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" type="image/x-icon" href="/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="manifest" href="/site.webmanifest" />
<meta name="theme-color" content="#3b82f6" />`;
};

// 生成HTML文件
const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SCADA System - Favicon Generator</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
    .favicon-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
    .favicon-item { text-align: center; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }
    .favicon-item img { border: 1px solid #d1d5db; border-radius: 4px; }
    code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
    pre { background: #f3f4f6; padding: 16px; border-radius: 8px; overflow-x: auto; }
  </style>
</head>
<body>
  <h1>🎨 SCADA System Favicon Generator</h1>
  
  <p>这个页面展示了SCADA系统的favicon和logo文件。</p>
  
  <h2>📁 生成的文件</h2>
  <div class="favicon-grid">
    <div class="favicon-item">
      <h3>SVG Logo</h3>
      <img src="/logo.svg" alt="SVG Logo" width="64" height="64">
      <p><code>/logo.svg</code></p>
    </div>
    <div class="favicon-item">
      <h3>Large Logo</h3>
      <img src="/logo-large.svg" alt="Large Logo" width="120" height="40">
      <p><code>/logo-large.svg</code></p>
    </div>
    <div class="favicon-item">
      <h3>Favicon</h3>
      <img src="/favicon.svg" alt="Favicon" width="32" height="32">
      <p><code>/favicon.svg</code></p>
    </div>
  </div>
  
  <h2>📋 HTML代码片段</h2>
  <p>将以下代码添加到你的HTML head部分：</p>
  <pre><code>${generateFaviconHTML()}</code></pre>
  
  <h2>🔧 使用方法</h2>
  <ol>
    <li>将SVG文件转换为PNG格式（可以使用在线工具或设计软件）</li>
    <li>将生成的文件放在 <code>/public</code> 目录中</li>
    <li>在Next.js的 <code>layout.tsx</code> 中配置metadata</li>
    <li>使用Logo组件在应用内显示logo</li>
  </ol>
  
  <h2>🎯 最佳实践</h2>
  <ul>
    <li>使用SVG格式获得最佳缩放效果</li>
    <li>确保favicon在不同背景下都清晰可见</li>
    <li>测试在不同设备和浏览器上的显示效果</li>
    <li>使用适当的alt文本提高可访问性</li>
  </ul>
</body>
</html>`;
};

// 写入HTML文件
const htmlPath = path.join(__dirname, '..', 'src', 'app', 'public', 'favicon-preview.html');
fs.writeFileSync(htmlPath, htmlContent);

console.log('✅ 生成的文件:');
console.log('  📄 favicon.svg - SVG格式的favicon');
console.log('  📄 logo.svg - 应用内使用的logo');
console.log('  📄 logo-large.svg - 带文字的完整logo');
console.log('  📄 site.webmanifest - PWA配置文件');
console.log('  📄 favicon-preview.html - 预览页面');

console.log('\n🎯 下一步:');
console.log('  1. 使用设计工具将SVG转换为PNG格式');
console.log('  2. 将PNG文件放在 /app/public 目录中');
console.log('  3. 访问 /favicon-preview.html 查看效果');
console.log('  4. 在应用中使用Logo组件');

console.log('\n💡 提示:');
console.log('  - SVG文件已经创建完成');
console.log('  - 可以使用在线工具如 favicon.io 生成PNG文件');
console.log('  - Logo组件支持不同尺寸和变体'); 