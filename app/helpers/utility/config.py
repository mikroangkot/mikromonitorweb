import os
from dataclasses import dataclass, field
from typing import ClassVar

try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (ImportError, AssertionError, Exception):
        pass
except ImportError:
    pass

@dataclass(frozen=True)
class Config:

    DEBUG: bool = field(
        default_factory=lambda: (
            val[0] != "production"
            if (val := "#TEMPLATE_APP_ENV#") and isinstance(val, list)
            else os.getenv("APP_ENV") != "production"
        )
    )

    APP_NAME: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_APP_NAME#") and isinstance(val, list)
            else os.getenv("APP_NAME")
        )
    )

    APP_VERSION: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_APP_VERSION#") and isinstance(val, list)
            else os.getenv("APP_VERSION")
        )
    )

    API_URL: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_API_URL#") and isinstance(val, list)
            else os.getenv("API_URL")
        )
    )

    API_CDN: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_API_CDN#") and isinstance(val, list)
            else os.getenv("API_CDN")
        )
    )

    HISTORY_BUS: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_HISTORY_BUS#") and isinstance(val, list)
            else os.getenv("HISTORY_BUS")
        )
    )

    LIST_BUS: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_LIST_BUS#") and isinstance(val, list)
            else os.getenv("LIST_BUS")
        )
    )

    LOKASI_HEADWAY: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_LOKASI_HEADWAY#") and isinstance(val, list)
            else os.getenv("LOKASI_HEADWAY")
        )
    )

    HISTORY_HEADWAY: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_HISTORY_HEADWAY#") and isinstance(val, list)
            else os.getenv("HISTORY_HEADWAY")
        )
    )

    MIKRO_API: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_MIKRO_API#") and isinstance(val, list)
            else os.getenv("MIKRO_API")
        )
    )

    AUTHORIZATION: str = field(
        default_factory=lambda: (
            val[0]
            if (val := "#TEMPLATE_AUTHORIZATION#") and isinstance(val, list)
            else os.getenv("AUTHORIZATION")
        )
    )

    HEADERS: ClassVar[dict] = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json",
    }

config = Config()
