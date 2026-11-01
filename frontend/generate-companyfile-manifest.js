const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(process.cwd(), 'public', 'pdfs', 'companyfile');
const OUTPUT_FILE = path.join(ROOT_DIR, 'pdf-manifest.json');

function isPdf(filename) {
  return filename.toLowerCase().endsWith('.pdf');
}

function extractYear(filename) {
  const match = filename.match(/(20\d{2})/);
  return match ? match[1] : '';
}

function scanCompanyFolder(companyFolderName) {
  const companyDir = path.join(ROOT_DIR, companyFolderName);
  const entries = fs.readdirSync(companyDir, { withFileTypes: true });

  return entries
    .filter(entry => entry.isFile() && isPdf(entry.name))
    .map(entry => {
      const relativePath = path.posix.join(
        'pdfs',
        'companyfile',
        encodeURIComponent(companyFolderName),
        encodeURIComponent(entry.name)
      );

      const url = '/' + relativePath;
      const year = extractYear(entry.name);

      return {
        id: `${companyFolderName}_${year}_${entry.name}`,
        stockName: companyFolderName,
        fileName: entry.name,
        year,
        relativePath,
        url
      };
    });
}

function generateManifest() {
  if (!fs.existsSync(ROOT_DIR)) {
    console.error('目录不存在：' + ROOT_DIR);
    process.exit(1);
  }

  const companyFolders = fs.readdirSync(ROOT_DIR, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => entry.name);

  const manifest = companyFolders.flatMap(scanCompanyFolder);

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(manifest, null, 2), 'utf-8');

  console.log(`已生成 ${manifest.length} 条记录`);
  console.log(`输出文件：${OUTPUT_FILE}`);
}

generateManifest();