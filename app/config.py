from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    version: str = "1.0.0"
    debug: bool = False
    root_path: str = "/"
    port: int = 8001
    host: str = "0.0.0.0"
    city: Optional[str] = None
    radar_location: Optional[str] = None
    wx_station_url: Optional[str] = None

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
