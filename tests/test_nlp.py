import sys
import os
from datetime import datetime

# Thêm thư mục `src` vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from nlp.engine import parse_natural_input


def run_tests():
    now = datetime(2025, 12, 1, 9, 0)  # Thứ Hai 1/12/2025, 09:00
    test_cases = [
        # 1. Cơ bản: giờ + địa điểm + nhắc phút
        (
            "họp lúc 15:45 ở phòng 302 nhắc trước 5 phút",
            {
                "event": "họp",
                "start_time": "2025-12-01T15:45:00",
                "location": "phòng 302",
                "reminder_minutes": 5,
            },
        ),
        # 2. Giờ nguyên + địa điểm
        (
            "nhắc tôi họp nhóm lúc 10 giờ sáng nay ở phòng A101, nhắc trước 15 phút",
            {
                "event": "họp nhóm",
                "start_time": "2025-12-01T10:00:00",
                "location": "phòng A101",
                "reminder_minutes": 15,
            },
        ),
        # 3. Sáng mai
        (
            "nhắc tui đi học lúc 7h sáng mai tại phòng 203",
            {
                "event": "đi học",
                "start_time": "2025-12-02T07:00:00",
                "location": "phòng 203",
            },
        ),
        # 4. Chiều nay
        (
            "tạo lịch họp với thầy lúc 15h chiều nay ở phòng họp 312",
            {
                "event": "họp với thầy",
                "start_time": "2025-12-01T15:00:00",
                "location": "phòng họp 312",
            },
        ),
        # 5. Tối nay
        (
            "nhắc tôi xem bóng đá lúc 20 giờ tối nay",
            {
                "event": "xem bóng đá",
                "start_time": "2025-12-01T20:00:00",
            },
        ),
        # 6. Thứ + tuần này
        (
            "đặt lịch họp nhóm vào 9h thứ 5 tuần này ở phòng 302",
            {
                "event": "họp nhóm",
                "start_time": "2025-12-04T09:00:00",
                "location": "phòng 302",
            },
        ),
        # 7. Thứ + tuần sau
        (
            "nhắc tôi đi khám bệnh 8 giờ thứ 3 tuần sau tại bệnh viện Chợ Rẫy",
            {
                "event": "đi khám bệnh",
                "start_time": "2025-12-09T08:00:00",
                "location": "bệnh viện Chợ Rẫy",
            },
        ),
        # 8. Ngày cụ thể dd/mm/yyyy
        (
            "tạo lịch thi cuối kỳ ngày 5/12/2025 lúc 9 giờ sáng",
            {
                "event": "thi cuối kỳ",
                "start_time": "2025-12-05T09:00:00",
            },
        ),
        # 9. Giờ trước, ngày sau
        (
            "họp báo cáo 14h ngày 10/12/2025 ở phòng 502",
            {
                "event": "họp báo cáo",
                "start_time": "2025-12-10T14:00:00",
                "location": "phòng 502",
            },
        ),
        # 10. Chỉ có thứ
        (
            "nhắc tôi họp nhóm 7 giờ thứ 4 tuần sau ở trường học",
            {
                "event": "ôn tập",
                "start_time": "2025-12-10T07:00:00",
                "location": "trường học",
            },
        ),
        # 11. Dùng 2-12-2025
        (
            "nhắc tôi đi mua sắm tại siêu thị ngày 2-12-2025 lúc 18:30",
            {
                "event": "đi mua sắm",
                "start_time": "2025-12-02T18:30:00",
            },
        ),
        # 12. Ngày mai
        (
            "nhắc tôi đi nộp bài lúc 9 giờ ngày 2/12/2025, nhắc trước 15 phút",
            {
                "event": "đi nộp bài",
                "start_time": "2025-12-02T09:00:00",
            },
        ),
        # 13. Sáng mai, không nói giờ (mặc định 08:00)
        (
            "nhắc tôi dậy sớm vào sáng mai để chạy bộ",
            {
                "event": "dậy sớm để chạy bộ",
                "start_time": "2025-12-02T08:00:00",
            },
        ),
        # 14. Tối mai, có giờ
        (
            "nhắc tôi xem phim lúc 20:00 tối mai",
            {
                "event": "xem phim",
                "start_time": "2025-12-02T20:00:00",
            },
        ),
        # 15. Khoảng giờ + kết thúc (end_time)
        (
            "đặt lịch học nhóm từ 9 giờ đến 11 giờ sáng mai ở phòng 101",
            {
                "event": "học nhóm",
                "start_time": "2025-12-02T09:00:00",
                "end_time": "2025-12-02T11:00:00",
                "location": "phòng 101",
            },
        ),
        # 16. Có chữ 'đến' ở giữa
        (
            "họp đồ án 7h thứ 5 tuần này ở phòng 502",
            {
                "event": "họp đồ án",
                "start_time": "2025-12-04T07:00:00",
                "location": "phòng lab",
            },
        ),
        # 17. Thứ năm không dấu
        (
            "nhac toi hop luc 10 gio thu nam tuan nay o phong 302",
            {
                "event": "Họp",
                "start_time": "2025-12-04T10:00:00",
                "location": "phòng 302",
            },
        ),
        # 18. Viết không dấu hoàn toàn
        (
            "nhac toi di hoc luc 7h sang mai o phong 203",
            {
                "event": "di hoc",
                "start_time": "2025-12-02T07:00:00",
                "location": "phòng 203",
            },
        ),
        # 19. Nhắc trước bằng giờ
        (
            "nhắc tôi họp hội đồng lúc 15h chiều mai ở phòng họp, nhắc trước 2 tiếng",
            {
                "event": "Họp hội đồng",
                "start_time": "2025-12-02T15:00:00",
                "location": "phòng họp",
                "reminder_minutes": 120,
            },
        ),
        # 20. Chỉ địa điểm + ngày (mặc định giờ)
        (
            "tạo lịch đi làm tại công ty ngày 2/12/2025",
            {
                "event": "ghé thư viện đại học bách khoa",
                "start_time": "2025-12-02T06:00:00",
                "location": "thư viện đại học bách khoa",
            },
        ),
        # 21. Sử dụng 'cuối tuần'
        (
            "nhắc tôi đi chơi vào 9h sáng cuối tuần ở quán cà phê ABC",
            {
                "event": "đi chơi",
                "start_time": "2025-12-07T09:00:00",
                "location": "quán cà phê ABC",
            },
        ),
        # 22. Chủ nhật
        (
            "nhắc tôi đi lễ lúc 7 giờ sáng chủ nhật này",
            {
                "event": "đi lễ",
                "start_time": "2025-12-07T07:00:00",
            },
        ),
        # 23. CN viết tắt, không dấu
        (
            "nhac toi di le luc 7 gio cn nay",
            {
                "event": "di le",
                "start_time": "2025-12-07T07:00:00",
            },
        ),
        # 24. 10h30
        (
            "họp nhóm lúc 10h30 sáng mai tại phòng 201",
            {
                "event": "họp nhóm",
                "start_time": "2025-12-02T10:30:00",
                "location": "phòng 201",
            },
        ),
        # 25. Định dạng 09:00
        (
            "nhắc tôi họp lớp lúc 09:00 ngày 3/12/2025 ở hội trường chính",
            {
                "event": "họp lớp",
                "start_time": "2025-12-03T09:00:00",
                "location": "hội trường chính",
            },
        ),
        # 26. Song ngữ
        (
            "meeting với client lúc 13:30 chiều nay tại phòng họp 4",
            {
                "event": "meeting với client",
                "start_time": "2025-12-01T13:30:00",
                "location": "phòng họp 4",
            },
        ),
        # 27. Ngày cụ thể khác
        (
            "ngày 5/12/2025 nhớ tôi đi khám tổng quát ở bệnh viện quốc tế",
            {
                "event": "đi khám tổng quát",
                "start_time": "2025-12-05T06:00:00",
                "location": "bệnh viện quốc tế",
            },
        ),
        # 28. Thứ 7 tuần sau
        (
            "nhắc tôi đi chơi lúc 19h thứ 7 tuần sau",
            {
                "event": "đi chơi",
                "start_time": "2025-12-13T19:00:00",
            },
        ),
        # 29. Trưa nay
        (
            "nhắc tôi ăn trưa với bạn lúc 12h trưa nay ở căn tin",
            {
                "event": "ăn trưa với bạn",
                "start_time": "2025-12-01T12:00:00",
                "location": "căn tin",
            },
        ),
        # 30. Đêm nay
        (
            "nhắc tôi uống thuốc lúc 22h đêm nay",
            {
                "event": "uống thuốc",
                "start_time": "2025-12-01T22:00:00",
            },
        ),
    ]

    total = len(test_cases)
    passed = 0

    for idx, (text, expected) in enumerate(test_cases, start=1):
        print("=" * 80)
        print(f"Test {idx}: {text}")
        try:
            result = parse_natural_input(text, now=now)
            print("Kết quả:", result)

            ok = True

            # So sánh từng trường
            if "event" in expected:
                if result["event"].lower() != expected["event"].lower():
                    print(f"  ❌ event khác. expected='{expected['event']}', got='{result['event']}'")
                    ok = False

            if "start_time" in expected:
                if result["start_time"] != expected["start_time"]:
                    print(f"  ❌ start_time khác. expected='{expected['start_time']}', got='{result['start_time']}'")
                    ok = False

            if "end_time" in expected:
                if result["end_time"] != expected["end_time"]:
                    print(f"  ❌ end_time khác. expected='{expected['end_time']}', got='{result['end_time']}'")
                    ok = False

            if "location" in expected:
                got_loc = result.get("location") or ""
                if got_loc.lower() != expected["location"].lower():
                    print(f"  ❌ location khác. expected='{expected['location']}', got='{got_loc}'")
                    ok = False

            if "reminder_minutes" in expected:
                if result["reminder_minutes"] != expected["reminder_minutes"]:
                    print(
                        f"  ❌ reminder_minutes khác. expected={expected['reminder_minutes']}, "
                        f"got={result['reminder_minutes']}"
                    )
                    ok = False

            if ok:
                print("  ✅ PASSED")
                passed += 1
            else:
                print("  ❌ FAILED")

        except Exception as e:
            print("  ❌ LỖI:", e)

    print("=" * 80)
    print(f"Tổng: {passed}/{total} test passed")
    acc = passed / total * 100
    print(f"Độ chính xác xấp xỉ: {acc:.2f}%")
    if acc >= 80:
        print("✅ Đạt yêu cầu > 80%")
    else:
        print("⚠️ Chưa đạt 80%, cần cải thiện NLP/time_parsing.")


if __name__ == "__main__":
    print("=== Kiểm tra toàn bộ pipeline với 30 test case ===")
    run_tests()