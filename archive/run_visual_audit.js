const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');
const playwright = require('playwright');

const BASE_URL = 'http://127.0.0.1:8000';
const OUT_DIR = 'C:/Users/lenovo/.gemini/antigravity-cli/brain/a38b5cc7-f912-441a-8e64-ce0c4cc1dc79/screenshots';

// Ensure output directory exists
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

function startServer() {
  return new Promise((resolve, reject) => {
    console.log('Starting Django development server...');
    const server = spawn('..\\venv\\Scripts\\python.exe', ['..\\manage.py', 'runserver', '8000'], {
      cwd: 'E:\\PropVista_Final',
      shell: true
    });
    
    server.stdout.on('data', (data) => {
      // console.log(`Django: ${data}`);
    });
    server.stderr.on('data', (data) => {
      // console.log(`Django Error: ${data}`);
    });

    let attempts = 0;
    const poll = setInterval(() => {
      attempts++;
      http.get('http://127.0.0.1:8000/', (res) => {
        console.log('Django server responded! Starting Playwright...');
        clearInterval(poll);
        resolve(server);
      }).on('error', (err) => {
        if (attempts > 30) {
          clearInterval(poll);
          server.kill();
          reject(new Error('Django server failed to start within 30 seconds.'));
        }
      });
    }, 1000);
  });
}

