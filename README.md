Personal Schedule Assistant: Ứng dụng hỗ trợ quản lý lịch cá nhân bằng ngôn ngữ tự nhiên tiếng Việt, phát triển trên nền Python và Tkinter.

1. Giới thiệu
   Personal Schedule Assistant cho phép người dùng nhập câu lệnh tiếng Việt tự nhiên để tạo, chỉnh sửa, xóa và nhắc lịch tự động. Hệ thống tự động phân tích câu lệnh để trích xuất thông tin sự kiện như nội dung, thời gian, địa điểm và thời gian nhắc trước.

2. Chức năng chính
- Xử lý ngôn ngữ tự nhiên (NLP):Tự động trích xuất thời gian, ngày, địa điểm, nhắc trước, thời gian kết thúc, hỗ trợ nhiều dạng biểu đạt thời gian, tự động chuẩn hóa văn bản trước khi phân tích.
- Quản lý sự kiện:Thêm sự kiện bằng câu lệnh tiếng Việt, chỉnh sửa và xóa sự kiện, lưu trữ trong SQLite dưới dạng chuẩn ISO datetime.
- Nhắc lịch tự động: Bộ lập lịch chạy dưới dạng luồng nền, kiểm tra sự kiện định kỳ và hiển thị thông báo đúng thời điểm, hỗ trợ âm báo trên Windows.
- Giao diện Tkinter: Giao diện hiện đại, rõ ràng, dễ sử dụng, bảng danh sách sự kiện, ô tìm kiếm, mini-calendar, các nút chức năng: Thêm sự kiện, Chỉnh sửa, Xóa, Xuất file .ics.

3. Công nghệ sử dụng:
- Python 3.10+: Ngôn ngữ lập trình chính của dự án.
- Tkinter: Xây dựng giao diện người dùng cho ứng dụng desktop.
- SQLite3: Lưu trữ dữ liệu cục bộ, không cần cài đặt thêm.
- underthesea: Hỗ trợ xử lý tiếng Việt như tách từ và nhận diện thực thể cơ bản.
- Regex (re): Trích xuất thời gian, địa điểm và cụm từ quan trọng trong câu lệnh.
- dateparser: Chuẩn hóa và phân tích các chuỗi thời gian tiếng Việt.
- Threading: Tạo bộ nhắc lịch chạy nền, kiểm tra sự kiện định kỳ.
- winsound (Windows): Tạo âm báo khi đến giờ nhắc nhở.
- Datetime & Timezone Utilities: Chuyển đổi và quản lý đối tượng ngày/giờ một cách nhất quán.

4. Cài đặt và chạy
- Cài đặt python: 3.10 trở lên
- Cài thư viện: pip install -r requirements.txt
- Chạy ứng dụng: python src/app.py

5. Bộ kiểm thử NLP:
- Câu có dấu / không dấu
- Thời gian dạng giờ, phút, ngày, tuần
- Nhắc trước bằng phút hoặc giờ
- Câu lệnh đa cấu trúc
- Mục tiêu độ chính xác ≥ 80%.

6. Hạn chế
- Chưa xử lý câu quá phức tạp mang tính điều kiện hoặc mơ hồ.
- Location chủ yếu dựa vào rule-based.
