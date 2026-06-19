const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const imgDir = 'C:/Users/lenovo/Downloads/property_000';
  const outDir = path.resolve(__dirname, '..', 'static', 'images', 'temp_inspect');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  // Copy potential frames to static folder to load them in playwright
  const frames = ['000', '010', '020', '030', '040', '050', '060', '070', '080', '090', '099'];
  frames.forEach(f => {
    const src = path.join(imgDir, `property_${f}.jpg`);
    const dest = path.join(outDir, `property_${f}.jpg`);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
    }
  });

  // Create inspect.html
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { font-family: sans-serif; background: #081024; color: #fff; margin: 20px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .card { border: 1px solid #334155; padding: 10px; background: #1e293b; border-radius: 8px; }
        .card img { width: 100%; aspect-ratio: 16/9; object-fit: cover; border-radius: 4px; }
        .card-title { margin-top: 10px; font-weight: bold; text-align: center; }
      </style>
    </head>
    <body>
      <h1>Inspect Frames</h1>
      <div class="grid">
        ${frames.map(f => `
          <div class="card">
            <img src="file:///${path.join(outDir, `property_${f}.jpg`).replace(/\\/g, '/')}" />
            <div class="card-title">property_${f}.jpg</div>
          </div>
        `).join('')}
      </div>
    </body>
    </html>
  `;
  const htmlPath = path.join(__dirname, 'inspect.html');
  fs.writeFileSync(htmlPath, htmlContent);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1600 } });
  await page.goto(`file:///${htmlPath.replace(/\\/g, '/')}`);
  await page.waitForTimeout(2000);

  const screenshotPath = path.resolve(__dirname, '..', 'scratch', 'inspect_frames.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`Inspection screenshot generated at: ${screenshotPath}`);

  await browser.close();
  fs.unlinkSync(htmlPath);
})();
