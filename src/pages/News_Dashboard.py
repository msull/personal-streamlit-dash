"""
This module implements a News Dashboard application using the Streamlit library.

The application fetches news articles from the NewsAPI, caches them using DiskCache, and displays them in a
streamlined UI. The application supports both a search feature and a live headlines feature.

The search feature allows users to search for articles by keywords, and the results are displayed in the left column.
The live headlines feature fetches and displays the latest headlines from all categories or a selected category
in the right column.

The layout of the page is responsive and adjusts depending on whether a search is made or not. In the presence of a
search term, the search results are given more space, and the live headlines are displayed to the side.

Each news article is presented with its title, source, author, and a link to the full article. If available,
the content of the article is displayed under an expandable section.

The settings for the application, such as the NewsAPI key and the cache directory, are configured using environment
variables and the Pydantic library.

The application also supports a debug mode, which displays the raw data of each article when enabled (on by default).
"""
import json
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

import streamlit as st
from auth_helpers import set_page_config
from common_settings import AppSettings
from diskcache import Cache
from humanize import precisedelta
from logzero import logger
from newsapi import NewsApiClient
from pydantic import BaseModel, HttpUrl

set_page_config("News Dashboard", requires_auth=True)

now = datetime.now(tz=ZoneInfo("UTC"))

NUM_ARTICLES = 50


class SessionData(BaseModel):
    newsdash_init: bool = True
    hidden_articles: List[str] = []
    live_category: str = "all"
    live_article_urls: List[str] = []
    hide_read: bool = True

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.save_to_session()

    def save_to_session(self):
        for k, v in self.dict().items():
            st.session_state[k] = v

    def hide_article(self, url):
        session_data.hidden_articles.append(url)
        self.save_to_session()
        self._save_hidden_articles()

    def _save_hidden_articles(self):
        save_name = st.session_state.get("username") or "global"
        path = settings.newsapi_hidden_urls_dir / (save_name + ".json")
        path.write_text(json.dumps(self.hidden_articles))

    def load_saved_hidden_article_data(self):
        if self.hidden_articles:
            return

        save_name = st.session_state.get("username") or "global"
        path = settings.newsapi_hidden_urls_dir / (save_name + ".json")
        if not path.exists():
            return
        self.hidden_articles = json.loads(path.read_text())


@st.cache_resource
def get_settings():
    return AppSettings()


settings = AppSettings()
settings.newsapi_hidden_urls_dir.mkdir(exist_ok=True, parents=True)


@st.cache_resource
def news_api_cache():
    logger.debug("Setting up NewsAPI Cache")
    return Cache(str(settings.newsapi_cache_dir))


cache = news_api_cache()
logger.debug("Expiring cache items; expired:")
logger.debug(cache.expire())


@st.cache_resource
def news_api_client():
    logger.debug("Setting up NewsAPI Client")
    return NewsApiClient(api_key=settings.newsapi_api_key.get_secret_value())


newsapi = news_api_client()


def _clean_content(content: str) -> str:
    """Cleans the content text by removing unwanted characters and prefixes.

    Args:
        content (str): The raw content text.

    Returns:
        str: The cleaned content text.
    """
    if not content:
        return ""
    content = content.replace("\r", "").replace("\n", " ").replace("  ", " ")
    return content.removeprefix("Comment on this story Comment")


class Article(BaseModel):
    author: Optional[str]
    title: str
    description: Optional[str]
    url: HttpUrl
    publishedAt: datetime
    content: Optional[str]
    source: dict

    def get_content(self) -> str:
        return _clean_content(self.content)


def fetch_news_data(search_term: str) -> List[Article]:
    """Fetches news data for a given search term. The data is fetched from an API or from the cache.

    Args:
        search_term (str): The term to search for in the news.

    Returns:
        List[Article]: A list of news articles matching the search term, sorted by publication date.
    """
    cachekey = f"search-{search_term}"
    if data := cache.get(cachekey):
        logger.debug(f"Retrieved news for {search_term=} from cache")
    else:
        logger.info(f"Fetching headlines for {search_term=} data from NewsAPI")

        data = newsapi.get_everything(q=search_term, page_size=NUM_ARTICLES, language="en")
        if not data["status"] == "ok":
            st.error("Error fetching newsapi data: ", data)
            return []
        logger.debug("Caching data")
        cache.set(cachekey, data, expire=7200)  # 2 hours

    return sorted(
        (Article(**article) for article in data["articles"]),
        key=lambda x: x.publishedAt,
        reverse=True,
    )


