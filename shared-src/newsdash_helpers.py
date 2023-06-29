import json
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, HttpUrl
from logzero import logger
from chat_session import ChatSession

if TYPE_CHECKING:
    from diskcache import Cache

LLM_INSTRUCTIONS = """
You are an AI News Headline Formatter. 
Your task is to process and clean up news headlines, which are presented to you as JSON objects. 
These object have keys as numbers, representing the articles, and the values contain the headlines 
that need reformatting. The headlines are usually inconsistently formatted, including unnecessary characters, 
and are generally short, spanning one or two lines. Your job is to return a single, well-formatted, 
clean sentence for each headline in a JSON object, maintaining the same key for each corresponding article.
"""

LLM_REINFORCEMENT = "Be sure to respond in valid JSON"

LLM_EXAMPLE = {
    "user": json.dumps(
        {
            0: " In the bustling city of Midonia, the mayor unveiled a new public park yesterday, designed to promote outdoor activities and community bonding. Colorful kites filled the sky, and … [+3820 chars]",
            1: "",
            4: "Acclaimed author and novelist, Jane Pennar, won the prestigious Riverton Book Award on Monday. Pennar, known for her remarkable storytelling, was elated with the recognition. In her acceptance speech, she… [+3270 chars]",
            5: "Astrophysicist, Dr. Alex Turner, announced a groundbreaking discovery at the Cosmo Science Convention yesterday. The detection of a previously unknown celestial body has stirred excitement in the scientific community. More details to follow… [+5134 chars]",
        }
    ),
    "assistant": json.dumps(
        {
            0: "Midonia's mayor introduced a new public park yesterday, encouraging outdoor activities and community interaction, marked by the sight of colorful kites filling the sky.",
            1: "",
            4: "Renowned author and novelist, Jane Pennar, claimed the esteemed Riverton Book Award on Monday, celebrated for her exceptional narrative skill.",
            5: "At the Cosmo Science Convention, astrophysicist Dr. Alex Turner revealed the detection of an unknown celestial body, sparking enthusiasm among the scientific community.",
        }
    ),
}


class Article(BaseModel):
    author: Optional[str]
    title: str
    description: Optional[str]
    url: HttpUrl
    publishedAt: datetime
    content: Optional[str]
    source: dict

    def get_content(self) -> str:
        if self.content and self.content.strip():
            use_content = self.content
        else:
            use_content = self.description

        return self._clean_content(use_content)

    @staticmethod
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


@dataclass
class NewsHeadlineFormatter:
    cache: "Cache"
    cache_for_days = 60

    @property
    def cache_for_secs(self) -> int:
        return self.cache_for_days * 24 * 60 * 60

    def _cachekey_for_article(self, article: Article) -> str:
        return f"AI-SUMMARY-{article.url}"

    def generate_ai_headlines_for_articles(self, articles: list[Article]) -> bool:
        needs_headline = {}
        for idx, article in enumerate(articles):
            if self.article_has_ai_headline(article):
                continue
            needs_headline[idx] = article.get_content()

        if not needs_headline:
            return True

        chat_session = ChatSession(initial_system_message=LLM_INSTRUCTIONS, reinforcement_system_msg=LLM_REINFORCEMENT)
        chat_session.user_says(LLM_EXAMPLE["user"])
        chat_session.assistant_says(LLM_EXAMPLE["assistant"])
        chat_session.user_says(json.dumps(needs_headline))
        response = chat_session.get_ai_response()
        content = response.choices[0]["message"]["content"]
        try:
            new_headlines: dict = json.loads(content)
        except:
            logger.exception("Error loading AI headlines response")
            return False

        for idx, headline in new_headlines.items():
            cachekey = self._cachekey_for_article(articles[int(idx)])
            self.cache.set(cachekey, headline, expire=self.cache_for_secs)

        return True

    def get_headline(self, article: Article):
        """Returns the AI generated headline if one exists, otherwise the cleaned Article content."""
        ai_headline = self.get_ai_headline(article)
        if ai_headline:
            return "✨" + ai_headline
        else:
            return article.get_content()

    def article_has_ai_headline(self, article: Article) -> bool:
        return bool(self.cache.get(self._cachekey_for_article(article)))

    def get_ai_headline(self, article: Article) -> Optional[str]:
        return self.cache.get(self._cachekey_for_article(article))
