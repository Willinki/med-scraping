const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const url = require('url');

const visited = new Set();
let baseDomain;

async function downloadPage(page, currentUrl, savePath) {
  try {
    console.log(`Navigating to: ${currentUrl}`);
    await page.goto(currentUrl, { waitUntil: 'networkidle2' });

    const html = await page.content();
    const parsedUrl = url.parse(currentUrl);
    const filePath = path.join(savePath, parsedUrl.hostname, parsedUrl.pathname, 'index.html');
    const dir = path.dirname(filePath);

    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(filePath, html);
    console.log(`Saved: ${filePath}`);
  } catch (error) {
    console.error(`Failed to download ${currentUrl}: ${error}`);
  }
}

async function crawlPage(browser, startUrl, savePath) {
  if (visited.has(startUrl)) {
    return;
  }

  visited.add(startUrl);

  const page = await browser.newPage();
  await downloadPage(page, startUrl, savePath);

  try {
    const links = await page.evaluate(() =>
      Array.from(document.querySelectorAll('a'))
        .map(anchor => anchor.href)
        .filter(href => href.startsWith(location.origin))
    );

    for (const link of links) {
      const parsedLink = url.parse(link);
      if (parsedLink.hostname === baseDomain && !visited.has(link)) {
        await crawlPage(browser, link, savePath);
      }
    }
  } catch (error) {
    console.error(`Failed to extract links from ${startUrl}: ${error}`);
  } finally {
    await page.close();
  }
}

async function main() {
  const startUrl = 'https://www.salute.gov.it/'; // Replace with the actual starting URL
  const savePath = './downloaded_site';

  if (!fs.existsSync(savePath)) {
    fs.mkdirSync(savePath, { recursive: true });
  }

  baseDomain = url.parse(startUrl).hostname;

  const browser = await puppeteer.launch();
  await crawlPage(browser, startUrl, savePath);
  await browser.close();
}

main();