async function runAudit() {
  let serverProcess;
  try {
    serverProcess = await startServer();
  } catch (e) {
    console.error(e);
    process.exit(1);
  }

  const browser = await playwright.chromium.launch({ headless: true });
  const breakpoints = [
    { name: '320px', width: 320, height: 568 },
    { name: '375px', width: 375, height: 667 },
    { name: '768px', width: 768, height: 1024 },
    { name: '1024px', width: 1024, height: 768 },
    { name: '1440px', width: 1440, height: 900 }
  ];

  const results = {
    pages: {},
    errors: [],
    overflows: []
  };

  async function checkOverflow(page, pageName, vpName) {
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });
    if (hasHorizontalScroll) {
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const windowWidth = await page.evaluate(() => window.innerWidth);
      results.overflows.push(`${pageName} (${vpName}) has horizontal overflow: scrollWidth=${scrollWidth}, innerWidth=${windowWidth}`);
    }
  }

  try {
    // 1. Audit Public Pages
    const publicPages = [
      { name: 'homepage', url: '/' },
      { name: 'properties_list', url: '/properties/' }
    ];

    for (const p of publicPages) {
      console.log(`Auditing ${p.name}...`);
      for (const bp of breakpoints) {
        const context = await browser.newContext({ viewport: { width: bp.width, height: bp.height } });
        const page = await context.newPage();
        try {
          await page.goto(`${BASE_URL}${p.url}`, { waitUntil: 'networkidle', timeout: 15000 });
          await page.waitForTimeout(1000);
          const screenshotPath = path.join(OUT_DIR, `${p.name}_${bp.name}.png`);
          await page.screenshot({ path: screenshotPath, fullPage: true });
          await checkOverflow(page, p.name, bp.name);
        } catch (e) {
          results.errors.push(`Error on ${p.name} (${bp.name}): ${e.message}`);
        }
        await context.close();
      }
    }

    // 2. Audit Property Detail Page (get first property slug from list page)
    console.log('Auditing Property Detail Page...');
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    let detailUrl = null;
    try {
      await page.goto(`${BASE_URL}/properties/`, { waitUntil: 'networkidle' });
      detailUrl = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a[href*="/properties/"]'));
        const propLink = links.find(a => a.href.match(/\/properties\/[^/]+\/$/) && !a.href.includes('/new') && !a.href.includes('/city'));
        return propLink ? propLink.getAttribute('href') : null;
      });
    } catch (e) {
      results.errors.push(`Failed to fetch property slug: ${e.message}`);
    }
    await context.close();

    if (detailUrl) {
      console.log(`Found property detail URL: ${detailUrl}. Auditing detail page...`);
      for (const bp of breakpoints) {
        const dContext = await browser.newContext({ viewport: { width: bp.width, height: bp.height } });
        const dPage = await dContext.newPage();
        try {
          // Log in as buyer so inquiries form is visible
          await dPage.goto(`${BASE_URL}/accounts/demo/buyer/`, { waitUntil: 'networkidle' });
          await dPage.goto(`${BASE_URL}${detailUrl}`, { waitUntil: 'networkidle', timeout: 20000 });
          await dPage.waitForTimeout(1000);
          const screenshotPath = path.join(OUT_DIR, `property_detail_${bp.name}.png`);
          await dPage.screenshot({ path: screenshotPath, fullPage: true });
          await checkOverflow(dPage, 'property_detail', bp.name);

          // Verify elements presence on Desktop
          if (bp.width === 1440) {
            const hasGallery = await dPage.locator('.grid-left-gallery').count();
            const hasNarrative = await dPage.locator('.grid-left-narrative').count();
            const hasLifecycle = await dPage.locator('.grid-left-lifecycle').count();
            const hasSidebar = await dPage.locator('.grid-right-sidebar').count();
            const hasAmenities = await dPage.locator('.grid-left-amenities').count();
            const hasLocation = await dPage.locator('.grid-left-location').count();
            const hasSimilar = await dPage.locator('.grid-left-similar').count();

            console.log(`Detail elements: Gallery=${hasGallery}, Narrative=${hasNarrative}, Lifecycle=${hasLifecycle}, Sidebar=${hasSidebar}, Amenities=${hasAmenities}, Location=${hasLocation}, Similar=${hasSimilar}`);
          }
        } catch (e) {
          results.errors.push(`Error on property_detail (${bp.name}): ${e.message}`);
        }
        await dContext.close();
      }
    } else {
      results.errors.push('No property detail URL found during list scan.');
    }

    // 3. Audit Buyer Dashboard & Pages (Favorites, Notifications, Profile)
    console.log('Auditing Buyer views...');
    for (const bp of breakpoints) {
      const bContext = await browser.newContext({ viewport: { width: bp.width, height: bp.height } });
      const bPage = await bContext.newPage();
      try {
        await bPage.goto(`${BASE_URL}/accounts/demo/buyer/`, { waitUntil: 'networkidle' });
        
        // Buyer Dashboard
        await bPage.goto(`${BASE_URL}/accounts/dashboard/buyer/`, { waitUntil: 'networkidle' });
        await bPage.waitForTimeout(1000);
        await bPage.screenshot({ path: path.join(OUT_DIR, `buyer_dashboard_${bp.name}.png`), fullPage: true });
        await checkOverflow(bPage, 'buyer_dashboard', bp.name);

        if (bp.width === 1440) {
          // Favorites
          await bPage.goto(`${BASE_URL}/favorites/`, { waitUntil: 'networkidle' });
          await bPage.screenshot({ path: path.join(OUT_DIR, `favorites_${bp.name}.png`), fullPage: true });
          await checkOverflow(bPage, 'favorites', bp.name);

          // Notifications
          await bPage.goto(`${BASE_URL}/notifications/`, { waitUntil: 'networkidle' });
          await bPage.screenshot({ path: path.join(OUT_DIR, `notifications_${bp.name}.png`), fullPage: true });
          await checkOverflow(bPage, 'notifications', bp.name);

          // Profile
          await bPage.goto(`${BASE_URL}/accounts/profile/`, { waitUntil: 'networkidle' });
          await bPage.screenshot({ path: path.join(OUT_DIR, `profile_${bp.name}.png`), fullPage: true });
          await checkOverflow(bPage, 'profile', bp.name);
        }
      } catch (e) {
        results.errors.push(`Error on Buyer views (${bp.name}): ${e.message}`);
      }
      await bContext.close();
    }

    // 4. Audit Seller Dashboard & Reports
    console.log('Auditing Seller views...');
    for (const bp of breakpoints) {
      const sContext = await browser.newContext({ viewport: { width: bp.width, height: bp.height } });
      const sPage = await sContext.newPage();
      try {
        await sPage.goto(`${BASE_URL}/accounts/demo/seller/`, { waitUntil: 'networkidle' });
        
        // Seller Dashboard
        await sPage.goto(`${BASE_URL}/accounts/dashboard/seller/`, { waitUntil: 'networkidle' });
        await sPage.waitForTimeout(1000);
        await sPage.screenshot({ path: path.join(OUT_DIR, `seller_dashboard_${bp.name}.png`), fullPage: true });
        await checkOverflow(sPage, 'seller_dashboard', bp.name);

        if (bp.width === 1440) {
          // Reports page
          await sPage.goto(`${BASE_URL}/reports/`, { waitUntil: 'networkidle' });
          await sPage.waitForTimeout(1000); // Wait for Chart rendering
          await sPage.screenshot({ path: path.join(OUT_DIR, `reports_${bp.name}.png`), fullPage: true });
          await checkOverflow(sPage, 'reports', bp.name);
        }
      } catch (e) {
        results.errors.push(`Error on Seller views (${bp.name}): ${e.message}`);
      }
      await sContext.close();
    }

    // 5. Audit Admin Dashboard
    console.log('Auditing Admin views...');
    for (const bp of breakpoints) {
      const aContext = await browser.newContext({ viewport: { width: bp.width, height: bp.height } });
      const aPage = await aContext.newPage();
      try {
        await aPage.goto(`${BASE_URL}/accounts/demo/admin/`, { waitUntil: 'networkidle' });
        
        // Admin Dashboard
        await aPage.goto(`${BASE_URL}/accounts/dashboard/admin/`, { waitUntil: 'networkidle' });
        await aPage.waitForTimeout(1000);
        await aPage.screenshot({ path: path.join(OUT_DIR, `admin_dashboard_${bp.name}.png`), fullPage: true });
        await checkOverflow(aPage, 'admin_dashboard', bp.name);
      } catch (e) {
        results.errors.push(`Error on Admin views (${bp.name}): ${e.message}`);
      }
      await aContext.close();
    }

  } catch (err) {
    console.error('Audit encountered unexpected error:', err);
  } finally {
    await browser.close();
    console.log('Stopping Django server...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
    } else {
      serverProcess.kill('SIGINT');
    }
    console.log('Audit completed.');
    console.log('Errors:', results.errors);
    console.log('Overflows:', results.overflows);
  }
}

runAudit();
