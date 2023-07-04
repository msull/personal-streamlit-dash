from pathlib import Path

from pydantic import BaseSettings, SecretStr


class AppSettings(BaseSettings):
    streamlit_app_output_dir: Path

    todoist_api_key: SecretStr
    openai_api_key: SecretStr
    newsapi_api_key: SecretStr
    mapquest_api_key: SecretStr

    newsapi_cache_dir: Path
    app_debug: bool = True

    @property
    def credentials_dir(self) -> Path:
        return self.streamlit_app_output_dir / "credentials-db"

    @property
    def newsapi_cache_dir(self) -> Path:
        return self.streamlit_app_output_dir / "newsapi-cache"

    @property
    def newsapi_ai_headlines_cache_dir(self) -> Path:
        p = self.streamlit_app_output_dir / "newsapi-ai-headlines-cache"
        p.mkdir(exist_ok=True, parents=True)
        return p

    def _webscraper_data(self, sub_path) -> Path:
        p = self.streamlit_app_output_dir / "webscraper" / sub_path
        p.mkdir(exist_ok=True, parents=True)
        return p

    @property
    def webscraper_cache_dir(self) -> Path:
        return self._webscraper_data('cache')

    @property
    def webscraper_content_dir(self) -> Path:
        return self._webscraper_data('content')

    @property
    def newsapi_hidden_urls_dir(self) -> Path:
        return self.streamlit_app_output_dir / "newsapi-hidden-urls"

    @property
    def pdf_uploads(self) -> Path:
        return self.streamlit_app_output_dir / "pdf-upload-dir"
