// PropVista — Navbar Redesign Playwright Validation
// Run: node run_navbar_screenshots.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT_DIR = path.join(__dirname, 'screenshots', 'navbar_redesign');
fs.mkdirSync(OUT_DIR, { recursive: true });

const BASE_URL = 'http://127.0.0.1:8000';

const VIEWPORTS = [
  { name: '1920x1080', width: 1920, height: 1080 },
  { name: '1440x900',  width: 1440, height: 900  },
  { name: '1366x768',  width: 1366, height: 768  },
  { name: '768x1024',  width: 768,  height: 1024 },
  { name: '390x844',   width: 390,  height: 844  },
];

const PAGES = [
  { name: 'home',       path: '/' },
  { name: 'properties', path: '/properties/' },
];

async function takeScreenshots() {
  const browser = await chromium.launch({ headless: true });
  const results = [];

  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
    });
    const page = await ctx.newPage();

    for (const pg of PAGES) {
      const url = BASE_URL + pg.path;
      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
        await page.waitForTimeout(800);

        // At-top screenshot
        const fname = `${pg.name}_${vp.name}_top.png`;
        const fpath = path.join(OUT_DIR, fname);
        await page.screenshot({ path: fpath, fullPage: false });

        // Scrolled screenshot
        await page.evaluate(() => window.scrollBy(0, 400));
        await page.waitForTimeout(400);
        const fnamedScrolled = `${pg.name}_${vp.name}_scrolled.png`;
        const fpathScrolled = path.join(OUT_DIR, fnamedScrolled);
        await page.screenshot({ path: fpathScrolled, fullPage: false });

        // Check for overflow
        const hasOverflow = await page.evaluate(() => {
          const body = document.body;
          return body.scrollWidth > window.innerWidth;
        });

        // Check navbar sticky position
        const navbarTop = await page.evaluate(() => {
          const nav = document.querySelector('[data-navbar]');
          if (!nav) return null;
          return nav.getBoundingClientRect().top;
        });

        results.push({
          page: pg.name, viewport: vp.name,
          status: 'OK',
          hasHorizontalOverflow: hasOverflow,
          navbarStickyTop: navbarTop,
          screenshots: [fname, fnamedScrolled],
        });
        console.log(`✓ ${pg.name} @ ${vp.name}`);
      } catch (err) {
        results.push({ page: pg.name, viewport: vp.name, status: 'ERROR', error: err.message });
        console.error(`✗ ${pg.name} @ ${vp.name}: ${err.message}`);
      }
    }
    await ctx.close();
  }

  await browser.close();
  return results;
}

takeScreenshots().then(results => {
  fs.writeFileSync(
    path.join(OUT_DIR, 'results.json'),
    JSON.stringify(results, null, 2)
  );
  console.log('\nDone. Results saved to screenshots/navbar_redesign/results.json');
  const errors = results.filter(r => r.status === 'ERROR');
  const overflows = results.filter(r => r.hasHorizontalOverflow);
  console.log(`\nSummary: ${results.length - errors.length}/${results.length} passed`);
  if (overflows.length) console.log(`⚠ Overflow detected: ${overflows.map(r=>r.page+'@'+r.viewport).join(', ')}`);
  if (errors.length) console.log(`✗ Errors: ${errors.map(e=>e.page+'@'+e.viewport).join(', ')}`);
}).catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
