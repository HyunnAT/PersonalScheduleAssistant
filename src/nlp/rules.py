import re
from typing import List, Optional
from nlp.preprocessing import normalize_text

# 1) Trích số phút nhắc trước (reminder)
def extract_reminder_minutes(text: str) -> Optional[int]:

    t = text.lower()

    # 1) phút
    m = re.search(r"nhắc trước\s*(\d+)\s*(phút|phut)", t)
    if not m:
        m = re.search(r"(\d+)\s*(phút|phut)\b", t)
    if m:
        return int(m.group(1))

    # 2) tiếng / giờ
    m = re.search(r"nhắc trước\s*(\d+)\s*(tiếng|tieng|giờ|gio)", t)
    if not m:
        m = re.search(r"(\d+)\s*(tiếng|tieng|giờ|gio)\b", t)
    if m:
        return int(m.group(1)) * 60

    return None

# 2) Trích tên sự kiện (event_name)
def extract_event_name(
    original_text: str,
    times: List[str],
    locations: List[str],
    reminder_minutes: Optional[int] = None,
) -> str:

    # 1) Chuẩn hóa câu gốc
    text = normalize_text(original_text)  
    text = text.lower()

    # 2) Bỏ các cụm thời gian
    for t in times:
        if not t:
            continue
        nt = normalize_text(t).lower()
        if nt:
            text = text.replace(nt, " ")

    # 3) Bỏ các cụm địa điểm
    for loc in locations:
        if not loc:
            continue
        nl = normalize_text(loc).lower()
        if nl:
            text = text.replace(nl, " ")

    # 4) Bỏ cụm "nhắc trước X phút/giờ"
    text = re.sub(
        r"nh[aá]c\s+trước\s+\d+\s*(phút|phut|giờ|gio|tiếng|tieng)",
        " ",
        text,
    )

    # 5) Bỏ các số đơn lẻ
    text = re.sub(r"\b\d+\b", " ", text)

    # 6) Bỏ từ rác
    junk_words = [
        "nhắc", "nhac","tôi", "toi","tui",
        "lúc", "luc","nhớ","ở", "o", "tai", "tại",
        "trước", "truoc","từ","đến","phút", "phut", "tu","đen","giờ", "gio", "mai",
        "tiếng", "tieng","đặt","vào", "vao","tạo","tao",
        "ngày", "ngay","lịch","lich","thứ", "thu","tuần", "tuan",
        "nay", "này","sau", "sáng","năm", "nam",
    ]

    # Loại từ rác
    for w in junk_words:
        text = re.sub(rf"\b{w}\b", " ", text)

    # 7) Xóa dấu câu còn sót
    text = re.sub(r"[^\w\s]", " ", text)

    # 8) Gom khoảng trắng
    text = " ".join(text.split()).strip()

    # Nếu sau khi clean thành rỗng, fallback dùng câu gốc (nhưng đã normalize)
    if not text:
        text = normalize_text(original_text).strip()

    # 9) Viết hoa chữ cái đầu
    if text:
        text = text[0].upper() + text[1:]

    return text
