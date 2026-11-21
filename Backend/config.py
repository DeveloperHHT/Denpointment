"""Settings, read from environment variables so no password or key lives in the code."""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Everything the application needs to start."""

    backend: str = "mysql"  # "mysql" or "sqlite"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "dentist_management_system"
    sqlite_path: Path = ROOT / "Data" / "demo.db"
    secret_key: str = field(default_factory=lambda: secrets.token_hex(32))
    csrf_enabled: bool = True
    testing: bool = False
    password_rounds: int = 535000  # sha256_crypt cost; the tests use a small number to stay fast

    @classmethod
    def from_environment(cls) -> "Settings":
        env = os.environ.get
        return cls(
            backend=env("DENPOINTMENT_DB_BACKEND", "mysql").lower(),
            mysql_host=env("DENPOINTMENT_DB_HOST", "localhost"),
            mysql_port=int(env("DENPOINTMENT_DB_PORT", "3306")),
            mysql_user=env("DENPOINTMENT_DB_USER", "root"),
            mysql_password=env("DENPOINTMENT_DB_PASSWORD", ""),
            mysql_database=env("DENPOINTMENT_DB_NAME", "dentist_management_system"),
            sqlite_path=Path(env("DENPOINTMENT_SQLITE_PATH", str(ROOT / "Data" / "demo.db"))),
            # Without a key a random one is made at start, so everybody is logged out after a restart.
            secret_key=env("DENPOINTMENT_SECRET_KEY") or secrets.token_hex(32),
        )
