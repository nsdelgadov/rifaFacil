import sqlite3

from rifafacil.domain.rifa import Rifa


class SqliteRifaRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS rifa (id INTEGER PRIMARY KEY, datos TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )

    def guardar(self, rifa: Rifa) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO rifa (id, datos) VALUES (1, ?)",
                (rifa.model_dump_json(),),
            )

    def obtener(self) -> Rifa | None:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute("SELECT datos FROM rifa WHERE id = 1").fetchone()
        if row is None:
            return None
        return Rifa.model_validate_json(row[0])

    def get_config(self, key: str, default: str) -> str:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default

    def set_config(self, key: str, value: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, value),
            )
