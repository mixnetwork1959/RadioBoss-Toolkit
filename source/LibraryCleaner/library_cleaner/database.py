from __future__ import annotations

import re
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable


class DatabaseError(RuntimeError):
    pass


class Database(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[tuple]: ...

    @abstractmethod
    def table_exists(self, name: str) -> bool: ...

    @abstractmethod
    def quote(self, identifier: str) -> str: ...

    @abstractmethod
    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @property
    @abstractmethod
    def placeholder(self) -> str: ...

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def validate_table_name(name: str) -> str:
    if not re.fullmatch(r"library_\d+|libraries|tracks2", name):
        raise DatabaseError(f"Unsafe or unexpected table name: {name}")
    return name


class SQLiteDatabase(Database):
    def __init__(self, path: str | Path, read_only: bool = True):
        self.path = Path(path)
        self.read_only = read_only
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        if not self.path.is_file():
            raise DatabaseError(f"SQLite database not found: {self.path}")
        try:
            mode = "ro" if self.read_only else "rw"
            uri = self.path.resolve().as_uri() + f"?mode={mode}"
            self.connection = sqlite3.connect(uri, uri=True)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Could not open SQLite database: {exc}") from exc

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[tuple]:
        if self.connection is None:
            raise DatabaseError("Database is not connected")
        try:
            return list(self.connection.execute(sql, params).fetchall())
        except sqlite3.Error as exc:
            raise DatabaseError(str(exc)) from exc

    def table_exists(self, name: str) -> bool:
        rows = self.fetchall(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        )
        return bool(rows)

    def quote(self, identifier: str) -> str:
        return f'"{validate_table_name(identifier)}"'

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        if self.connection is None:
            raise DatabaseError("Database is not connected")
        if self.read_only:
            raise DatabaseError("SQLite database was opened in read-only mode")
        try:
            cursor = self.connection.execute(sql, params)
            return cursor.rowcount
        except sqlite3.Error as exc:
            raise DatabaseError(str(exc)) from exc

    def commit(self) -> None:
        if self.connection is not None:
            self.connection.commit()

    def rollback(self) -> None:
        if self.connection is not None:
            self.connection.rollback()

    @property
    def placeholder(self) -> str:
        return "?"

    def backup_to(self, target: str | Path) -> None:
        if self.connection is None:
            raise DatabaseError("Database is not connected")
        destination = sqlite3.connect(target)
        try:
            self.connection.backup(destination)
        finally:
            destination.close()


class MySQLDatabase(Database):
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ):
        self.settings = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }
        self.connection: Any = None

    def connect(self) -> None:
        try:
            import pymysql
        except ImportError as exc:
            raise DatabaseError(
                "MySQL support requires PyMySQL (pip install PyMySQL)."
            ) from exc
        try:
            self.connection = pymysql.connect(
                **self.settings, charset="utf8mb4", autocommit=False
            )
        except Exception as exc:
            raise DatabaseError(f"Could not connect to MySQL: {exc}") from exc

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[tuple]:
        if self.connection is None:
            raise DatabaseError("Database is not connected")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return list(cursor.fetchall())
        except Exception as exc:
            raise DatabaseError(str(exc)) from exc

    def table_exists(self, name: str) -> bool:
        rows = self.fetchall(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema=%s AND table_name=%s",
            (self.settings["database"], name),
        )
        return bool(rows)

    def quote(self, identifier: str) -> str:
        return f"`{validate_table_name(identifier)}`"

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        if self.connection is None:
            raise DatabaseError("Database is not connected")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount
        except Exception as exc:
            raise DatabaseError(str(exc)) from exc

    def commit(self) -> None:
        if self.connection is not None:
            self.connection.commit()

    def rollback(self) -> None:
        if self.connection is not None:
            self.connection.rollback()

    @property
    def placeholder(self) -> str:
        return "%s"
