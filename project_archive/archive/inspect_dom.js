const { spawn } = require('child_process');
const http = require('http');
const playwright = require('playwright');

const BASE_URL = 'http://127.0.0.1:8000';

function startServer() {
  return new Promise((resolve, reject) => {
    console.log('Starting Django development server...');
    const server = spawn('..\\venv\\Scripts\\python.exe', ['..\\manage.py', 'runserver', '8000'], {
      cwd: 'E:\\PropVista_Final',
      shell: true
    });
    
    let attempts = 0;
    const poll = setInterval(() => {
      attempts++;
      http.get('http://127.0.0.1:8000/', (res) => {
        console.log('Django server responded! Starting Playwright inspection...');
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

async function inspectDOM() {
  let serverProcess;
  try {
    serverProcess = await startServer();
  } catch (e) {
    console.error(e);
    process.exit(1);
  }

  const browser = await playwright.chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  try {
    // Get property slug from properties list
    console.log('Fetching first property details link...');
    await page.goto(`${BASE_URL}/properties/`, { waitUntil: 'networkidle' });
    const detailUrl = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a[href*="/properties/"]'));
      const propLink = links.find(a => a.href.match(/\/properties\/[^/]+\/$/) && !a.href.includes('/new') && !a.href.includes('/city'));
      return propLink ? propLink.getAttribute('href') : null;
    });

    if (!detailUrl) {
      throw new Error('No property detail URL found on the list page.');
    }

    console.log(`Navigating to property page: ${detailUrl}`);
    // Log in as buyer
    await page.goto(`${BASE_URL}/accounts/demo/buyer/`, { waitUntil: 'networkidle' });
    await page.goto(`${BASE_URL}${detailUrl}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Inspect the DOM elements and print major containers and their class names
    console.log('\n--- INSPECTING DOM CONTAINERS ---');
    const elementsInfo = await page.evaluate(() => {
      const info = [];
      
      // Look for the main layout row and its children
      const gridRows = document.querySelectorAll('.detail-grid-row, .detail-grid-row-bottom');
      gridRows.forEach((row, rIdx) => {
        info.push(`Grid Row #${rIdx + 1}: class="${row.className}"`);
        Array.from(row.children).forEach((child, cIdx) => {
          info.push(`  Child #${cIdx + 1}: <${child.tagName.toLowerCase()}> class="${child.className}"`);
          // Let's list some children of the child
          Array.from(child.children).forEach((subChild) => {
            const heading = subChild.querySelector('h1, h2, h3');
            const headingText = heading ? ` (${heading.tagName.toLowerCase()}: "${heading.textContent.trim().replace(/\s+/g, ' ')}")` : '';
            info.push(`    Sub-child: <${subChild.tagName.toLowerCase()}> class="${subChild.className}"${headingText}`);
            
            // For sidebar aside and its cards
            if (subChild.tagName.toLowerCase() === 'aside') {
              Array.from(subChild.children).forEach(asideCard => {
                const asideHeading = asideCard.querySelector('h1, h2, h3');
                const asideHeadingText = asideHeading ? ` (${asideHeading.tagName.toLowerCase()}: "${asideHeading.textContent.trim().replace(/\s+/g, ' ')}")` : '';
                info.push(`      Aside Card: <${asideCard.tagName.toLowerCase()}> class="${asideCard.className}"${asideHeadingText}`);
              });
            }
          });
        });
      });
      return info;
    });

    elementsInfo.forEach(line => console.log(line));

    // Specifically test finding each section and printing their resolved selectors
    console.log('\n--- RESOLVING TARGET SELECTORS ---');
    const targetSelectors = await page.evaluate(() => {
      const results = {};
      
      // 1. Gallery
      const gallery = document.querySelector('.grid-left-gallery');
      results.gallery = gallery ? { selector: '.grid-left-gallery', found: true, classes: gallery.className } : { found: false };

      // 2. Narrative Section
      const narrative = document.querySelector('.grid-left-narrative');
      results.narrative = narrative ? { selector: '.grid-left-narrative', found: true, classes: narrative.className } : { found: false };

      // 3. Lifecycle Section
      const lifecycle = document.querySelector('.grid-left-lifecycle');
      results.lifecycle = lifecycle ? { selector: '.grid-left-lifecycle', found: true, classes: lifecycle.className } : { found: false };

      // 4. Sidebar Container
      const sidebar = document.querySelector('.grid-right-sidebar');
      results.sidebar = sidebar ? { selector: '.grid-right-sidebar', found: true, classes: sidebar.className } : { found: false };

      // 5. Finance Calculator
      const calculator = document.querySelector('.grid-sidebar-calculator');
      results.calculator = calculator ? { selector: '.grid-sidebar-calculator', found: true, classes: calculator.className } : { found: false };

      // 6. Inquiry Form
      const inquiry = document.querySelector('.grid-sidebar-inquiry');
      results.inquiry = inquiry ? { selector: '.grid-sidebar-inquiry', found: true, classes: inquiry.className } : { found: false };

      // 7. Amenities Section
      const amenities = document.querySelector('.grid-left-amenities');
      results.amenities = amenities ? { selector: '.grid-left-amenities', found: true, classes: amenities.className } : { found: false };

      // 8. Location Section
      const location = document.querySelector('.grid-left-location');
      results.location = location ? { selector: '.grid-left-location', found: true, classes: location.className } : { found: false };

      // 9. Similar Opportunities Section
      const similar = document.querySelector('.grid-left-similar');
      results.similar = similar ? { selector: '.grid-left-similar', found: true, classes: similar.className } : { found: false };

      return results;
    });

    console.log(JSON.stringify(targetSelectors, null, 2));

  } catch (err) {
    console.error('Inspection failed:', err);
  } finally {
    await browser.close();
    console.log('Stopping Django server...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
    } else {
      serverProcess.kill('SIGINT');
    }
    console.log('Inspection complete.');
  }
}

inspectDOM();
