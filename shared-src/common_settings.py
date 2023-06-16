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
    def newsapi_cache_dir(self) -> Path:
        return self.streamlit_app_output_dir / "newsapi-cache"

    @property
    def pdf_uploads(self) -> Path:
        return self.streamlit_app_output_dir / "pdf-upload-dir"
