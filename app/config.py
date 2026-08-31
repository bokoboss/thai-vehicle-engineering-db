from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vehicle_engineering.db")
    app_name: str = "Thailand Vehicle Engineering Database"
    debug: bool = os.getenv("APP_DEBUG", "0").lower() in {"1", "true", "yes"}
    project_root: Path = PROJECT_ROOT


settings = Settings()
