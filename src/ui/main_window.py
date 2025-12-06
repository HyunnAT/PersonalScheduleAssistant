import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date
from storage.models import Event
import winsound
import calendar
from tkinter import filedialog
from storage.models import Event


class MainWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        # Biến trạng thái
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today
        self.view_mode = tk.StringVar(value="all")  

        # Cấu hình cửa sổ chính
        self.title("Personal Schedule Assistant")
        self.geometry("1000x640")
        self.minsize(960, 600)
        self.configure(bg="#f5f7fb")

        self._configure_styles()

        # HEADER
        header_frame = ttk.Frame(self, style="Header.TFrame")
        header_frame.pack(fill="x", padx=16, pady=(10, 4))

        title_lbl = ttk.Label(
            header_frame,
            text="📅 Personal Schedule Assistant",
            style="HeaderTitle.TLabel",
        )
        title_lbl.pack(side="left")

        subtitle_lbl = ttk.Label(
            header_frame,
            text="Quản lý lịch cá nhân với ngôn ngữ tự nhiên tiếng Việt",
            style="HeaderSubtitle.TLabel",
        )
        subtitle_lbl.pack(side="left", padx=(12, 0))

        # 1.Khung nhập yêu cầu
        input_frame_shadow = ttk.Frame(self, style="Shadow.TFrame")
        input_frame_shadow.pack(fill="x", padx=16, pady=(6, 4))
        input_frame = ttk.Frame(input_frame_shadow, style="Card.TFrame")
        input_frame.pack(fill="x", padx=1, pady=1)

        lbl = ttk.Label(
            input_frame,
            text="Nhập yêu cầu bằng tiếng Việt:",
            style="CardTitle.TLabel",
        )
        lbl.pack(anchor="w", pady=(4, 4))

        self.txt_input = tk.Text(
            input_frame,
            height=3,
            font=("Segoe UI", 10),
            relief="flat",
            wrap="word",
        )
        self.txt_input.pack(fill="x", pady=(0, 2))
        self.txt_input.configure(
            highlightthickness=1,
            highlightbackground="#d1d5db",
            bg="#ffffff",
        )

        hint_lbl = ttk.Label(
            input_frame,
            text='Ví dụ: "Tạo lịch họp nhóm vào 9h sáng mai tại phòng A"',
            style="Subtle.TLabel",
        )
        hint_lbl.pack(anchor="w", pady=(0, 6))

        def _on_focus_in(event):
            self.txt_input.configure(highlightbackground="#2563eb")

        def _on_focus_out(event):
            self.txt_input.configure(highlightbackground="#d1d5db")

        self.txt_input.bind("<FocusIn>", _on_focus_in)
        self.txt_input.bind("<FocusOut>", _on_focus_out)

        actions_frame = ttk.Frame(input_frame, style="Card.TFrame")
        actions_frame.pack(fill="x", pady=(2, 4))

        # Nút thêm, sửa, xóa sự kiện
        btn_add = ttk.Button(
            actions_frame,
            text="➕ Thêm sự kiện",
            style="Primary.TButton",
            command=self._on_add_event_clicked,
        )
        btn_add.pack(side="left", padx=(0, 6))

        btn_edit = ttk.Button(
            actions_frame,
            text="📝 Chỉnh sửa",
            style="Secondary.TButton",
            command=self._on_edit_event_clicked,
        )
        btn_edit.pack(side="left", padx=(0, 6))

        btn_delete = ttk.Button(
            actions_frame,
            text="❌ Xóa",
            style="Danger.TButton",
            command=self._on_delete_event_clicked,
        )
        btn_delete.pack(side="left", padx=6)

        # Nút xuất dữ liệu .ics
        btn_export_ics = ttk.Button(
            actions_frame,
            text="📤Xuất .ics",
            style="Secondary.TButton",
            command=self._on_export_ics_clicked,
        )
        btn_export_ics.pack(side="left", padx=6)

        # 2. Tìm kiếm sự kiện
        search_shadow = ttk.Frame(self, style="Shadow.TFrame")
        search_shadow.pack(fill="x", padx=16, pady=4)

        search_frame = ttk.Frame(search_shadow, style="Card.TFrame")
        search_frame.pack(fill="x", padx=1, pady=1)

        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        search_frame.grid_columnconfigure(2, weight=0)
        search_frame.grid_columnconfigure(3, weight=0)

        spacer = ttk.Frame(search_frame, style="Card.TFrame")
        spacer.grid(row=0, column=0, sticky="ew")

        self.search_entry = ttk.Entry(
            search_frame,
            font=("Segoe UI", 10),
            width=62
        )
        self.search_entry.grid(row=0, column=1, padx=(0, 6), pady=6, sticky="e")

        # Nút tìm kiếm 
        btn_search = ttk.Button(
            search_frame,
            text="🔎 Tìm kiếm",
            style="Secondary.TButton",
            command=self._on_search_clicked,
        )
        btn_search.grid(row=0, column=2, padx=(0, 6), pady=6, sticky="e")

        # Nút hiển thị tất cả 
        btn_clear_search = ttk.Button(
            search_frame,
            text="📄  Hiển thị tất cả",
            style="Ghost.TButton",
            command=self._on_clear_search_clicked,
        )
        btn_clear_search.grid(row=0, column=3, padx=(0, 8), pady=6, sticky="e")


        # 3. Lịch mini + bảng sự kiện
        main_shadow = ttk.Frame(self, style="Shadow.TFrame")
        main_shadow.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        main_frame = ttk.Frame(main_shadow, style="Card.TFrame")
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # ----- 3.1 LỊCH MINI BÊN TRÁI -----
        calendar_outer = ttk.Frame(main_frame, style="CardInner.TFrame")
        calendar_outer.grid(row=0, column=0, sticky="nsw", padx=(8, 12), pady=8)

        self._build_mini_calendar(calendar_outer)

        # ----- 3.2 BẢNG SỰ KIỆN BÊN PHẢI -----
        table_outer = ttk.Frame(main_frame, style="CardInner.TFrame")
        table_outer.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=8)
        table_outer.grid_rowconfigure(2, weight=1)
        table_outer.grid_columnconfigure(0, weight=1)

        # Thanh filter kiểu Today / Day / Week / Month
        filter_frame = ttk.Frame(table_outer, style="CardInner.TFrame")
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        filter_frame.grid_columnconfigure(0, weight=1)

        self.selected_date_label = ttk.Label(
            filter_frame,
            text="",
            style="Subtle.TLabel",
        )
        self.selected_date_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        buttons_frame = ttk.Frame(filter_frame, style="CardInner.TFrame")
        buttons_frame.grid(row=0, column=1, sticky="e")

        ttk.Button(
            buttons_frame,
            text="Today",
            style="Chip.TButton",
            command=self._on_today_clicked,
        ).pack(side="left", padx=2)

        ttk.Button(
            buttons_frame,
            text="Day",
            style="Chip.TButton",
            command=lambda: self._set_view_mode("day"),
        ).pack(side="left", padx=2)

        ttk.Button(
            buttons_frame,
            text="Week",
            style="Chip.TButton",
            command=lambda: self._set_view_mode("week"),
        ).pack(side="left", padx=2)

        ttk.Button(
            buttons_frame,
            text="Month",
            style="Chip.TButton",
            command=lambda: self._set_view_mode("month"),
        ).pack(side="left", padx=2)

        # Tiêu đề bảng
        table_title = ttk.Label(
            table_outer,
            text="Danh sách sự kiện",
            style="CardTitle.TLabel",
        )
        table_title.grid(row=1, column=0, sticky="w", pady=(4, 2))
        
        # Bảng sự kiện (Treeview)
        tree_container = ttk.Frame(table_outer, style="CardInner.TFrame")
        tree_container.grid(row=2, column=0, sticky="nsew", pady=(2, 0))

        columns = ("id", "event", "start_time", "end_time", "location", "reminder_minutes")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            style="Modern.Treeview",
        )

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        headers = {
            "id": "ID",
            "event": "Sự kiện",
            "start_time": "Bắt đầu",
            "end_time": "Kết thúc",
            "location": "Địa điểm",
            "reminder_minutes": "Nhắc trước (phút)",
        }
        for col in columns:
            self.tree.heading(col, text=headers.get(col, col))

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("event", width=260, anchor="w")
        self.tree.column("start_time", width=150, anchor="center")
        self.tree.column("end_time", width=150, anchor="center")
        self.tree.column("location", width=170, anchor="w")
        self.tree.column("reminder_minutes", width=130, anchor="center")

        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("evenrow", background="#f9fafb")

        self._reload_treeview()
        self._update_selected_date_label()


    #Styles

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Header
        style.configure("Header.TFrame", background="#e0f2fe") 
        style.configure(
            "HeaderTitle.TLabel",
            font=("Segoe UI Semibold", 20),
            foreground="#111827",
            background="#e0f2fe",
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            font=("Segoe UI", 10),
            foreground="#6b7280",
            background="#e0f2fe",
        )

        style.configure("Shadow.TFrame", background="#e5e7eb")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("CardInner.TFrame", background="#ffffff")

        style.configure(
            "CardTitle.TLabel",
            font=("Segoe UI Semibold", 11),
            foreground="#111827",
            background="#ffffff",
        )
        style.configure(
            "Subtle.TLabel",
            font=("Segoe UI", 9),
            foreground="#6b7280",
            background="#ffffff",
        )

        # Button styles
        style.configure(
            "Primary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=8,
            foreground="#ffffff",
            background="#3b82f6",    
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#2563eb"), ("disabled", "#93c5fd")],
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=8,
            foreground="#1e3a8a",
            background="#e0f2fe",   
            borderwidth=0,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#bae6fd")],
        )

        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 10),
            padding=8,
            foreground="#ffffff",
            background="#f87171",   
            borderwidth=0,
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#dc2626")],
        )

        style.configure(
            "Ghost.TButton",
            font=("Segoe UI", 10),
            padding=8,
            foreground="#1e3a8a",
            background="#f3f4f6",
            borderwidth=0,
        )
        style.map(
            "Ghost.TButton",
            background=[("active", "#e5e7eb")],
        )

        style.configure(
            "Chip.TButton",
            font=("Segoe UI", 9),
            padding=(14, 4),
            foreground="#334155",
            background="#e2e8f0",
            borderwidth=0,
        )
        style.map(
            "Chip.TButton",
            background=[("active", "#cbd5e1")],
        )

        # Dialog-pop up
        style.configure(
            "Dialog.TFrame",
            background="#ffffff",
        )
        style.configure(
            "DialogHeader.TFrame",
            background="#eff6ff",
        )
        style.configure(
            "DialogTitle.TLabel",
            font=("Segoe UI Semibold", 12),
            foreground="#1f2937",
            background="#eff6ff",
        )
        style.configure(
            "FormLabel.TLabel",
            font=("Segoe UI", 10),
            foreground="#4b5563",
            background="#ffffff",
        )


        # Bảng Treeview 
        style.configure(
            "Modern.Treeview",
            background="#ffffff",
            foreground="#111827",
            fieldbackground="#ffffff",
            rowheight=30,
            borderwidth=1,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#f3f4f6",
            foreground="#111827",
            font=("Segoe UI Semibold", 10),
            relief="flat",
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", "#e0edff")],
            foreground=[("selected", "#111827")],
        )

        # thanh cuộn dọc
        style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            background="#d1d5db",
            darkcolor="#9ca3af",
            lightcolor="#e5e7eb",
            troughcolor="#f3f4f6",
            bordercolor="#f3f4f6",
            arrowcolor="#6b7280",
            relief="flat",
        )

        style.layout("Modern.Treeview", style.layout("Treeview"))

    #Mini Calendar
    def _build_mini_calendar(self, parent):
        header = ttk.Frame(parent, style="CardInner.TFrame")
        header.pack(fill="x", pady=(4, 2))

        self.month_label_var = tk.StringVar()
        btn_prev = ttk.Button(
            header,
            text="◀",
            width=3,
            style="Chip.TButton",
            command=self._prev_month,
        )
        btn_prev.pack(side="left", padx=(0, 4))

        month_lbl = ttk.Label(
            header,
            textvariable=self.month_label_var,
            style="CardTitle.TLabel",
        )
        month_lbl.pack(side="left")

        btn_next = ttk.Button(
            header,
            text="▶",
            width=3,
            style="Chip.TButton",
            command=self._next_month,
        )
        btn_next.pack(side="left", padx=(4, 0))

        # Grid ngày
        grid = ttk.Frame(parent, style="CardInner.TFrame")
        grid.pack(pady=(4, 8))

        # tiêu đề thứ
        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, wd in enumerate(weekdays):
            lbl = ttk.Label(
                grid,
                text=wd,
                style="Subtle.TLabel",
            )
            lbl.grid(row=0, column=col, padx=2, pady=2)

        # ô ngày
        self.calendar_cells = []
        for r in range(6):
            row_cells = []
            for c in range(7):
                lbl = tk.Label(
                    grid,
                    text="",
                    font=("Nunito 10", 9),
                    width=3,
                    height=1,
                    bg="#ffffff",
                    fg="#111827",
                )
                lbl.grid(row=r + 1, column=c, padx=2, pady=2)
                lbl.bind("<Button-1>", self._on_calendar_day_click)
                lbl.date = None
                row_cells.append(lbl)
            self.calendar_cells.append(row_cells)

        self._render_calendar()

    # Render lại lịch mini
    def _render_calendar(self):
        self.month_label_var.set(
            f"{calendar.month_name[self.current_month]} {self.current_year}"
        )

        cal = calendar.Calendar(firstweekday=0)  # Monday=0
        month_matrix = cal.monthdayscalendar(self.current_year, self.current_month)

        for r in range(6):
            for c in range(7):
                lbl = self.calendar_cells[r][c]
                day = month_matrix[r][c] if r < len(month_matrix) else 0

                if day == 0:
                    lbl.config(text="", bg="#ffffff", fg="#d1d5db")
                    lbl.date = None
                else:
                    d = date(self.current_year, self.current_month, day)
                    lbl.date = d
                    lbl.config(text=str(day))

                    # default
                    bg = "#ffffff"
                    fg = "#111827"

                    if d == self.selected_date:
                        bg = "#2563eb"
                        fg = "#ffffff"
                    elif d == date.today():
                        bg = "#e0edff"
                        fg = "#1d4ed8"

                    lbl.config(bg=bg, fg=fg)

    def _on_calendar_day_click(self, event):
        d = getattr(event.widget, "date", None)
        if d is None:
            return
        self.selected_date = d
        self._render_calendar()
        self._apply_view_filter()

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._render_calendar()

    def _on_today_clicked(self):
        today = date.today()
        self.selected_date = today
        self.current_year = today.year
        self.current_month = today.month
        self.view_mode.set("day")
        self._render_calendar()
        self._apply_view_filter()

    def _set_view_mode(self, mode: str):
        self.view_mode.set(mode)
        self._apply_view_filter()

    def _update_selected_date_label(self):
        self.selected_date_label.config(
            text=f"Ngày được chọn: {self.selected_date.strftime('%Y-%m-%d')}  •  View: {self.view_mode.get().capitalize() if self.view_mode.get() != 'all' else 'All'}"
        )

    def _apply_view_filter(self):
        events = self.db.get_all_events()
        mode = self.view_mode.get()
        sd = self.selected_date

        if mode == "day":
            events = [e for e in events if e.start_time.date() == sd]
        elif mode == "week":
            start_week = sd - timedelta(days=sd.weekday())
            end_week = start_week + timedelta(days=6)
            events = [e for e in events if start_week <= e.start_time.date() <= end_week]
        elif mode == "month":
            events = [
                e
                for e in events
                if e.start_time.year == sd.year and e.start_time.month == sd.month
            ]
        self._reload_treeview(events)
        self._update_selected_date_label()

    # Tải lại dữ liệu bảng sự kiện
    def _reload_treeview(self, events=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if events is None:
            events = self.db.get_all_events()

        for idx, event in enumerate(events):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                values=(
                    event.id,
                    event.event,
                    event.start_time.isoformat(),
                    event.end_time.isoformat() if event.end_time else "",
                    event.location or "",
                    event.reminder_minutes,
                ),
                tags=(tag,),
            )

    # Xử lý nút Thêm sự kiện
    def _on_add_event_clicked(self):
        text = self.txt_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung sự kiện.")
            return

        try:
            from nlp.engine import parse_natural_input

            parsed_data = parse_natural_input(text)

            event = Event(
                id=None,
                event=parsed_data["event"],
                start_time=datetime.fromisoformat(parsed_data["start_time"]),
                end_time=datetime.fromisoformat(parsed_data["end_time"])
                if parsed_data["end_time"]
                else None,
                location=parsed_data["location"],
                reminder_minutes=parsed_data["reminder_minutes"],
            )

            self.db.add_event(event)
            self._apply_view_filter()
            messagebox.showinfo("Thông báo", "Thêm sự kiện thành công.")
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Không thể phân tích thời gian: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

    # Xử lý nút Sửa sự kiện
    def _on_edit_event_clicked(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sự kiện để sửa.")
            return

        item = self.tree.item(selected_item[0])
        event_id = item["values"][0]
        event = next((e for e in self.db.get_all_events() if e.id == event_id), None)

        if not event:
            messagebox.showerror("Lỗi", "Không tìm thấy sự kiện.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Chỉnh sửa sự kiện")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg="#e5e7eb")
        dialog.resizable(False, False)

        # Khung chính
        main_frame = ttk.Frame(dialog, style="Dialog.TFrame")
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Header
        header = ttk.Frame(main_frame, style="DialogHeader.TFrame")
        header.pack(fill="x", pady=(0, 10))

        # Body
        body = ttk.Frame(main_frame, style="Dialog.TFrame")
        body.pack(fill="x")

        for i in range(4):
            body.grid_columnconfigure(i, weight=1)

        ttk.Label(body, text="Tên sự kiện", style="FormLabel.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        event_name_entry = ttk.Entry(body)
        event_name_entry.insert(0, event.event)
        event_name_entry.grid(
            row=0, column=1, columnspan=3, padx=8, pady=(4, 6), sticky="ew"
        )

        ttk.Label(body, text="Bắt đầu", style="FormLabel.TLabel").grid(
            row=1, column=0, sticky="w", padx=8, pady=2
        )
        start_date_entry = ttk.Entry(body, width=12)
        start_time_entry = ttk.Entry(body, width=8)
        start_date_entry.insert(0, event.start_time.strftime("%Y-%m-%d"))
        start_time_entry.insert(0, event.start_time.strftime("%H:%M"))
        start_date_entry.grid(row=1, column=1, padx=(8, 4), pady=2, sticky="w")
        start_time_entry.grid(row=1, column=2, padx=(4, 8), pady=2, sticky="w")

        ttk.Label(body, text="Kết thúc", style="FormLabel.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=2
        )
        end_date_entry = ttk.Entry(body, width=12)
        end_time_entry = ttk.Entry(body, width=8)
        if event.end_time:
            end_date_entry.insert(0, event.end_time.strftime("%Y-%m-%d"))
            end_time_entry.insert(0, event.end_time.strftime("%H:%M"))
        end_date_entry.grid(row=2, column=1, padx=(8, 4), pady=2, sticky="w")
        end_time_entry.grid(row=2, column=2, padx=(4, 8), pady=2, sticky="w")

        ttk.Label(body, text="Địa điểm", style="FormLabel.TLabel").grid(
            row=3, column=0, sticky="w", padx=8, pady=2
        )
        location_entry = ttk.Entry(body)
        location_entry.insert(0, event.location or "")
        location_entry.grid(
            row=3, column=1, columnspan=3, padx=8, pady=2, sticky="ew"
        )

        ttk.Label(body, text="Nhắc trước (phút)", style="FormLabel.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(2, 4)
        )
        reminder_entry = ttk.Entry(body, width=10)
        reminder_entry.insert(0, str(event.reminder_minutes))
        reminder_entry.grid(row=4, column=1, padx=8, pady=(2, 4), sticky="w")

        # Lưu thay đổi
        def save_changes():
            try:
                name = event_name_entry.get().strip()
                loc = location_entry.get().strip()
                reminder_val = int(reminder_entry.get().strip() or "0")

                sd = start_date_entry.get().strip()
                st = start_time_entry.get().strip()
                start_dt = datetime.fromisoformat(f"{sd}T{st}")

                end_dt = None
                ed = end_date_entry.get().strip()
                et = end_time_entry.get().strip()
                if ed and et:
                    end_dt = datetime.fromisoformat(f"{ed}T{et}")

                updated_event = Event(
                    id=event.id,
                    event=name,
                    start_time=start_dt,
                    end_time=end_dt,
                    location=loc,
                    reminder_minutes=reminder_val,
                )
                self.db.update_event(updated_event)
                self._apply_view_filter()
                dialog.destroy()
                messagebox.showinfo("Thông báo", "Sửa sự kiện thành công.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu thay đổi: {e}")

        # Footer nút
        btn_frame = ttk.Frame(main_frame, style="Dialog.TFrame")
        btn_frame.pack(fill="x", pady=(12, 0))

        ttk.Button(
            btn_frame,
            text="Hủy",
            style="Ghost.TButton",
            command=dialog.destroy,
        ).pack(side="right", padx=6)

        ttk.Button(
            btn_frame,
            text="💾  Lưu",
            style="Primary.TButton",
            command=save_changes,
        ).pack(side="right", padx=6)

    # Xử lý nút xoá sự kiện
    def _on_delete_event_clicked(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một sự kiện để xóa.")
            return

        if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sự kiện này?"):
            return

        item = self.tree.item(selected_item[0])
        event_id = item["values"][0]

        try:
            self.db.delete_event(event_id)
            self._apply_view_filter()
            messagebox.showinfo("Thông báo", "Xóa sự kiện thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa sự kiện: {e}")

    # Xử lý nút tìm kiếm
    def _on_search_clicked(self):
        search_text = self.search_entry.get().strip().lower()
        events = self.db.get_all_events()

        if search_text:
            filtered_events = []
            for event in events:
                if search_text in event.event.lower():
                    filtered_events.append(event)
                try:
                    search_date = datetime.fromisoformat(search_text).date()
                    if event.start_time.date() == search_date:
                        filtered_events.append(event)
                except ValueError:
                    pass
            self._reload_treeview(filtered_events)
        else:
            self._apply_view_filter()

    def _on_clear_search_clicked(self):
        self.search_entry.delete(0, tk.END)
        self._apply_view_filter()

    # Hiển thị popup nhắc nhở sự kiện
    def show_reminder_popup(self, event):
        # Âm thanh nhắc nhở
        winsound.Beep(1000, 500)
        win = tk.Toplevel(self)
        win.title("Nhắc nhở sự kiện")
        win.transient(self)
        win.grab_set()
        win.configure(bg="#e5e7eb")
        win.resizable(False, False)

        container = ttk.Frame(win, style="Dialog.TFrame")
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Header
        header = ttk.Frame(container, style="DialogHeader.TFrame")
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text="⏰  Nhắc nhở sự kiện",
            style="DialogTitle.TLabel",
        ).pack(side="left", padx=10, pady=8)

        # Nội dung
        body = ttk.Frame(container, style="Dialog.TFrame")
        body.pack(fill="x")

        ttk.Label(
            body,
            text=event.event,
            font=("Segoe UI Semibold", 11),
            foreground="#111827",
            background="#ffffff",
        ).pack(anchor="w", padx=10, pady=(0, 6))

        ttk.Label(
            body,
            text=f"Thời gian: {event.start_time.strftime('%Y-%m-%d %H:%M')}",
            style="FormLabel.TLabel",
        ).pack(anchor="w", padx=10, pady=2)

        ttk.Label(
            body,
            text=f"Địa điểm: {event.location or 'Không có'}",
            style="FormLabel.TLabel",
        ).pack(anchor="w", padx=10, pady=(2, 8))

        # Footer
        footer = ttk.Frame(container, style="Dialog.TFrame")
        footer.pack(fill="x", pady=(10, 0))

        ttk.Button(
            footer,
            text="Đã hiểu",
            style="Primary.TButton",
            command=win.destroy,
        ).pack(side="right", padx=8)
 
    # Xuất sự kiện ra file .ics
    def _export_events_as_ics(self):
        try:
            events: list[Event] = self.db.get_all_events()
        except AttributeError:
            # Nếu DB dùng API khác, chỉnh lại cho đúng
            events = self.db.list_events()

        if not events:
            messagebox.showwarning("Xuất ICS", "Không có sự kiện nào để xuất.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar files", "*.ics"), ("All files", "*.*")]
        )
        if not file_path:
            return

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//PersonalScheduleAssistant//EN",
        ]

        for ev in events:
            start = getattr(ev, "start_time", None)
            if not start:
                continue

            end = getattr(ev, "end_time", None) or start

            dt_start = start.strftime("%Y%m%dT%H%M%S")
            dt_end = end.strftime("%Y%m%dT%H%M%S")

            summary = getattr(ev, "title", None) or getattr(ev, "name", None) or getattr(ev, "event", "Sự kiện")
            location = getattr(ev, "location", "") or ""
            reminder = getattr(ev, "reminder_minutes", None)

            uid = f"{int(start.timestamp())}-{hash(summary)}@personalschedule"

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART:{dt_start}",
                f"DTEND:{dt_end}",
                f"SUMMARY:{summary}",
                f"LOCATION:{location}",
            ])

            if reminder:
                try:
                    minutes = int(reminder)
                    lines.extend([
                        "BEGIN:VALARM",
                        f"TRIGGER:-PT{minutes}M",
                        "ACTION:DISPLAY",
                        f"DESCRIPTION:Nhắc nhở - {summary}",
                        "END:VALARM",
                    ])
                except (TypeError, ValueError):
                    pass

            lines.append("END:VEVENT")

        lines.append("END:VCALENDAR")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\r\n".join(lines))
            messagebox.showinfo("Xuất ICS", f"Đã xuất lịch trình ra:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi file ICS:\n{e}")

    def _on_export_ics_clicked(self):
        self._export_events_as_ics()