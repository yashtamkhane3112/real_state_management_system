const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  const consoleErrors = [];
  const missingAssets = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  page.on('pageerror', err => {
    consoleErrors.push(err.toString());
  });

  page.on('response', response => {
    const status = response.status();
    const url = response.url();
    if (status >= 400 && url.includes('127.0.0.1')) {
      missingAssets.push(`${status}: ${url}`);
    }
  });

  try {
    console.log('Navigating to http://127.0.0.1:8000/...');
    await page.goto('http://127.0.0.1:8000/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    
    // Wait for pv-loader to hide if present
    try {
      await page.waitForSelector('#pv-loader', { state: 'hidden', timeout: 5000 });
    } catch (e) {}

    await page.waitForTimeout(2000);

    const mode = await page.$eval('#landing-mode-config', el => el.getAttribute('data-mode'));
    console.log(`Detected Active Landing Media Mode: ${mode}`);

    // Take screenshot of the hero area
    const screenshotPath = path.resolve(__dirname, '..', 'scratch', `landing_${mode.toLowerCase()}.png`);
    await page.screenshot({ path: screenshotPath });
    console.log(`Hero screenshot captured at: ${screenshotPath}`);

    // Verify correct element is on the page
    if (mode === 'VIDEO_SCROLL_STORY') {
      const container = await page.$('#cinematic-container');
      const video = await page.$('#cinematic-video');
      if (!container || !video) throw new Error('VIDEO_SCROLL_STORY video elements not found in DOM');
    }

    if (consoleErrors.length > 0) {
      console.error(`❌ Console errors detected:`);
      consoleErrors.forEach(e => console.error(`   - ${e}`));
      process.exit(1);
    } else {
      console.log(`✓ No console errors.`);
    }

    if (missingAssets.length > 0) {
      console.error(`❌ Missing local assets:`);
      missingAssets.forEach(a => console.error(`   - ${a}`));
      process.exit(1);
    } else {
      console.log(`✓ No missing local assets.`);
    }

    console.log(`🎉 Validation of active mode ${mode} passed successfully!`);

  } catch (err) {
    console.error('❌ Validation failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
