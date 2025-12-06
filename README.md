Personal Schedule Assistant: Ứng dụng hỗ trợ quản lý lịch cá nhân bằng ngôn ngữ tự nhiên tiếng Việt, phát triển trên nền Python và Tkinter.

1. Giới thiệu
   Personal Schedule Assistant cho phép người dùng nhập câu lệnh tiếng Việt tự nhiên để tạo, chỉnh sửa, xóa và nhắc lịch tự động. Hệ thống tự động phân tích câu lệnh để trích xuất thông tin sự kiện như nội dung, thời gian, địa điểm và thời gian nhắc trước.

2. Chức năng chính

2.1 Xử lý ngôn ngữ tự nhiên (NLP)
-Tự động trích xuất thời gian, ngày, địa điểm, nhắc trước, thời gian kết thúc.
-Hỗ trợ nhiều dạng biểu đạt thời gian
-Tự động chuẩn hóa văn bản trước khi phân tích.

2.2 Quản lý sự kiện
-Thêm sự kiện bằng câu lệnh tiếng Việt.
-Chỉnh sửa và xóa sự kiện.
-Lưu trữ trong SQLite dưới dạng chuẩn ISO datetime.

2.3 Nhắc lịch tự động
-Bộ lập lịch chạy dưới dạng luồng nền.
-Kiểm tra sự kiện định kỳ và hiển thị thông báo đúng thời điểm.
-Hỗ trợ âm báo trên Windows.

2.4 Giao diện Tkinter
-Giao diện hiện đại, rõ ràng, dễ sử dụng.
-Bảng danh sách sự kiện, ô tìm kiếm, mini-calendar.
-Các nút chức năng: Thêm sự kiện, Chỉnh sửa, Xóa, Xuất file .ics.

3. Công nghệ sử dụng
   -Python 3.10+: Ngôn ngữ lập trình chính của dự án.
   -Tkinter: Xây dựng giao diện người dùng cho ứng dụng desktop.
   -SQLite3: Lưu trữ dữ liệu cục bộ, không cần cài đặt thêm.
   -underthesea: Hỗ trợ xử lý tiếng Việt như tách từ và nhận diện thực thể cơ bản.
   -Regex (re): Trích xuất thời gian, địa điểm và cụm từ quan trọng trong câu lệnh.
   -dateparser: Chuẩn hóa và phân tích các chuỗi thời gian tiếng Việt.
   -Threading: Tạo bộ nhắc lịch chạy nền, kiểm tra sự kiện định kỳ.
   -winsound (Windows): Tạo âm báo khi đến giờ nhắc nhở.
   -Datetime & Timezone Utilities: Chuyển đổi và quản lý đối tượng ngày/giờ một cách nhất quán.
4. Kiến trúc hệ thống
   src/
   ├─ nlp/
   │ ├─ preprocessing.py # Phân đoạn từ và tiền xử lý
   │ ├─ ner.py # Nhận diện thực thể
   │ ├─ rules.py # Trích tên sự kiện, nhắc nhở
   │ ├─ time_parsing.py # Phân tích thời gian
   │ └─ engine.py # Lưu sự kiện
   │
   ├── storage/
   │ └── db.py # Tương tác SQLite
   │
   ├── reminder/
   │ └── scheduler.py # Bộ nhắc lịch tự động
   │
   ├── ui/
   │ └── main_window.py # Giao diện Tkinter
   │
   └── app.py # File chạy chính

5. Cài đặt và chạy
   -Cài thư viện: pip install -r requirements.txt
   -Chạy ứng dụng: python app.py

6. Bộ kiểm thử NLP
   -Ứng dụng được kiểm thử với bộ 30 test case bao gồm:
   -Câu có dấu / không dấu
   -Thời gian dạng giờ, phút, ngày, tuần
   -Trường hợp có end_time và không có end_time
   -Nhắc trước bằng phút hoặc giờ
   -Câu lệnh đa cấu trúc
   -Mục tiêu độ chính xác ≥ 80%.

7. Hạn chế
   -Chưa xử lý câu quá phức tạp mang tính điều kiện hoặc mơ hồ.
   -Location chủ yếu dựa vào rule-based.
   -Nhắc lịch chỉ chạy khi ứng dụng đang mở.
