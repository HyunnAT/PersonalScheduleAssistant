from ui.main_window import MainWindow
from storage.db import Database
from reminder.scheduler import ReminderScheduler


def main():
    db = Database("events.db")
    app = MainWindow(db=db)

    # Callback khi đến thời gian nhắc
    def on_reminder(event):
        app.after(0, lambda e=event: app.show_reminder_popup(e))
    scheduler = ReminderScheduler(db=db, on_reminder=on_reminder)
    scheduler.daemon = True
    scheduler.start()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")

