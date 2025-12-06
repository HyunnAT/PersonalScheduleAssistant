import re
from typing import List
from underthesea import word_tokenize, text_normalize

# Bảng chuyển dấu cho các thủ công
ACCENT_MAP = {
    "hop": "họp","nhom": "nhóm",
    "gio": "giờ","phut": "phút",
    "phong": "phòng","truoc": "trước",
    "tuan nay": "tuần này",
    "tuan sau": "tuần sau",
    "tuần nay": "tuần này", 
    "tuần sau": "tuần sau",
    "o": "ở","vao": "vào",
    "luc": "lúc","nhac": "nhắc",
    "toi": "tôi","truoc": "trước","ngay": "ngày",

    # ngày trong tuần
    "thu hai": "thứ hai",
    "thu ba": "thứ ba",
    "thu tu": "thứ tư",
    "thu nam": "thứ năm",
    "thu sau": "thứ sáu",
    "thu bay": "thứ bảy",
    "chu nhat": "chủ nhật",

    # phiên bản dính liền
    "thuhai": "thứ hai",
    "thuba": "thứ ba",
    "thutu": "thứ tư",
    "thunam": "thứ năm",
    "thusau": "thứ sáu",
    "thubay": "thứ bảy",
    "chunhat": "chủ nhật",
}

# Hàm áp dụng bảng chuyển dấu
def apply_accent_mapping(text: str) -> str:
    for k, v in ACCENT_MAP.items():
        text = re.sub(rf"\b{k}\b", v, text)
    return text


def normalize_text(text: str) -> str:
    text = text.strip().lower()

    # B1: normalize cơ bản của underthesea
    text = text_normalize(text)

    # B2: áp dụng bảng chuyển dấu
    text = apply_accent_mapping(text)

    # B3: loại ký tự đặc biệt, giữ lại chữ, số, khoảng trắng, :, /, -
    text = re.sub(r"[^\w\s:/-]", "", text)

    # B4: loại nhiều khoảng trắng
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text: str) -> List[str]:
    return word_tokenize(normalize_text(text))
