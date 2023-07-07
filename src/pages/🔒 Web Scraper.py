# Required Libraries
from collections import defaultdict
from random import choice

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from logzero import logger
from diskcache import Cache

from auth_helpers import set_page_config
from common_settings import AppSettings
from readability import Document
import streamlit.components.v1 as components

set_page_config("Web scraper", requires_auth=True)

ONE_YEAR_IN_SECS = 60 * 60 * 24 * 365

if not "scraped_urls" in st.session_state:
    st.session_state.scraped_urls = defaultdict(list)
    st.session_state.view_url = None


@st.cache_resource
def get_settings():
    return AppSettings(
        app_debug=False,
    )


settings = get_settings()


@st.cache_resource
def scraped_url_cache():
    cache = Cache(str(settings.webscraper_cache_dir))
    logger.debug("Setting up Webscraper Cache")
    logger.debug("Expiring cache items; expired:")
    logger.debug(cache.expire())
    return cache


CACHE = scraped_url_cache()


def get_url_cachekey(url: str) -> str:
    return url.replace("/", "_").replace(".", "_")


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    # add as many as you want
]


def get_url_contents(url: str, cache_time_secs=3600):
    cache_url = get_url_cachekey(url)
    cached_content_path = settings.webscraper_content_dir / cache_url
    has_cache = cached_content_path.exists()
    cache_valid = CACHE.get(cache_url, False)

    if has_cache and cache_valid:
        content = cached_content_path.read_bytes()
    else:
        logger.debug(f"Making web request to {url=}")
        headers = {"User-Agent": choice(USER_AGENTS)}

        content = requests.get(url, timeout=10, headers=headers).content
        cached_content_path.write_bytes(content)
        CACHE.set(cache_url, True, expire=ONE_YEAR_IN_SECS)

    return content


# Functions to Fetch and Parse URL
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


@st.cache_data
def fetch_url(url):
    logger.info(f"Fetching {url}")
    return BeautifulSoup(get_url_contents(url), "html.parser")


def get_all_links(url):
    soup = fetch_url(url)
    domain = urlparse(url).netloc
    num_links = 0
    links = []
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        if parsed_href.scheme.startswith("mailto"):
            continue

        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            continue
        if domain not in href:
            if not allow_cross_domain:
                continue
        num_links += 1
        links.append(href)
    logger.debug(f"Page had {num_links=}")
    return links


# Streamlit Interface
st.title("Web Scraper")

# User Inputs
with st.form("Scrape"):
    base_url = st.text_input("Enter Base URL: ")
    if base_url:
        base_url = base_url.removesuffix('/')
    depth = st.slider("Select Depth of Crawl: ", min_value=1, max_value=5, value=2)
    max_links_crawled = st.number_input("Max number of links crawled: ", min_value=1, max_value=1000, value=50, step=25)
    allow_cross_domain = st.checkbox("Allow Cross-Domain Crawling?")

    if st.form_submit_button("Start Scraping") and base_url:
        logger.info(f"Begin scrape for {base_url=}")
        # reset session state vars
        st.session_state.scraped_urls = defaultdict(list)
        st.session_state.view_url = None
        with st.spinner(f"Crawling {base_url}..."):
            num_crawled = 0
            crawled_count_display = st.empty()

            # Check Robots.txt
            rp = RobotFileParser()
            rp.set_url(urljoin(base_url, "/robots.txt"))
            try:
                rp.read()
            except:
                no_robots_txt = True
            else:
                no_robots_txt = False

            if no_robots_txt or rp.can_fetch("*", base_url):
                urls_to_scrape = {base_url}
                scraped_urls = set()

                stop_processing = False

                # Crawl Pages and Fetch Data
                for level in range(depth):
                    if stop_processing:
                        break
                    new_urls_to_scrape = set()
                    for url in urls_to_scrape:
                        if num_crawled >= max_links_crawled:
                            st.info("Hit max links crawled")
                            stop_processing = True
                            break
                        try:
                            if url not in scraped_urls:
                                soup = fetch_url(url)
                                for found_url in get_all_links(url):
                                    new_urls_to_scrape.add(found_url)
                                st.session_state.scraped_urls[level + 1].append((url, soup.title.string))
                                scraped_urls.add(url)

                                num_crawled += 1
                                crawled_count_display.write(f"Num crawled {num_crawled}")
                        except Exception as e:
                            logger.exception(f"Error scraping {url=}")
                            st.write(f"Error scraping {url}: {e}")
                    st.write(f"Done with level {level+1}")
                    urls_to_scrape = new_urls_to_scrape
            else:
                st.write(f"The website at {base_url} has disallowed scraping.")

if st.session_state.scraped_urls:
    core_content, links = st.columns((2, 1))

    with core_content:
        root_url = st.session_state.scraped_urls[1][0][0]
        root_doc = Document(get_url_contents(root_url))

        st.write(f"Scrape Results for **{root_doc.short_title()}**")

        if st.session_state.view_url:
            view_url = st.session_state.view_url
            view_doc = Document(get_url_contents(st.session_state.view_url))
        else:
            view_url = root_url
            view_doc = root_doc
        view_type = st.radio("View type", ("summary", "full"))
        if view_type == "summary":
            view_content = view_doc.summary()
        else:
            view_content = view_doc.content()

        st.write(f'**Viewing** "{view_doc.title()}"')
        st.caption(view_url)

        components.html(view_content, height=800, scrolling=True)

    with links:

        def _view_url(view_level, view_idx):
            st.session_state.view_url = st.session_state.scraped_urls[view_level][view_idx][0]

        for level, scraped_urls in st.session_state.scraped_urls.items():
            st.write(f"Level {level}")
            with st.expander(f"Crawl depth {level}"):
                for idx, scraped_url in enumerate(scraped_urls):
                    url, title = scraped_url
                    if idx > 0:
                        st.divider()
                    st.write(f"[{title}]({url})")
                    st.button("View", key=f"view-{level}-{idx}", on_click=_view_url, args=(level, idx))


st.divider()

with st.expander("Session State"):
    st.write(st.session_state)
