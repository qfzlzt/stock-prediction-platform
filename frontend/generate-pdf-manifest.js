const fs = require('fs');
const path = require('path');

// 脚本放在项目根目录
const PDFS_DIR = path.join(__dirname, 'public', 'pdfs');
const OUTPUT_FILE = path.join(PDFS_DIR, 'pdf-manifest.json');

function isPdf(filename) {
  return filename.toLowerCase().endsWith('.pdf');
}

function normalizeReportType(filename) {
  const name = filename.replace(/\.pdf$/i, '').trim();

  // 先判断半年报，避免“半年度”被“年度”误判成年报
  if (/半年度|半年报|中报|半年(?:度)?报告|Q2/i.test(name)) {
    return '半年度报告';
  }

  if (/第一季度|一季报|第一季度报告|\bQ1\b/i.test(name)) {
    return '第一季度报告';
  }

  if (/第三季度|三季报|第三季度报告|\bQ3\b/i.test(name)) {
    return '第三季度报告';
  }

  if (
    /年报|年度报告|年度(?:报表|财报)?/i.test(name) &&
    !/半年度|半年报|中报|半年(?:度)?报告/i.test(name)
  ) {
    return '年报';
  }

  if (/技术分析/i.test(name)) {
    return '技术分析报告';
  }
  if (/基本面分析/i.test(name)) {
    return '基本面分析报告';
  }
  if (/风险评估/i.test(name)) {
    return '风险评估报告';
  }
  if (/策略回测|回测/i.test(name)) {
    return '策略回测报告';
  }
  if (/分析报告/i.test(name)) {
    return '分析报告';
  }

  return '未分类报告';
}

function extractYear(filename) {
  const match = filename.match(/(20\d{2})/);
  return match ? match[1] : '';
}

// 扫描 pdfs 下的所有子目录
function scanFolder(folderName) {
  const folderPath = path.join(PDFS_DIR, folderName);

  if (!fs.existsSync(folderPath)) {
    return [];
  }

  const stat = fs.statSync(folderPath);
  if (!stat.isDirectory()) {
    return [];
  }

  const entries = fs.readdirSync(folderPath, { withFileTypes: true });

  return entries
    .filter(entry => entry.isFile() && isPdf(entry.name))
    .map(entry => {
      const relativePath = path.posix.join(
        'pdfs',
        encodeURIComponent(folderName),
        encodeURIComponent(entry.name)
      );

      return {
        stockName: folderName,
        fileName: entry.name,
        reportType: normalizeReportType(entry.name),
        year: extractYear(entry.name),
        relativePath,
        url: '/' + relativePath
      };
    });
}

function generateManifest() {
  if (!fs.existsSync(PDFS_DIR)) {
    console.error('目录不存在：' + PDFS_DIR);
    process.exit(1);
  }

  const folders = fs.readdirSync(PDFS_DIR, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => entry.name)
    .filter(name => name !== 'icons' && name !== 'images'); // 可按需排除无关目录

  const manifest = folders.flatMap(scanFolder);

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(manifest, null, 2), 'utf-8');

  console.log(`已生成 ${manifest.length} 条记录`);
  console.log(`输出文件：${OUTPUT_FILE}`);
}

generateManifest();