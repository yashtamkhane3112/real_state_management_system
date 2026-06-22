const playwright = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:8000';
const OUT_DIR = 'C:/Users/lenovo/.gemini/antigravity-cli/brain/7ae3881f-8786-4b92-9140-0d4fb26d0844/screenshots';

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

async function captureResponsive(browser, pathUrl, name) {
  const viewports = [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 }
  ];

  for (const vp of viewports) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 1
    });
    const page = await context.newPage();
    try {
      await page.goto(`${BASE_URL}${pathUrl}`, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(2500); // Allow any animations to settle
      const fileOut = path.join(OUT_DIR, `${name}_${vp.name}.png`);
      await page.screenshot({ path: fileOut, fullPage: true });
      console.log(`Captured ${name} (${vp.name}) -> ${fileOut}`);
    } catch (e) {
      console.error(`Failed to capture ${name} (${vp.name}): ${e.message}`);
    }
    await context.close();
  }
}

async function captureAuthenticated(browser, role, name) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();
  try {
    // Log in using demo logins
    console.log(`Logging in as ${role}...`);
    await page.goto(`${BASE_URL}/accounts/login/`, { waitUntil: 'networkidle' });
    await page.fill('input[name="username"]', role);
    await page.fill('input[name="password"]', 'Pass@12345');
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');
    
    // Go to dashboard
    await page.goto(`${BASE_URL}/accounts/dashboard/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500); // wait for Chart.js rendering
    const fileOut = path.join(OUT_DIR, `${name}_desktop.png`);
    await page.screenshot({ path: fileOut, fullPage: true });
    console.log(`Captured ${role} dashboard -> ${fileOut}`);
  } catch (e) {
    console.error(`Failed to capture ${role} dashboard: ${e.message}`);
  }
  await context.close();
}

(async () => {
  console.log('Starting screenshot QA script...');
  const browser = await playwright.chromium.launch({ headless: true });

  // 1. Capture public pages responsively
  await captureResponsive(browser, '/', 'home');
  await captureResponsive(browser, '/accounts/login/', 'login');
  await captureResponsive(browser, '/accounts/register/', 'register');

  // 2. Capture property list and detail
  const listContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const listPage = await listContext.newPage();
  try {
    await listPage.goto(`${BASE_URL}/properties/`, { waitUntil: 'networkidle' });
    await listPage.screenshot({ path: path.join(OUT_DIR, 'properties_list_desktop.png'), fullPage: true });
    console.log('Captured properties list');

    // Get the first property slug
    const firstSlug = await listPage.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a[href*="/properties/"]'));
      const prop = links.find(a => a.href.match(/\/properties\/[^/]+\/$/) && !a.href.includes('/new') && !a.href.includes('/city'));
      return prop ? prop.getAttribute('href') : null;
    });
    if (firstSlug) {
      await listPage.goto(`${BASE_URL}${firstSlug}`, { waitUntil: 'networkidle' });
      await listPage.screenshot({ path: path.join(OUT_DIR, 'property_detail_desktop.png'), fullPage: true });
      console.log(`Captured property detail for ${firstSlug}`);
    }
  } catch (e) {
    console.error(`Error in property navigation: ${e.message}`);
  }
  await listContext.close();

  // 3. Capture dashboards
  await captureAuthenticated(browser, 'buyer', 'buyer_dashboard');
  await captureAuthenticated(browser, 'seller', 'seller_dashboard');
  await captureAuthenticated(browser, 'agent', 'agent_dashboard');
  await captureAuthenticated(browser, 'admin', 'admin_dashboard');

  await browser.close();
  console.log('Screenshot QA completed.');
})();
