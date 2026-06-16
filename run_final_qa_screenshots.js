const playwright = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:8000';
const OUT_DIR = 'C:/Users/lenovo/.gemini/antigravity-cli/brain/0cb06c49-7fa4-478d-8b85-012236322047/screenshots/final_qa';

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

async function captureResponsive(browser, pathUrl, name, contextOptions = {}) {
  const viewports = [
    { name: '1920x1080', width: 1920, height: 1080 },
    { name: '1440x900', width: 1440, height: 900 },
    { name: '1366x768', width: 1366, height: 768 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 812 }
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
      await page.waitForTimeout(2500); // Wait for rendering/animations
      
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
  console.log('Starting final QA visual verification...');
  const browser = await playwright.chromium.launch({ headless: true });

  try {
    // 1. Capture public homepage
    await captureResponsive(browser, '/', 'home');

    // 2. Authenticate as admin to capture admin dashboard, users list, and reports
    console.log('Logging in as admin...');
    const authContext = await browser.newContext({
      viewport: { width: 1440, height: 900 }
    });
    const authPage = await authContext.newPage();
    await authPage.goto(`${BASE_URL}/accounts/login/`, { waitUntil: 'networkidle' });
    await authPage.fill('input[name="username"]', 'admin');
    await authPage.fill('input[name="password"]', 'Pass@12345');
    await authPage.click('form button.pv-btn-primary');
    await authPage.waitForLoadState('networkidle');

    // Reuse cookies
    const storageState = await authContext.storageState();
    await authContext.close();

    // 3. Capture admin-only pages
    await captureResponsive(browser, '/accounts/dashboard/admin/', 'admin_dashboard', { storageState });
    await captureResponsive(browser, '/accounts/dashboard/admin/users/', 'admin_users', { storageState });
    await captureResponsive(browser, '/reports/', 'reports', { storageState });
    await captureResponsive(browser, '/notifications/', 'notifications', { storageState });

  } catch (e) {
    console.error('Critical error in verification script:', e.message);
  } finally {
    await browser.close();
    console.log('Visual QA verification finished.');
  }
})();
