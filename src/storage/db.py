import sqlite3
from typing import List, Optional
from datetime import datetime, timedelta
from storage.models import Event


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table_if_not_exists()

    # Tạo bảng nếu chưa tồn tại
    def _create_table_if_not_exists(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            location TEXT,
            reminder_minutes INTEGER NOT NULL
        )
        """
        self._conn.execute(sql)
        self._conn.commit()

    # Thêm sự kiện mới
    def add_event(self, event: Event) -> int:
        sql = """
        INSERT INTO events (event, start_time, end_time, location, reminder_minutes)
        VALUES (?, ?, ?, ?, ?)
        """
        cursor = self._conn.execute(
            sql,
            (
                event.event,
                event.start_time.isoformat(),
                event.end_time.isoformat() if event.end_time else None,
                event.location,
                event.reminder_minutes,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    # Cập nhật sự kiện
    def update_event(self, event: Event) -> None:
        sql = """
        UPDATE events
        SET event = ?, start_time = ?, end_time = ?, location = ?, reminder_minutes = ?
        WHERE id = ?
        """
        self._conn.execute(
            sql,
            (
                event.event,
                event.start_time.isoformat(),
                event.end_time.isoformat() if event.end_time else None,
                event.location,
                event.reminder_minutes,
                event.id,
            ),
        )
        self._conn.commit()

    # Xóa sự kiện
    def delete_event(self, event_id: int) -> None:
        sql = "DELETE FROM events WHERE id = ?"
        self._conn.execute(sql, (event_id,))
        self._conn.commit()

    # Lấy tất cả sự kiện
    def get_all_events(self) -> List[Event]:
        sql = "SELECT * FROM events"
        cursor = self._conn.execute(sql)
        rows = cursor.fetchall()
        return [
            Event(
                id=row["id"],
                event=row["event"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                location=row["location"],
                reminder_minutes=row["reminder_minutes"],
            )
            for row in rows
        ]

    # Lấy các sự kiện sắp đến trong khoảng thời gian nhất định
    def get_due_events(self, now: datetime) -> List[Event]:
        sql = """
        SELECT * FROM events
        WHERE start_time <= ? AND start_time >= ?
        """
        cursor = self._conn.execute(
            sql,
            (
                now.isoformat(),
                (now - timedelta(minutes=15)).isoformat(),  # Giả sử nhắc trước 15 phút
            ),
        )
        rows = cursor.fetchall()

        return [
            Event(
                id=row["id"],
                event=row["event"],
                start_time=datetime.fromisoformat(row["start_time"]),
                end_time=datetime.fromisoformat(row["end_time"]) if row["end_time"] else None,
                location=row["location"],
                reminder_minutes=row["reminder_minutes"],
            )
            for row in rows
        ]