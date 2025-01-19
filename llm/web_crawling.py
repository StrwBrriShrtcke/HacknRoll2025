import asyncio

from os import path
from pathlib import Path
from datetime import datetime, timezone, timedelta

from crawlee import Request
from crawlee.storages import RequestQueue
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext

from bs4 import BeautifulSoup

import sqlite3
from sqlite3 import Cursor

sites = {
    "nus": "https://www.nus.edu.sg/",
    "nus-soc": "https://www.comp.nus.edu.sg/",
    "sutd": "https://www.sutd.edu.sg/",
    "ntu":"https://www.ntu.edu.sg/",
    "sit":"https://www.singaporetech.edu.sg/",
    "sim":"https://www.sim.edu.sg/",
    "mit":"https://www.mit.edu/",
    "cmu":"https://www.cmu.edu/",
    "berkeley":"https://www.berkeley.edu/",
}

# Config
max_crawl_depth = 2  # TODO change to 2 later
site = "nus"
max_links_visited_per_page = 200
results_dir = "results"
filename = f"crawl_{site}_max_depth_{max_crawl_depth}"

Path(results_dir).mkdir(parents=True, exist_ok=True)
db_filepath = path.join(results_dir, "site_info.db")

# set up database connection
con = sqlite3.connect(db_filepath)
cur = con.cursor()

# make table schema
cur.execute(
    """
CREATE TABLE IF NOT EXISTS domains(
    site TEXT PRIMARY KEY NOT NULL,
    url TEXT NOT NULL
)
"""
)

cur.execute(
    """
CREATE TABLE IF NOT EXISTS sites(
    id INTEGER PRIMARY KEY NOT NULL,
    created_at TEXT NOT NULL DEFAULT current_timestamp,
    url TEXT UNIQUE NOT NULL,
    loaded_url TEXT NOT NULL,
    site NOT NULL REFERENCES domains(site),
    from_site_id REFERENCES sites(id),
    depth INTEGER NOT NULL,
    num_links INTEGER NOT NULL,
    num_imgs INTEGER NOT NULL,
    title TEXT NOT NULL,
    text_content TEXT,
    FOREIGN KEY(site) REFERENCES domains(site),
    FOREIGN KEY(from_site_id) REFERENCES sites(id)
)
"""
)

cur.executemany(
    "INSERT OR IGNORE INTO domains VALUES(?, ?)",
    [(k, v) for k, v in sites.items()],
)
con.commit()


async def crawl_site(site: str) -> None:

    rq = await RequestQueue.open()
    request = Request.from_url(sites[site])
    await rq.add_request(request)

    crawler = PlaywrightCrawler(
        request_provider=rq,
        max_requests_per_crawl=10000,  # can increase if too low, or remove it if you're confident it won't run indefinitely
        headless=True,  # so that it doesn't run the browser gui
        browser_type="chromium",
        max_crawl_depth=max_crawl_depth,  # adjustable
    )

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        from_url = context.request.user_data.get("fromUrl")
        url = context.request.url

        context.log.info(
            f"""
            Depth: {context.request.crawl_depth}
            Current url: {url}
            From: {from_url}
            """
        )

        # Enqueue all links found on the page and set url of current page as its label
        # Using the request's label as a way to track parent links

        # built in enqueue_links function seems limited
        await context.enqueue_links(
            user_data={"fromUrl": url},
            # limit=max_links_visited_per_page,  # seems to limit the queue capacity and nothing would be enqueued if the queue is full, idk man
        )

        # Extract text from html using BeautifulSoup
        html_content = await context.page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)
        num_links = len(soup.find_all("a"))
        num_imgs = len(soup.find_all("img"))

        from_site_id = (
            cur.execute(
                "SELECT id FROM sites WHERE url=?",
                (from_url,),
            ).fetchone()[0]
            if from_url
            else None
        )

        # Extract data from the page using Playwright API.
        data = {
            "url": url,
            "loaded_url": context.request.loaded_url,  # could differ from url because of redirects
            "site": site,
            "from_site_id": from_site_id,
            "depth": context.request.crawl_depth,
            # "generated_at": datetime.now(sg_tz),
            "num_links": num_links,
            "num_imgs": num_imgs,
            "title": await context.page.title(),
            "text_content": text_content,
        }

        cur.execute(
            """
INSERT OR IGNORE INTO sites(
    url,
    loaded_url,
    site,
    from_site_id,
    depth,
    num_links,
    num_imgs,
    title,
    text_content
) VALUES (
    :url,
    :loaded_url,
    :site,
    :from_site_id,
    :depth,
    :num_links,
    :num_imgs,
    :title,
    :text_content
)
""",
            data,
        )
        con.commit()

        # Push the extracted data to the default dataset.
        # await context.push_data(data)  # just a json file right now

    await crawler.run()

    # Export the entire dataset to a JSON file.
    # results_file = path.join(results_dir, f"{filename}_results.json")
    # await crawler.export_data(results_file)

    # Export stats
    stats_file = path.join(results_dir, f"{filename}_stats.json")
    with open(stats_file, "w") as f:
        f.write(str(crawler.statistics.calculate()))

    # Or work with the data directly.
    # data = await crawler.get_data()


if __name__ == "__main__":
    asyncio.run(crawl_site("nus"))
