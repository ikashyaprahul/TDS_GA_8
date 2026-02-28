const { chromium } = require("playwright");

const URLS = [
    "https://sanand0.github.io/tdsdata/js_table/?seed=44",
    "https://sanand0.github.io/tdsdata/js_table/?seed=45",
    "https://sanand0.github.io/tdsdata/js_table/?seed=46",
    "https://sanand0.github.io/tdsdata/js_table/?seed=47",
    "https://sanand0.github.io/tdsdata/js_table/?seed=48",
    "https://sanand0.github.io/tdsdata/js_table/?seed=49",
    "https://sanand0.github.io/tdsdata/js_table/?seed=50",
    "https://sanand0.github.io/tdsdata/js_table/?seed=51",
    "https://sanand0.github.io/tdsdata/js_table/?seed=52",
    "https://sanand0.github.io/tdsdata/js_table/?seed=53",
];

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    let grandTotal = 0;

    for (const url of URLS) {
        await page.goto(url, { waitUntil: "networkidle" });
        // Wait for at least one <td> to appear (JS-rendered table)
        await page.waitForSelector("td", { timeout: 30000 });

        const pageSum = await page.$$eval("td", (cells) =>
            cells.reduce((sum, cell) => {
                const num = parseFloat(cell.innerText);
                return isNaN(num) ? sum : sum + num;
            }, 0)
        );

        console.log(`URL: ${url} => Sum: ${pageSum}`);
        grandTotal += pageSum;
    }

    console.log(`\nGRAND TOTAL: ${grandTotal}`);
    await browser.close();
})();
