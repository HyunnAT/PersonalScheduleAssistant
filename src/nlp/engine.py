from datetime import datetime
from typing import Optional, Dict, Any
import re

from nlp.preprocessing import normalize_text
from nlp.ner import extract_entities
from nlp.rules import extract_event_name, extract_reminder_minutes
from nlp.time_parsing import parse_time_expression

# Kiểm tra biểu thức có chứa giờ không
def _has_hour(expr: str) -> bool:
    expr = expr.lower()
    if re.search(r"\b\d{1,2}\s*giờ\b", expr):
        return True
    if re.search(r"\b\d{1,2}\s*h\b", expr):
        return True
    if re.search(r"\b\d{1,2}\s*:\s*\d{1,2}\b", expr):
        return True
    return False

# Hàm chính để phân tích câu nhập tự nhiên
def parse_natural_input(text: str, now: Optional[datetime] = None):

    if now is None:
        now = datetime.now()

    # STEP 1 — Tiền xử lý
    normalized = normalize_text(text)
    print("DEBUG: normalized =", normalized)

    # STEP 2 — NER
    entities = extract_entities(normalized)
    print("DEBUG: entities =", entities)
    times = entities.get("times", [])
    locations = entities.get("locations", [])

    # STEP 3 — Tên sự kiện
    event_name = extract_event_name(text, times, locations)
    print("DEBUG: event_name =", event_name)

    # STEP 4 — Reminder
    reminder_minutes = extract_reminder_minutes(text)
    print("DEBUG: reminder_minutes =", reminder_minutes)

    # STEP 5 — Thời gian bắt đầu và kết thúc
    start_time = None
    end_time = None

    text_lower = text.lower()
    time_expr_for_start = None

    has_from_to = ("từ" in text_lower) and any(kw in text_lower for kw in ["đến", "den", "tới", "toi"])

    # ==== TRƯỜNG HỢP "TỪ ... ĐẾN ..." =====
    if has_from_to and len(times) >= 2:
        # Lấy các biểu thức có giờ
        hour_exprs = [t for t in times if _has_hour(t)]

        # Hàm lấy số giờ (đơn giản chỉ cần giờ, phút xử lý trong time_parsing)
        def _extract_hour(s: str) -> int:
            m = re.search(r"(\d{1,2})", s)
            return int(m.group(1)) if m else 0

        start_expr = None
        end_expr = None

        if len(hour_exprs) >= 2:
            # sort theo giờ tăng dần
            sorted_by_hour = sorted(hour_exprs, key=_extract_hour)
            start_expr = sorted_by_hour[0]  # giờ nhỏ hơn
            end_expr = sorted_by_hour[1]    # giờ lớn hơn
        else:
            # fallback: dùng times[0], times[1]
            start_expr = times[0]
            end_expr = times[1] if len(times) > 1 else times[0]

        print("DEBUG: từ/đến → start_expr:", start_expr, "end_expr:", end_expr)
        # parse start theo now
        start_time = parse_time_expression(start_expr, now=now)
        print("DEBUG: start_time =", start_time)
        # parse end theo now
        end_time = parse_time_expression(end_expr, now=now)
        print("DEBUG: end_time =", end_time)

    else:
        if any(
            kw in text_lower
            for kw in ["thứ", "chu nhat", "chủ nhật", "cuối tuần", "cuoi tuan", "tuần", "tuan", "cn"]
        ):
            time_expr_for_start = text_lower
        elif times:
            # Ưu tiên cụm có cả ngày + giờ
            for t in times:
                tl = t.lower()
                if "ngày" in tl and _has_hour(t):
                    time_expr_for_start = t
                    break

            # Nếu chưa tìm được: ưu tiên cụm chỉ có giờ
            if time_expr_for_start is None:
                for t in times:
                    if _has_hour(t):
                        time_expr_for_start = t
                        break

            # Nếu vẫn chưa có: dùng phần tử đầu tiên
            if time_expr_for_start is None:
                time_expr_for_start = times[0]

        # Nối thêm ngày nếu có giờ nhưng thiếu ngày
        if time_expr_for_start and _has_hour(time_expr_for_start):
            date_piece = None
            for t in times:
                tl = t.lower()
                if "ngày" in tl:
                    date_piece = t
                    break
                if re.search(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b", tl):
                    date_piece = t
                    break

            if date_piece and "ngày" not in time_expr_for_start.lower():
                if not date_piece.lower().startswith("ngày"):
                    date_piece = "ngày " + date_piece
                time_expr_for_start = f"{time_expr_for_start} {date_piece}"

        if time_expr_for_start:
            print("DEBUG: Đang xử lý thời gian bắt đầu:", time_expr_for_start)
            start_time = parse_time_expression(time_expr_for_start, now=now)
            print("DEBUG: start_time =", start_time)

    if start_time is None:
        raise ValueError("Không thể phân tích thời gian")

    return {
        "event": event_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat() if end_time else None,
        "location": locations[0] if locations else None,
        "reminder_minutes": reminder_minutes,
    }