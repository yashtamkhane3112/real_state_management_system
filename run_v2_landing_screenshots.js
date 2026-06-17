const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const base = 'http://127.0.0.1:8000';
  const outDir = path.join(__dirname, 'screenshots', 'v2-landing');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const viewports = [
    { name: '1920', width: 1920, height: 1080 },
    { name: '1440', width: 1440, height: 900 },
    { name: '1366', width: 1366, height: 768 },
    { name: 'tablet-768', width: 768, height: 1024 },
    { name: 'mobile-390', width: 390, height: 844 },
  ];

  for (const vp of viewports) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 20000 });
    // Wait for loading overlay to disappear
    try {
      await page.waitForSelector('#pv-loader', { state: 'hidden', timeout: 8000 });
    } catch(e) {}
    await page.waitForTimeout(1500);

    // Slow scroll through the page to trigger IntersectionObserver reveals
    await page.evaluate(async () => {
      const delay = ms => new Promise(r => setTimeout(r, ms));
      const totalH = document.body.scrollHeight;
      const step = 300;
      for (let y = 0; y < totalH; y += step) {
        window.scrollTo({ top: y, behavior: 'instant' });
        await delay(180);
      }
      // Scroll back to top for hero shot
      window.scrollTo({ top: 0, behavior: 'instant' });
      await delay(600);
    });
    await page.waitForTimeout(1200);

    // Hero screenshot (above the fold)
    await page.screenshot({ path: path.join(outDir, `hero-${vp.name}.png`), fullPage: false });
    console.log(`[HERO] ${vp.name} ✓`);

    // Full page scroll screenshot
    await page.screenshot({ path: path.join(outDir, `fullpage-${vp.name}.png`), fullPage: true });
    console.log(`[FULL] ${vp.name} ✓`);

    await page.close();
  }

  await browser.close();
  console.log('All screenshots done.');
})();
