"""Database access: one connection per request, MySQL in production and SQLite for the demo and the tests.

All SQL in the repositories is written with %s placeholders and plain SQL that both engines understand.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Sequence

from flask import Flask, g

from .config import Settings

Row = Dict[str, Any]


class Database:
    """A thin wrapper around a DB-API connection that returns rows as dictionaries."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._connection: Any = None

    # -- connection -------------------------------------------------------------------------

    @property
    def is_sqlite(self) -> bool:
        return self.settings.backend == "sqlite"

    def _connect(self) -> Any:
        if self.is_sqlite:
            self.settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(str(self.settings.sqlite_path), detect_types=sqlite3.PARSE_DECLTYPES)
            connection.row_factory = lambda cursor, row: {d[0]: row[i] for i, d in enumerate(cursor.description)}
            connection.execute("PRAGMA foreign_keys = ON")
            return connection

        import pymysql  # imported here so the demo works without the MySQL driver

        return pymysql.connect(
            host=self.settings.mysql_host,
            port=self.settings.mysql_port,
            user=self.settings.mysql_user,
            password=self.settings.mysql_password,
            database=self.settings.mysql_database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    @property
    def connection(self) -> Any:
        if self._connection is None:
            self._connection = self._connect()
        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    # -- queries ----------------------------------------------------------------------------

    def _sql(self, sql: str) -> str:
        return sql.replace("%s", "?") if self.is_sqlite else sql

    def fetch_all(self, sql: str, params: Sequence[Any] = ()) -> List[Row]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(self._sql(sql), tuple(params))
            return list(cursor.fetchall())
        finally:
            cursor.close()

    def fetch_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[Row]:
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        """Runs a write statement, commits and returns the id of the new row (when there is one)."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(self._sql(sql), tuple(params))
            self.connection.commit()
            return int(cursor.lastrowid or 0)
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def run_script(self, script: str) -> None:
        """Runs several SQL statements (SQLite only, used for the schema and the demo data)."""
        if not self.is_sqlite:
            raise RuntimeError("Scripts are only supported for SQLite; import the .sql file into MySQL instead.")
        self.connection.executescript(script)
        self.connection.commit()


def get_database() -> Database:
    """The database of the current request."""
    if "database" not in g:
        from flask import current_app

        g.database = Database(current_app.config["SETTINGS"])
    return g.database


def init_app(app: Flask) -> None:
    @app.teardown_appcontext
    def close_database(_error: Optional[BaseException] = None) -> None:
        database = g.pop("database", None)
        if database is not None:
            database.close()
