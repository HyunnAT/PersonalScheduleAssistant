from typing import Dict, List
import re
from underthesea import ner


def extract_entities(text: str) -> Dict[str, List[str]]:

    times = []
    locations = []

    tagged = ner(text)

    # 1) LẤY KẾT QUẢ NER BAN ĐẦU
    for item in tagged:
        token = item[0]
        label = item[-1]

        if label == "TIME":
            times.append(token)

        if label == "LOC":
            locations.append(token)

    # 2) BỔ SUNG LOCATION RULE-BASED
    location_patterns = [
        r"phòng\s+[a-zA-ZÀ-Ỵà-ỵ0-9]+\s*\d*",      
        r"phòng\s+\d+", 
        r"p\.\s*\d+",
        r"lầu\s*\d+",
        r"tầng\s*\d+",
        r"thư viện\s+[a-zA-ZÀ-Ỵà-ỵ0-9]+\s*\d*",
        r"phòng\s+[a-zA-ZÀ-Ỵà-ỵ0-9\s]+",
        r"nhà\s*[a-zA-Z0-9]+",
        r"nhà\s+[a-zA-ZÀ-Ỵà-ỵ0-9\s]+",
        r"hội trường\s+[a-zA-ZÀ-Ỵà-ỵ0-9\s]+",
        r"căn tin", r"trường học",
        r"công ty", r"văn phòng",
        r"căng tin", r"siêu thị",
        r"quán\s+[a-zA-ZÀ-Ỵà-ỵ0-9\s]+",
        r"khoa\s+[a-zA-ZÀ-Ỵà-ỵ0-9\s]+",
        r"bệnh viện\s+[a-zA-ZÀ-Ỵà-ỵ0-9\s]+"
    ]

    for p in location_patterns:
        matches = re.findall(p, text, flags=re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()
            if cleaned.lower() not in [loc.lower() for loc in locations]:
                locations.append(cleaned)

    # 3) Tăng cường regex TIME — FULL MATCHING
    time_patterns = [
        r"\b\d{1,2}\s*giờ(?:\s*\d{1,2}\s*phút)?(?:\s*ngày\s*\d{1,2}[-/]\d{1,2}[-/]\d{4})?",  # 9 giờ, 9 giờ 30 phút, 9 giờ ngày 2/10/2023
        r"\b\d{1,2}h\d{1,2}\b(?:\s*ngày\s*\d{1,2}[-/]\d{1,2}[-/]\d{4})?",                   # 9h30 ngày 2/10/2023
        r"\b\d{1,2}h\b(?:\s*ngày\s*\d{1,2}[-/]\d{1,2}[-/]\d{4})?",                          # 9h ngày 2/10/2023
        r"\b\d{1,2}:\d{1,2}\b(?:\s*ngày\s*\d{1,2}[-/]\d{1,2}[-/]\d{4})?",                   # 09:30 ngày 2/10/2023
        r"\bngày\s*\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",  # ngày 2/10/2023
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",  # 2/10/2023
        r"\b\d{1,2}\s*h\s*\d{1,2}\b",
        r"\b\d{1,2}\s*h\b",
        r"\b\d{1,2}\s*:\s*\d{1,2}\b",
        r"sáng mai", r"chiều mai", r"tối mai",
        r"sáng nay", r"chiều nay", r"tối nay",
        r"trưa nay", r"trưa mai", r"đêm nay",
        r"sang mai", r"chieu mai", r"toi mai",
        r"sang nay", r"chieu nay", r"toi nay",
        r"trua nay", r"trua mai", r"dem nay",
        r"thứ\s+\w+\s+tuần\s+(này|nay|sau)",
        r"thứ\s*\d", r"tuần này", r"tuần sau", r"cuối tuần",
        r"thứ\s*(hai|ba|tư|tu|năm|nam|sáu|sau|bảy|bay)",
        r"chủ nhật", r"chu nhat",r"cn"

    ]

    for p in time_patterns:
        matches = re.findall(p, text, flags=re.IGNORECASE)
        for m in matches:
            # nếu pattern có nhóm (), m có thể là tuple → join về string
            if isinstance(m, tuple):
                cleaned = " ".join([x for x in m if x]).strip()
            else:
                cleaned = str(m).strip()
            if cleaned and cleaned.lower() not in [t.lower() for t in times]:
                times.append(cleaned)

    # Chuẩn hóa
    times = _normalize_list(times)
    locations = _normalize_list(locations)

    # 4) GHÉP TIME: (ví dụ "9 giờ" + "sáng mai")

    hour_patterns = [
        r"\b\d{1,2}\s*giờ\b",
        r"\b\d{1,2}\s*h\s*\d{1,2}\b",  # 10h30 hoặc 10 h30
        r"\b\d{1,2}\s*h\b",            # 10h hoặc 10 h
        r"\b\d{1,2}\s*:\s*\d{1,2}\b",  # 10:30 hoặc 10 : 30
    ]

    weekday_keywords = [
        "thứ 2", "thứ 3", "thứ 4", "thứ 5",
        "thứ 6", "thứ 7", "chủ nhật",
    ]

    week_keywords = ["tuần này", "tuần sau", "cuối tuần"]

    other_day_keywords = [
        "sáng mai", "chiều mai", "tối mai",
        "sáng nay", "chiều nay", "tối nay",
        "trưa nay", "trưa mai", "đêm nay",
        "sang mai", "chieu mai", "toi mai",
        "sang nay", "chieu nay", "toi nay",
        "trua nay", "trua mai", "dem nay",
    ]

    hour_part = None
    weekday_part = None
    week_part = None
    other_day_part = None
    has_any_hour = False 

    for t in times:
        lower = t.lower()

        # tìm phần giờ
        for hp in hour_patterns:
            if re.search(hp, lower):
                hour_part = t
                has_any_hour = True

        # tìm thứ (thứ 5, thứ 3, chủ nhật...)
        for wd in weekday_keywords:
            if wd in lower:
                weekday_part = wd

        # tìm từ khóa tuần (tuần này, tuần sau, cuối tuần)
        for wk in week_keywords:
            if wk in lower:
                week_part = wk

        # tìm các từ khóa buổi/ngày khác (sáng mai, chiều nay,...)
        for od in other_day_keywords:
            if od in lower:
                other_day_part = od

    # Tạo cụm day_phrase
    day_phrase = None
    if weekday_part and week_part:
        day_phrase = f"{weekday_part} {week_part}"      # "thứ 5 tuần này"
    elif weekday_part:
        day_phrase = weekday_part                       # "thứ 5"
    elif other_day_part:
        day_phrase = other_day_part                     # "sáng mai" / "đêm nay"
    elif week_part:
        day_phrase = week_part                          # "tuần này"

    # nếu có cả giờ lẫn ngày → ghép
    if hour_part and day_phrase:
        combined = f"{hour_part} {day_phrase}"          # "22h đêm nay"
        if combined.lower() not in [t.lower() for t in times]:
            times.append(combined)
        # ưu tiên combined lên đầu
        times = [combined] + [t for t in times if t != combined]

    return {
        "times": times,
        "locations": locations
    }

def _normalize_list(values: List[str]) -> List[str]:
    """Loại trùng lặp, strip khoảng trắng, giữ thứ tự."""
    cleaned = []
    for v in values:
        v = v.strip()
        if v and v not in cleaned:
            cleaned.append(v)
    return cleaned


def _is_valid_time_string(s: str) -> bool:

    patterns = [
        r"^\d{1,2}h\d{1,2}$",     # 10h30
        r"^\d{1,2}h$",            # 10h
        r"^\d{1,2}:\d{1,2}$",     # 10:30
    ]

    for p in patterns:
        if re.match(p, s):
            return True
    return False
