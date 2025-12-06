import threading
import time
from datetime import datetime
from typing import Callable
from datetime import datetime, timedelta

from storage.db import Database
from storage.models import Event


class ReminderScheduler(threading.Thread):
    def __init__(self, db, on_reminder, poll_interval: int = 60):
        super().__init__(daemon=True)
        self.db = db
        self.on_reminder = on_reminder
        self.poll_interval = poll_interval
        self._running = True
        self._reminded_ids = set()

    # Run method of the thread
    def run(self):
        print("DEBUG: ReminderScheduler started")
        while self._running:
            try:
                now = datetime.now()
                events = self.db.get_all_events()

                for event in events:
                    if event.id in self._reminded_ids:
                        continue
                    if not event.start_time:
                        continue

                    reminder_minutes = event.reminder_minutes or 0
                    reminder_time = event.start_time - timedelta(minutes=reminder_minutes)

                    if reminder_time <= now < event.start_time:
                        print(f"DEBUG: triggering reminder for event {event.id}")
                        self.on_reminder(event)
                        self._reminded_ids.add(event.id)

                time.sleep(self.poll_interval)
            except Exception as e:
                print("ERROR in ReminderScheduler:", e)
                time.sleep(self.poll_interval)

    def stop(self):
        self._running = False
