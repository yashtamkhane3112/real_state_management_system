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
    
    let attempts = 0;
    const poll = setInterval(() => {
      attempts++;
      http.get('http://127.0.0.1:8000/', (res) => {
        console.log('Django server responded! Starting layout audit...');
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

async function runLayoutAudit() {
  let serverProcess;
  try {
    serverProcess = await startServer();
  } catch (e) {
    console.error(e);
    process.exit(1);
  }

  const browser = await playwright.chromium.launch({ headless: true });
  const viewports = [
    { name: '320px', width: 320, height: 568 },
    { name: '375px', width: 375, height: 667 },
    { name: '768px', width: 768, height: 1024 },
    { name: '1024px', width: 1024, height: 768 },
    { name: '1440px', width: 1440, height: 900 },
    { name: '1920px', width: 1920, height: 1080 }
  ];

  try {
    // 1. Get a property detail page link
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE_URL}/properties/`, { waitUntil: 'networkidle' });
    const detailUrl = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a[href*="/properties/"]'));
      const propLink = links.find(a => a.href.match(/\/properties\/[^/]+\/$/) && !a.href.includes('/new') && !a.href.includes('/city'));
      return propLink ? propLink.getAttribute('href') : null;
    });
    await context.close();

    if (!detailUrl) {
      throw new Error('No property detail slug found on list page.');
    }

    console.log(`Auditing property detail page: ${detailUrl}`);

    // Audit across all viewports
    for (const vp of viewports) {
      console.log(`\n=================== VIEWPORT: ${vp.name} (${vp.width}x${vp.height}) ===================`);
      const vpContext = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const vpPage = await vpContext.newPage();
      
      // Log in as demo buyer to ensure inquiry and calculator are visible
      await vpPage.goto(`${BASE_URL}/accounts/demo/buyer/`, { waitUntil: 'networkidle' });
      await vpPage.goto(`${BASE_URL}${detailUrl}`, { waitUntil: 'networkidle' });
      await vpPage.waitForTimeout(2000); // Allow any transitions/maps to initialize

      // Capture screenshot first as requested
      const screenshotName = `detail_layout_audit_${vp.name}.png`;
      const screenshotPath = path.join(OUT_DIR, screenshotName);
      await vpPage.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`Captured screenshot to: ${screenshotPath}`);

      // Perform measurements, overlaps, gaps, columns and clipping detection in page context
      const diagnostics = await vpPage.evaluate(() => {
        const selectors = {
          gallery: '.grid-left-gallery',
          narrative: '.grid-left-narrative',
          lifecycle: '.grid-left-lifecycle',
          sidebar: '.grid-right-sidebar',
          calculator: '.grid-sidebar-calculator',
          inquiry: '.grid-sidebar-inquiry',
          amenities: '.grid-left-amenities',
          location: '.grid-left-location',
          similar: '.grid-left-similar'
        };

        const elements = {};
        const logs = [];

        // Check counts & validate selectors
        logs.push('--- Selector Validation ---');
        for (const [key, selector] of Object.entries(selectors)) {
          const el = document.querySelector(selector);
          if (el) {
            const rect = el.getBoundingClientRect();
            // Store client coordinates relative to document scroll
            elements[key] = {
              selector,
              found: true,
              rect: {
                left: rect.left + window.scrollX,
                right: rect.right + window.scrollX,
                top: rect.top + window.scrollY,
                bottom: rect.bottom + window.scrollY,
                width: rect.width,
                height: rect.height
              },
              tagName: el.tagName.toLowerCase(),
              scrollWidth: el.scrollWidth,
              clientWidth: el.clientWidth,
              scrollHeight: el.scrollHeight,
              clientHeight: el.clientHeight
            };
            logs.push(`  [PASS] ${key} (${selector}): found 1 element`);
          } else {
            elements[key] = { selector, found: false };
            logs.push(`  [FAIL] ${key} (${selector}): NOT found`);
          }
        }

        // Measure Positions
        logs.push('\n--- Element Positions & Dimensions ---');
        for (const [key, info] of Object.entries(elements)) {
          if (info.found) {
            logs.push(`  ${key}: left=${info.rect.left.toFixed(1)}, top=${info.rect.top.toFixed(1)}, width=${info.rect.width.toFixed(1)}, height=${info.rect.height.toFixed(1)}`);
          }
        }

        // Detect Overlapping Boxes
        logs.push('\n--- Overlap Detection ---');
        const keys = Object.keys(elements).filter(k => elements[k].found);
        let overlapCount = 0;
        for (let i = 0; i < keys.length; i++) {
          for (let j = i + 1; j < keys.length; j++) {
            const k1 = keys[i];
            const k2 = keys[j];
            const r1 = elements[k1].rect;
            const r2 = elements[k2].rect;

            // Check if one is ancestor of another
            const el1 = document.querySelector(elements[k1].selector);
            const el2 = document.querySelector(elements[k2].selector);
            if (el1.contains(el2) || el2.contains(el1)) {
              continue; // Parent-child overlap is expected/normal
            }

            const overlapX = r1.left < r2.right && r1.right > r2.left;
            const overlapY = r1.top < r2.bottom && r1.bottom > r2.top;

            if (overlapX && overlapY) {
              overlapCount++;
              logs.push(`  [WARNING] Overlap detected between "${k1}" and "${k2}"!`);
            }
          }
        }
        if (overlapCount === 0) {
          logs.push('  [PASS] No overlapping blocks detected.');
        }

        // Detect Whitespace Gaps
        logs.push('\n--- Whitespace Gaps Detection ---');
        // Let's measure gap between adjacent elements in the Left Column
        const leftColKeys = ['gallery', 'narrative', 'lifecycle'];
        let gapIssue = false;
        for (let i = 0; i < leftColKeys.length - 1; i++) {
          const k1 = leftColKeys[i];
          const k2 = leftColKeys[i+1];
          if (elements[k1]?.found && elements[k2]?.found) {
            const bottomOf1 = elements[k1].rect.bottom;
            const topOf2 = elements[k2].rect.top;
            const gap = topOf2 - bottomOf1;
            logs.push(`  Gap between ${k1} and ${k2}: ${gap.toFixed(1)}px`);
            if (gap < 0) {
              logs.push(`  [WARNING] Elements are overlapping vertically (gap = ${gap.toFixed(1)}px)`);
              gapIssue = true;
            } else if (gap > 100) {
              logs.push(`  [WARNING] Large vertical gap detected (gap = ${gap.toFixed(1)}px)`);
              gapIssue = true;
            }
          }
        }
        if (!gapIssue) {
          logs.push('  [PASS] Vertical gaps are within standard margins (0px to 100px).');
        }

        // Column Heights comparison
        logs.push('\n--- Column Heights (Desktop/Large Screen check) ---');
        const leftColContainer = document.querySelector('.detail-left-col');
        const rightColContainer = document.querySelector('.detail-right-col');
        if (leftColContainer && rightColContainer) {
          const lHeight = leftColContainer.getBoundingClientRect().height;
          const rHeight = rightColContainer.getBoundingClientRect().height;
          logs.push(`  Left Column height: ${lHeight.toFixed(1)}px, Right Column height: ${rHeight.toFixed(1)}px`);
        } else {
          logs.push('  Grid columns container elements not found.');
        }

        // Clipping / Overflow issues detection
        logs.push('\n--- Overflow / Clipping Detection ---');
        let clippingCount = 0;
        for (const [key, info] of Object.entries(elements)) {
          if (info.found) {
            // Check horizontal overflow
            const horizOverflow = info.scrollWidth > info.clientWidth + 2; // tolerance of 2px for border/subpixel
            const vertOverflow = info.scrollHeight > info.clientHeight + 2;
            if (horizOverflow) {
              clippingCount++;
              logs.push(`  [WARNING] Horizontal overflow detected on "${key}": scrollWidth=${info.scrollWidth}, clientWidth=${info.clientWidth}`);
            }
            // For card items, we usually don't want vertical overflow to be clipped unless intentionally scrollable
            const styles = window.getComputedStyle(document.querySelector(info.selector));
            if (vertOverflow && styles.overflowY === 'hidden') {
              clippingCount++;
              logs.push(`  [WARNING] Content clipping detected on "${key}": scrollHeight=${info.scrollHeight}, clientHeight=${info.clientHeight}`);
            }
          }
        }
        if (clippingCount === 0) {
          logs.push('  [PASS] No element clipping or inner overflow detected.');
        }

        // Horizontal Scrollbar check for viewport
        const pageScrollWidth = document.documentElement.scrollWidth;
        const pageClientWidth = window.innerWidth;
        if (pageScrollWidth > pageClientWidth) {
          logs.push(`  [WARNING] Horizontal page scrollbar present! pageScrollWidth=${pageScrollWidth}, pageClientWidth=${pageClientWidth}`);
        } else {
          logs.push('  [PASS] No horizontal page scrollbar (no viewport overflow).');
        }

        return {
          logs,
          elements
        };
      });

      // Output diagnostics logs
      diagnostics.logs.forEach(line => console.log(line));
      await vpContext.close();
    }

  } catch (err) {
    console.error('Layout audit failed:', err);
  } finally {
    await browser.close();
    console.log('\nStopping Django server...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
    } else {
      serverProcess.kill('SIGINT');
    }
    console.log('Layout audit complete.');
  }
}

runLayoutAudit();
