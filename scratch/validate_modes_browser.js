const { spawn } = require('child_process');
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testMode(mode) {
  console.log(`\n==========================================`);
  console.log(`TESTING BROWSER FOR MODE: ${mode}`);
  console.log(`==========================================`);

  // Start django server with the env var
  const env = { ...process.env, LANDING_MEDIA_MODE: mode };
  const pythonPath = path.resolve(__dirname, '..', 'venv', 'Scripts', 'python.exe');
  const server = spawn(pythonPath, ['manage.py', 'runserver', '127.0.0.1:8001'], {
    cwd: path.resolve(__dirname, '..'),
    env
  });


  server.stdout.on('data', (data) => {
    // console.log(`[Django] ${data}`);
  });

  server.stderr.on('data', (data) => {
    // console.log(`[Django Err] ${data}`);
  });

  // Wait for server to start
  await sleep(3500);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleErrors = [];
  const missingAssets = [];

  page.on('console', msg => {
    // Filter out potential non-error logs or warnings
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
    // Exclude external third-party tools if they fail, focus on our local project files
    if (status >= 400 && url.includes('127.0.0.1')) {
      missingAssets.push(`${status}: ${url}`);
    }
  });

  try {
    await page.goto('http://127.0.0.1:8001/', { waitUntil: 'domcontentloaded', timeout: 15000 });

    
    // Wait for pv-loader to hide if it exists
    try {
      await page.waitForSelector('#pv-loader', { state: 'hidden', timeout: 5000 });
    } catch (e) {}

    await sleep(2000);

    // Verify correct element is on the page
    if (mode === 'VIDEO_HERO') {
      const hero = await page.$('.pv-hero');
      if (!hero) throw new Error('VIDEO_HERO element (.pv-hero) not found in browser');
      
      const config = await page.$eval('#landing-mode-config', el => el.getAttribute('data-mode'));
      if (config !== 'VIDEO_HERO') throw new Error(`Expected config data-mode to be VIDEO_HERO, got ${config}`);
      
    } else if (mode === 'VIDEO_SCRUB') {
      const cinematic = await page.$('.lp-cinematic');
      if (!cinematic) throw new Error('VIDEO_SCRUB cinematic element (.lp-cinematic) not found in browser');

      const video = await page.$('#cinematic-video');
      if (!video) throw new Error('Scrub video element (#cinematic-video) not found in browser');

      const config = await page.$eval('#landing-mode-config', el => el.getAttribute('data-mode'));
      if (config !== 'VIDEO_SCRUB') throw new Error(`Expected config data-mode to be VIDEO_SCRUB, got ${config}`);

    } else if (mode === 'IMAGE_STORY') {
      const cinematic = await page.$('.lp-cinematic');
      if (!cinematic) throw new Error('IMAGE_STORY cinematic element (.lp-cinematic) not found in browser');

      const wrapper = await page.$('.lp-story-wrapper');
      if (!wrapper) throw new Error('IMAGE_STORY wrapper element (.lp-story-wrapper) not found in browser');

      const imagesCount = await page.$$eval('.lp-story-img', imgs => imgs.length);
      if (imagesCount < 11) throw new Error(`Expected at least 11 story frames, found ${imagesCount}`);

    } else if (mode === 'VIDEO_SCROLL_STORY') {
      const cinematic = await page.$('.lp-cinematic');
      if (!cinematic) throw new Error('VIDEO_SCROLL_STORY cinematic element (.lp-cinematic) not found in browser');

      const video = await page.$('#cinematic-video');
      if (!video) throw new Error('Scroll-story video element (#cinematic-video) not found in browser');

      const config = await page.$eval('#landing-mode-config', el => el.getAttribute('data-mode'));
      if (config !== 'VIDEO_SCROLL_STORY') throw new Error(`Expected config data-mode to be VIDEO_SCROLL_STORY, got ${config}`);
    }

    console.log(`✓ HTML element validation succeeded!`);

    // Verify Console Errors
    if (consoleErrors.length > 0) {
      console.error(`❌ Found ${consoleErrors.length} console/page errors:`);
      consoleErrors.forEach(err => console.error(`   - ${err}`));
      throw new Error('Console errors encountered');
    } else {
      console.log(`✓ No console errors detected.`);
    }

    // Verify Missing Assets
    if (missingAssets.length > 0) {
      console.error(`❌ Found ${missingAssets.length} missing assets (status >= 400):`);
      missingAssets.forEach(asset => console.error(`   - ${asset}`));
      throw new Error('Missing assets detected');
    } else {
      console.log(`✓ No missing assets/network errors.`);
    }

    console.log(`🚀 ${mode} PASSED!`);

  } finally {
    await browser.close();
    server.kill();
    await sleep(1500);
  }
}

async function runAll() {
  try {
    await testMode('VIDEO_HERO');
    await testMode('VIDEO_SCRUB');
    await testMode('IMAGE_STORY');
    await testMode('VIDEO_SCROLL_STORY');
    console.log('\n==========================================');
    console.log('🎉 ALL BROWSER VALIDATION TESTS PASSED!');
    console.log('==========================================');
  } catch (err) {
    console.error('\n❌ Validation failed:', err.message);
    process.exit(1);
  }
}

runAll();
