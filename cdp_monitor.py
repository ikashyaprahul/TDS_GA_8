"""
TDS CDP Trap - Runtime Diagnostics Script
Navigates all 15 pages, captures uncaught JS exceptions via pageerror event.
Writes results to report.txt
"""

import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://sanand0.github.io/tdsdata/cdp_trap/"
STUDENT_PARAM = "student=23f1003149%40ds.study.iitm.ac.in"

PAGES = ["index.html"] + [f"page_{i}.html" for i in range(1, 15)]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        pages_visited = []
        uncaught_exceptions = {}  # page_name -> list of error messages
        all_console = []  # (page_name, type, text)
        current_page = {"name": ""}

        def on_page_error(error):
            pname = current_page["name"]
            err_msg = str(error)
            if pname not in uncaught_exceptions:
                uncaught_exceptions[pname] = []
            uncaught_exceptions[pname].append(err_msg)

        def on_console(msg):
            pname = current_page["name"]
            all_console.append((pname, msg.type, msg.text))

        page.on("pageerror", on_page_error)
        page.on("console", on_console)

        for page_name in PAGES:
            current_page["name"] = page_name
            url = f"{BASE_URL}{page_name}?{STUDENT_PARAM}"
            try:
                await page.goto(url, wait_until="load", timeout=15000)
            except Exception as e:
                pass
            pages_visited.append(page_name)
            # Wait for async errors (5 seconds)
            await asyncio.sleep(5)

        await browser.close()

        # Write report
        with open("report.txt", "w") as f:
            f.write("=" * 60 + "\n")
            f.write("DIAGNOSTIC REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Pages visited ({len(pages_visited)}):\n")
            for vp in pages_visited:
                f.write(f"  {vp}\n")

            f.write(f"\nPages with UNCAUGHT JS exceptions ({len(uncaught_exceptions)}):\n")
            for pg in pages_visited:
                if pg in uncaught_exceptions:
                    for e in uncaught_exceptions[pg]:
                        f.write(f"  {pg}: {e}\n")

            first_error_page = None
            for vp in pages_visited:
                if vp in uncaught_exceptions:
                    first_error_page = vp
                    break

            f.write(f"\n{'='*60}\n")
            f.write("FINAL ANSWER\n")
            f.write(f"{'='*60}\n")
            f.write(f"TOTAL_PAGES_VISITED={len(pages_visited)}\n")
            f.write(f"TOTAL_ERRORS={len(uncaught_exceptions)}\n")
            f.write(f"FIRST_ERROR_PAGE={first_error_page}\n")

            f.write(f"\n\nAll console messages:\n")
            for pname, mtype, text in all_console:
                f.write(f"  [{pname}] [{mtype}] {text}\n")

        print("Report written to report.txt")


if __name__ == "__main__":
    asyncio.run(main())
