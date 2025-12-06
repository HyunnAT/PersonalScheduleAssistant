from underthesea import word_tokenize
import dateparser
import re
from datetime import datetime, timedelta
from typing import Optional


def parse_time_expression(expr: str, now: Optional[datetime] = None) -> Optional[datetime]:

    if now is None:
        now = datetime.now()

    expr = expr.strip().lower()

    # 1) CHUẨN HÓA CÂU
    normalization_map = {
        # giờ/phút không dấu
        " gio": " giờ","gio ": "giờ ",
        " phut": " phút","phut ": "phút ",

        # tuần
        "tuan nay": "tuần này",
        "tuan sau": "tuần sau",

        # thứ + số/ chữ
        "thu hai": "thứ 2","thu ba": "thứ 3",
        "thu tu": "thứ 4","thu bon": "thứ 4",
        "thu nam": "thứ 5","thu 5": "thứ 5",
        "thu sau": "thứ 6","thu 6": "thứ 6",
        "thu bay": "thứ 7","thu 7": "thứ 7",

        # chủ nhật / cuối tuần
        "chu nhat": "chủ nhật",
        "cn": "chủ nhật",
        "cuoi tuan": "chủ nhật",

        # viết có dấu 
        "thứ năm": "thứ 5",
        "thu nam": "thứ 5",
        "cuối tuần": "chủ nhật",

        #các buổi
        "sang mai": "sáng mai","chieu mai": "chiều mai",
        "toi mai": "tối mai","trua mai": "trưa mai",
        "sang nay": "sáng nay","chieu nay": "chiều nay",
        "toi nay": "tối nay","trua nay": "trưa nay", "hom nay": "hôm nay"
    }
    for k, v in normalization_map.items():
        expr = expr.replace(k, v)


    # 1) có cả ngày và giờ cụ thể
    m = re.search(
        r"(\d{1,2})\s*[:h]\s*(\d{1,2})\s*ngày\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})",
        expr,
    )
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        day = int(m.group(3))
        month = int(m.group(4))
        year = int(m.group(5))
        return datetime(year, month, day, hour, minute, 0)

    # 2) "X giờ ngày 2/10/2023"
    m = re.search(
        r"(\d{1,2})\s*(?:giờ|h)?\s*ngày\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})",
        expr,
    )
    if m:
        hour = int(m.group(1))
        day = int(m.group(2))
        month = int(m.group(3))
        year = int(m.group(4))
        return datetime(year, month, day, hour, 0, 0)

    # Xử lý "X giờ chủ nhật nay/này"
    m = re.search(r"(\d{1,2})\s*giờ.*chủ nhật\s*(nay|này)", expr)
    if m:
        hour = int(m.group(1))
        minute = 0

        current_idx = now.weekday()
        target_idx = 6  # chủ nhật
        days_ahead = (target_idx - current_idx + 7) % 7

        target_date = now + timedelta(days=days_ahead)
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    m = re.search(r"chủ nhật\s*(nay|này)", expr)
    if m:
        current_idx = now.weekday()
        target_idx = 6
        days_ahead = (target_idx - current_idx + 7) % 7
        target_date = now + timedelta(days=days_ahead)
        return target_date.replace(hour=8, minute=0, second=0, microsecond=0)

    # Xử lý "X giờ chủ nhật"
    m = re.search(r"(\d{1,2})\s*(?:giờ|h|:\s*\d{1,2})?.*chủ nhật\b", expr)
    if m:
        hour = int(m.group(1))
        m_min = re.search(rf"{hour}\s*[:h]\s*(\d{{1,2}})", expr)
        minute = int(m_min.group(1)) if m_min else 0

        current_idx = now.weekday()
        target_idx = 6  # chủ nhật
        days_ahead = (target_idx - current_idx + 7) % 7
        if days_ahead == 0:
            days_ahead = 7  # nếu hôm nay là chủ nhật, sang CN tuần sau

        target_date = now + timedelta(days=days_ahead)
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Chỉ "chủ nhật"
    m = re.search(r"\bchủ nhật\b", expr)
    if m:
        current_idx = now.weekday()
        target_idx = 6
        days_ahead = (target_idx - current_idx + 7) % 7
        if days_ahead == 0:
            days_ahead = 7

        target_date = now + timedelta(days=days_ahead)
        return target_date.replace(hour=8, minute=0, second=0, microsecond=0)

    # "X giờ ngày 2/10/2023"
    m = re.search(r"(\d{1,2})\s*giờ\s*ngày\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})", expr)
    if m:
        hour = int(m.group(1))
        day = int(m.group(2))
        month = int(m.group(3))
        year = int(m.group(4))
        return datetime(year, month, day, hour, 0, 0)

    # "ngày 2/10/2023"
    m = re.search(r"ngày\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})", expr)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3))
        return datetime(year, month, day, 6, 0, 0)

    # "2/10/2023"
    m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", expr)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3))
        return datetime(year, month, day, 6, 0, 0)
    
    # Tìm thứ
    weekday_pattern = r"thứ\s+(2|3|4|5|6|7|hai|ba|tư|tu|bốn|bon|năm|nam|sáu|sau|bảy|bay)"
    m_wd = re.search(weekday_pattern, expr)
    if m_wd:
        wd_str = m_wd.group(1)

        weekday_map = {
            "2": 0, "hai": 0,
            "3": 1, "ba": 1,
            "4": 2, "tư": 2, "tu": 2, "bốn": 2, "bon": 2,
            "5": 3, "năm": 3, "nam": 3,
            "6": 4, "sáu": 4, "sau": 4,
            "7": 5, "bảy": 5, "bay": 5,
            "chủ nhật": 6,
        }
        if wd_str in weekday_map:
            target_idx = weekday_map[wd_str]
            current_idx = now.weekday()
            hour = None
            minute = 0

            # 10 giờ / 10 giờ 30 phút
            m_h = re.search(r"(\d{1,2})\s*giờ(\s*(\d{1,2})\s*phút)?", expr)
            if m_h:
                hour = int(m_h.group(1))
                if m_h.group(3):
                    minute = int(m_h.group(3))
            else:
                # 10h30
                m_h = re.search(r"(\d{1,2})h(\d{1,2})", expr)
                if m_h:
                    hour = int(m_h.group(1))
                    minute = int(m_h.group(2))
                else:
                    # 10h
                    m_h = re.search(r"(\d{1,2})h\b", expr)
                    if m_h:
                        hour = int(m_h.group(1))
                    else:
                        # 10:00
                        m_h = re.search(r"(\d{1,2}):(\d{1,2})", expr)
                        if m_h:
                            hour = int(m_h.group(1))
                            minute = int(m_h.group(2))

            if hour is not None:
                days_ahead = (target_idx - current_idx + 7) % 7
                # Nếu là hôm nay, chuyển sang tuần sau
                if "tuần sau" in expr:
                    days_ahead += 7

                target_date = now + timedelta(days=days_ahead)
                return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # 2) CÁC ĐỊNH DẠNG GIỜ THÔNG DỤNG
    # 10 giờ / 10 giờ 30 phút
    m = re.search(r"(\d{1,2})\s*giờ(\s*(\d{1,2})\s*phút)?", expr)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(3)) if m.group(3) else 0
        return _apply_tomorrow_if_needed(expr, now, hour, minute)

    # 10h30
    m = re.search(r"(\d{1,2})\s*h\s*(\d{1,2})", expr)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        return _apply_tomorrow_if_needed(expr, now, hour, minute)

    # 10h
    m = re.search(r"(\d{1,2})\s*h\b", expr)
    if m:
        hour = int(m.group(1))
        return _apply_tomorrow_if_needed(expr, now, hour, 0)

    # 10:00
    m = re.search(r"(\d{1,2})\s*:\s*(\d{1,2})", expr)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        return _apply_tomorrow_if_needed(expr, now, hour, minute)

    # 3) DÙNG dateparser 
    parsed = dateparser.parse(expr, settings={"RELATIVE_BASE": now})
    if parsed:
        return parsed

    # 4) XỬ LÝ TỪ KHÓA BUỔI TRONG NGÀY
    if "ngày mai" in expr:
        return now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if "sáng mai" in expr:
        return now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if "chiều mai" in expr:
        return now.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if "tối mai" in expr:
        return now.replace(hour=19, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if "trưa mai" in expr:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)

    if "sáng nay" in expr:
        return now.replace(hour=8, minute=0, second=0, microsecond=0)
    if "chiều nay" in expr:
        return now.replace(hour=15, minute=0, second=0, microsecond=0)
    if "tối nay" in expr:
        return now.replace(hour=19, minute=0, second=0, microsecond=0)
    if "trưa nay" in expr:
        return now.replace(hour=12, minute=0, second=0, microsecond=0)

    if "hôm nay" in expr:
        return now.replace(hour=8, minute=0, second=0, microsecond=0)
    print("DEBUG: parse_time_expression FAILED:", expr)
    return None


def _is_valid_time_string(s: str) -> bool:

    # keyword-based là valid
    keyword_list = [
        "sáng mai", "chiều mai", "tối mai", "trưa mai",
        "sáng nay", "chiều nay", "tối nay", "trưa nay"
    ]
    for k in keyword_list:
        if k in s:
            return True

    # regex-based valid time
    patterns = [
        r"\d{1,2}\s*giờ",
        r"\d{1,2}\s*giờ\s*\d{1,2}\s*phút",
        r"\d{1,2}h\d{1,2}",
        r"\d{1,2}h\b",
        r"\d{1,2}:\d{1,2}"
    ]

    for p in patterns:
        if re.search(p, s):
            return True

    return False

# Hàm phụ để quyết định ngày hôm nay hay ngày mai
def _apply_tomorrow_if_needed(expr: str, now: datetime, hour: int, minute: int) -> datetime:
    expr_low = expr.lower()
    dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if "mai" in expr_low:
        return dt + timedelta(days=1)

    if "nay" in expr_low:
        return dt

    if dt <= now:
        return dt + timedelta(days=1)

    return dt

