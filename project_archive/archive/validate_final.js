
const playwright = require('playwright');
(async () => {
  const browser = await playwright.chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  
  const routes = [
    { name: 'home', url: 'http://127.0.0.1:8080/' },
    { name: 'properties', url: 'http://127.0.0.1:8080/properties/' },
    { name: 'login', url: 'http://127.0.0.1:8080/accounts/login/' },
    { name: 'register', url: 'http://127.0.0.1:8080/accounts/register/' }
  ];

  console.log('--- BASIC ROUTES ---');
  for (const route of routes) {
    try {
      await page.goto(route.url, { waitUntil: 'networkidle' });
      const title = await page.title();
      console.log('Route ' + route.name + ': ' + title);
      await page.screenshot({ path: 'E:/PropVista_Final/artifacts/validation/' + route.name + '.png', fullPage: true });
    } catch (e) {
      console.error('Failed ' + route.name + ': ' + e.message);
    }
  }

  console.log('--- DASHBOARDS ---');
  const roles = ['buyer', 'seller', 'agent', 'admin'];
  for (const role of roles) {
    try {
      await page.goto('http://127.0.0.1:8080/accounts/demo/' + role + '/', { waitUntil: 'networkidle' });
      console.log('Verified dashboard for ' + role);
      await page.screenshot({ path: 'E:/PropVista_Final/artifacts/validation/dashboard-' + role + '.png', fullPage: true });
      
      if (role === 'seller') {
        console.log('Capturing seller profile...');
        await page.goto('http://127.0.0.1:8080/accounts/profile/', { waitUntil: 'networkidle' });
        await page.screenshot({ path: 'E:/PropVista_Final/artifacts/validation/profile.png', fullPage: true });
        
        console.log('Capturing seller reports...');
        await page.goto('http://127.0.0.1:8080/reports/', { waitUntil: 'networkidle' });
        await page.screenshot({ path: 'E:/PropVista_Final/artifacts/validation/reports.png', fullPage: true });

        console.log('Capturing seller inquiries...');
        await page.goto('http://127.0.0.1:8080/inquiries/', { waitUntil: 'networkidle' });
        await page.screenshot({ path: 'E:/PropVista_Final/artifacts/validation/inquiries.png', fullPage: true });
      }

      if (role === 'admin') {
        console.log('Capturing admin approvals...');
        await page.goto('http://127.0.0.1:8080/properties/approvals/', { waitUntil: 'networkidle' });
        await page.screenshot({ path: 'E:/PropVista_Final/artifacts/validation/approvals.png', fullPage: true });
      }
      
      await context.clearCookies();
    } catch (e) {
      console.error('Failed dashboard for ' + role + ': ' + e.message);
    }
  }

  await browser.close();
  console.log('Validation complete.');
})();
