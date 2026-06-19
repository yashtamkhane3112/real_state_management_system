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
    console.log('Navigating to http://127.0.0.1:8000/properties/...');
    await page.goto('http://127.0.0.1:8000/properties/', { waitUntil: 'networkidle', timeout: 15000 });
    
    // Wait for pv-loader to hide if present
    try {
      await page.waitForSelector('#pv-loader', { state: 'hidden', timeout: 5000 });
    } catch (e) {}

    await page.waitForTimeout(2000);

    // Capture screenshot of the properties list page
    const screenshotPath = path.resolve(__dirname, '..', 'scratch', 'properties_page.png');
    await page.screenshot({ path: screenshotPath });
    console.log(`Properties page screenshot captured at: ${screenshotPath}`);

    // Verify properties list rendering
    const cards = await page.$$('.property-card-premium');
    console.log(`Found ${cards.length} property card(s) on the listing page.`);

    // Verify all property card images have loaded successfully (none have opacity 0 or are missing class 'is-loaded')
    const unLoadedImagesCount = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('.property-media img'));
      return imgs.filter(img => !img.classList.contains('is-loaded')).length;
    });

    if (unLoadedImagesCount > 0) {
      console.warn(`⚠️ Warning: ${unLoadedImagesCount} image(s) do not have the 'is-loaded' class.`);
    } else {
      console.log(`✓ All property card images loaded successfully.`);
    }

    if (consoleErrors.length > 0) {
      console.error(`❌ Console errors detected:`);
      consoleErrors.forEach(e => console.error(`   - ${e}`));
      process.exit(1);
    } else {
      console.log(`✓ No console errors.`);
    }

    if (missingAssets.length > 0) {
      console.error(`❌ Missing local assets (404s/500s):`);
      missingAssets.forEach(a => console.error(`   - ${a}`));
      process.exit(1);
    } else {
      console.log(`✓ No missing local assets.`);
    }

    console.log(`🎉 Properties page validation passed successfully!`);

  } catch (err) {
    console.error('❌ Validation failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
