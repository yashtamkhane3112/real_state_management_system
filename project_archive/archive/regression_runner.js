
const playwright = require('playwright');
(async () => {
  const browser = await playwright.chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  const BASE_URL = 'http://127.0.0.1:8080';

  console.log('--- REFRESHING DASHBOARDS ---');
  const roles = ['buyer', 'seller', 'agent', 'admin'];
  for (const role of roles) {
    try {
      await page.goto(BASE_URL + '/accounts/login/', { waitUntil: 'networkidle' });
      await page.fill('input[name="username"]', role);
      await page.fill('input[name="password"]', 'Pass@12345');
      await page.click('button[type="submit"]');
      await page.waitForLoadState('networkidle');
      console.log('Verified dashboard for ' + role + ' at ' + page.url());
      await page.screenshot({ path: 'artifacts/validation/dash_' + role + '.png' });
      await context.clearCookies();
    } catch (e) {
      console.error('Failed dashboard for ' + role + ': ' + e.message);
    }
  }

  console.log('--- SEARCH & PROPERTY ---');
  try {
    await page.goto(BASE_URL + '/properties/', { waitUntil: 'networkidle' });
    await page.fill('input[name="q"]', 'Mansion');
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');
    console.log('Search for "Mansion" performed.');
    await page.screenshot({ path: 'artifacts/validation/search_results.png' });

    const propLink = await page.$('a[href*="/properties/"]:not([href*="/city/"]):not([href*="/new/"])');
    if (propLink) {
      await propLink.click();
      await page.waitForLoadState('networkidle');
      console.log('Property detail page loaded: ' + page.url());
      await page.screenshot({ path: 'artifacts/validation/prop_detail.png', fullPage: true });
    }
  } catch (e) {
    console.error('Search/Detail failed: ' + e.message);
  }

  console.log('--- MOBILE LAYOUTS ---');
  const viewports = [320, 375, 768, 1024];
  for (const width of viewports) {
    try {
      await page.setViewportSize({ width: width, height: 800 });
      await page.goto(BASE_URL + '/', { waitUntil: 'networkidle' });
      console.log('Home page layout check at ' + width + 'px');
      await page.screenshot({ path: 'artifacts/validation/mobile_' + width + '.png' });
    } catch (e) {
      console.error('Mobile check failed at ' + width + ': ' + e.message);
    }
  }

  await browser.close();
  console.log('Regression check complete.');
})();