def fetch_live_headlines(category: Optional[str] = None) -> List[Article]:
    """Fetches live headlines. The data is fetched from an API or from the cache.

    Args:
        category (Optional[str], optional): The category of news to fetch. If None, fetches all categories.

    Returns:
        List[Article]: A list of live news headlines, sorted by publication date.
    """
    logger.info(f"Getting live news for {category=}")
    if category:
        cachekey = f"live-headlines-{category}"
    else:
        cachekey = "live-headlines-all"
    if data := cache.get(cachekey):
        logger.debug("Retrieved live headlines data from cache")
    else:
        logger.info("Fetching live headlines data from NewsAPI")

        data = newsapi.get_top_headlines(category=category, page_size=NUM_ARTICLES)
        if not data["status"] == "ok":
            st.error("Error fetching newsapi data: ", data)
            session_data.live_article_urls = []
            return []
        logger.debug("Caching data")
        cache.set(cachekey, data, expire=7200)  # 2 hours

    data = sorted(
        (Article(**article) for article in data["articles"]),
        key=lambda x: x.publishedAt,
        reverse=True,
    )
    session_data.live_article_urls = [x.url for x in data]
    return data


def display_articles(articles: List[Article], hide_read=True):
    """Displays a list of news articles on the Streamlit page.

    Args:
        articles (List[Article]): The list of articles to display.
    """

    first = True
    hidden_placeholder = st.empty()
    num_hidden = 0
    if hide_read:
        hidden_placeholder.write(f"Hidden {num_hidden}")
    for idx, article in enumerate(articles):
        if hide_read and article.url in session_data.hidden_articles:
            num_hidden += 1
            hidden_placeholder.write(f"Hidden {num_hidden}")
            continue

        if first:
            first = False
        else:
            st.markdown("---")
        st.write(article.title)
        st.checkbox("Read", key=f"read-{idx}", value=article.url in session_data.hidden_articles)
        published_friendly = precisedelta(now - article.publishedAt, minimum_unit="minutes", format="%0.0f")
        st.write(f"[Read more]({article.url}) - ", f"Published {published_friendly} ago")
        if content := article.get_content():
            with st.expander("Content"):
                st.write(content)
        if settings.app_debug:
            with st.expander("Raw Data"):
                st.code(article.json(indent=2))
        st.caption(f"Source: {article.source['name']},  Author: {article.author or 'n/a'}")


def display_news():
    """Handles the news display process. Fetches and displays news based on user input."""
    search_term = st.text_input("Search News", "").strip()

    # Create columns for layout
    if search_term:
        # big main layout for search results, live news on the side
        col1, col2 = st.columns([2, 1])
    else:
        # live news only
        col1 = None
        col2 = st.columns(1)[0]

    # display the live news headlines
    with col2.form("Live News", clear_on_submit=False):
        options = ["all", "business", "entertainment", "general", "health", "science", "sports", "technology"]
        limit_categories = st.selectbox(
            "Live News - Category", options=options, index=options.index(session_data.live_category)
        )
        hide_read = st.checkbox("Hide read", session_data.hide_read)
        if st.form_submit_button("Update"):
            session_data.live_category = limit_categories
            session_data.hide_read = hide_read
            for x in range(NUM_ARTICLES):
                if st.session_state.get(f"read-{x}"):
                    session_data.hide_article(session_data.live_article_urls[x])
            st.experimental_rerun()
        if limit_categories == "all":
            limit_categories = None

        # Fetch live headlines
        articles = fetch_live_headlines(limit_categories)
        # Display live news in right column
        st.subheader("Live News")
        display_articles(articles, hide_read)

    # Display news in main column
    if search_term:
        news_data = fetch_news_data(search_term)
        with col1:
            st.subheader("Search Results")
            display_articles(news_data)


def main():
    st.title("News Dashboard")
    if st.button("Clear Cache"):
        cache.clear()
    display_news()


### APP STARTUP
try:
    if "newsdash_init" not in st.session_state:
        session_data = SessionData()
        session_data.load_saved_hidden_article_data()
        session_data.save_to_session()
    else:
        session_data = SessionData.parse_obj(st.session_state)
    main()
finally:
    with st.sidebar.expander("Session Data"):
        st.write(dict(sorted(st.session_state.items())))
