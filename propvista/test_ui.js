const { chromium } = require('playwright');
const path = require('path');
const EXECUTABLE = path.join(process.env.HOME, '.cache/ms-playwright/chromium-1223/chrome-linux64/chrome');
const OUT = '/home/diggerpunk/.gemini/antigravity-cli/brain/ee2540f0-ee67-4023-a748-bd2ed50f52d4/';
const BASE = 'http://localhost:8080';

async function shot(page, url, name) {
  try {
    await page.goto(BASE + url, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: OUT + name + '.png', fullPage: true });
    const title = await page.title();
    console.log('✓ ' + name + ' | ' + title);
  } catch(e) {
    console.log('✗ ' + name + ':', e.message.split('\n')[0]);
  }
}

async function loginAs(page, username, password) {
  await page.context().clearCookies();
  await page.goto(BASE + '/accounts/login/', { waitUntil: 'networkidle' });
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForLoadState('networkidle');
  console.log('Logged in as', username, '→', page.url());
}



(async () => {
  const browser = await chromium.launch({ executablePath: EXECUTABLE });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  // --- PUBLIC PAGES ---
  console.log('\n=== PUBLIC PAGES ===');
  await shot(page, '/', 'sc_home');
  await shot(page, '/properties/', 'sc_properties_list');
  await shot(page, '/accounts/login/', 'sc_login');
  await shot(page, '/accounts/register/', 'sc_register');
  await shot(page, '/api/docs/', 'sc_api_docs');

  // Get the first property slug for detail page
  await page.goto(BASE + '/properties/', { waitUntil: 'networkidle' });
  const firstSlug = await page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href*="/properties/"]'));
    const prop = links.find(a => a.href.match(/\/properties\/[^/]+\/$/) && !a.href.includes('/new') && !a.href.includes('/city'));
    return prop ? prop.getAttribute('href') : null;
  });
  if (firstSlug) {
    await shot(page, firstSlug, 'sc_property_detail');
  } else {
    console.log('✗ No property slug found');
  }

  // --- BUYER DASHBOARD ---
  console.log('\n=== BUYER PAGES ===');
  await loginAs(page, 'buyer', 'Pass@12345');
  await shot(page, '/accounts/dashboard/', 'sc_buyer_dashboard');
  await shot(page, '/accounts/profile/', 'sc_profile');
  await shot(page, '/favorites/', 'sc_wishlist');
  await shot(page, '/search/', 'sc_saved_searches');
  await shot(page, '/notifications/', 'sc_notifications');
  

  // --- SELLER DASHBOARD ---
  console.log('\n=== SELLER PAGES ===');
  await loginAs(page, 'seller', 'Pass@12345');
  await shot(page, '/accounts/dashboard/', 'sc_seller_dashboard');
  await shot(page, '/properties/new/', 'sc_property_add');
  await shot(page, '/reports/', 'sc_reports');
  

  // --- AGENT DASHBOARD ---
  console.log('\n=== AGENT PAGES ===');
  await loginAs(page, 'agent', 'Pass@12345');
  await shot(page, '/accounts/dashboard/', 'sc_agent_dashboard');
  await shot(page, '/leads/', 'sc_leads');
  

  // --- ADMIN DASHBOARD ---
  console.log('\n=== ADMIN PAGES ===');
  await loginAs(page, 'admin', 'Pass@12345');
  await shot(page, '/accounts/dashboard/', 'sc_admin_dashboard');
  await shot(page, '/ai/', 'sc_ai_tools');


  await browser.close();
  console.log('\n✅ All done!');
})();
