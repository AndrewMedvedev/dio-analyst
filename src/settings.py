from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class GoogleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GOOGLE_")

    base_url: str = "https://www.googleapis.com"
    psi_api_key: str = "<API_KEY>"


class YandexCloudSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YANDEX_CLOUD_")

    folder_id: str = "<FOLDER_ID>"
    api_key: str = "<API_KEY>"


class Settings(BaseSettings):
    google: GoogleSettings = GoogleSettings()
    yandexcloud: YandexCloudSettings = YandexCloudSettings()


settings = Settings()
