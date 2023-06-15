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

from datetime import datetime
from pathlib import Path
from typing import Optional, List
from zoneinfo import ZoneInfo

import streamlit as st
from diskcache import Cache
from logzero import logger
from humanize import precisedelta
from newsapi import NewsApiClient
from pydantic import BaseModel, BaseSettings, SecretStr, HttpUrl

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="News Dashboard",
)

now = datetime.now(tz=ZoneInfo("UTC"))


class AppSettings(BaseSettings):
    newsapi_api_key: SecretStr  # set NEWSAPI_API_KEY env variable with your apikey
    newsapi_cache_dir: Path  # set NEWSAPI_CACHE_DIR env variable where cache can be created
    app_debug: bool = True


@st.cache_resource
def get_settings():
    return AppSettings()


settings = AppSettings()


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

        data = newsapi.get_everything(q=search_term, page_size=50, language="en")
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
    if category:
        cachekey = f"live-headlines-{category}"
    else:
        cachekey = "live-headlines-all"
    if data := cache.get(cachekey):
        logger.debug("Retrieved live headlines data from cache")
    else:
        logger.info("Fetching live headlines data from NewsAPI")

        data = newsapi.get_top_headlines(category=category, page_size=50)
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


def display_articles(articles: List[Article]):
    """Displays a list of news articles on the Streamlit page.

    Args:
        articles (List[Article]): The list of articles to display.
    """
    first = True
    for article in articles:
        if first:
            first = False
        else:
            st.markdown("---")
        st.write(article.title)
        published_friendly = precisedelta(
            now - article.publishedAt, minimum_unit="minutes", format="%0.0f"
        )
        st.write(
            f"[Read more]({article.url}) - ", f"Published {published_friendly} ago"
        )
        if content := article.get_content():
            with st.expander("Content"):
                st.write(content)
        if settings.app_debug:
            with st.expander("Raw Data"):
                st.code(article.json(indent=2))
        st.caption(
            f"Source: {article.source['name']},  Author: {article.author or 'n/a'}"
        )


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
    with col2.form("Live News"):
        limit_categories = st.selectbox(
            "Live News - Category",
            options=[
                "all",
                "business",
                "entertainment",
                "general",
                "health",
                "science",
                "sports",
                "technology",
            ],
        )
        if limit_categories == "all":
            limit_categories = None

        st.form_submit_button("Update")

        # Fetch live headlines
        live_news_data = fetch_live_headlines(limit_categories)
        # Display live news in right column
        st.subheader("Live News")
        display_articles(live_news_data)

    # Display news in main column
    if search_term:
        news_data = fetch_news_data(search_term)
        with col1:
            st.subheader("Search Results")
            display_articles(news_data)


def main():
    st.title("News Dashboard")
    display_news()


if __name__ == "__main__":
    main()
