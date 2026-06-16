const playwright = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:8000';
const OUT_DIR = 'C:/Users/lenovo/.gemini/antigravity-cli/brain/0cb06c49-7fa4-478d-8b85-012236322047/screenshots';

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

async function captureResponsive(browser, pathUrl, name, contextOptions = {}) {
  const viewports = [
    { name: 'desktop_1920', width: 1920, height: 1080 },
    { name: 'desktop_1440', width: 1440, height: 900 },
    { name: 'desktop_1366', width: 1366, height: 768 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 }
  ];

  for (const vp of viewports) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 1,
      ...contextOptions
    });
    const page = await context.newPage();
    try {
      console.log(`Navigating to ${pathUrl} on ${vp.name}...`);
      await page.goto(`${BASE_URL}${pathUrl}`, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(2000); // Wait for animations
      
      const fileOut = path.join(OUT_DIR, `${name}_${vp.name}.png`);
      await page.screenshot({ path: fileOut, fullPage: true });
      console.log(`Captured ${name}_${vp.name}.png`);
    } catch (e) {
      console.error(`Failed to capture ${name} (${vp.name}): ${e.message}`);
    }
    await context.close();
  }
}

(async () => {
  console.log('Starting visual validation script for targeted refinement pass...');
  const browser = await playwright.chromium.launch({ headless: true });

  try {
    // 1. Capture public homepage responsively
    await captureResponsive(browser, '/', 'home');

    // 2. Authenticate and capture notifications page responsively
    console.log('Logging in as buyer to validate notifications...');
    const authContext = await browser.newContext({
      viewport: { width: 1440, height: 900 }
    });
    const authPage = await authContext.newPage();
    await authPage.goto(`${BASE_URL}/accounts/login/`, { waitUntil: 'networkidle' });
    await authPage.fill('input[name="username"]', 'buyer');
    await authPage.fill('input[name="password"]', 'Pass@12345');
    await authPage.click('form button.pv-btn-primary');
    await authPage.waitForLoadState('networkidle');

    // Reuse cookies by sharing context storage
    const storageState = await authContext.storageState();
    await authContext.close();

    // Capture /notifications/
    await captureResponsive(browser, '/notifications/', 'notifications', { storageState });

  } catch (e) {
    console.error('Critical error in validation script:', e.message);
  } finally {
    await browser.close();
    console.log('Visual validation script finished.');
  }
})();
