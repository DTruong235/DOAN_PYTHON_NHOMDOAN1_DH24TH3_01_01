DTH235802_LAMDUCTRUONG_DOAN
Phiên bản tài liệu: 30/10/2025

Tóm tắt
Đây là một ứng dụng desktop prototype để quản lý sinh viên, phát triển bằng Python. Giao diện chính sử dụng CustomTkinter (CTk) để cung cấp giao diện hiện đại; project kết hợp GUI với Data Access Layer (MS SQL Server qua pyodbc).

Mục tiêu
Cung cấp prototype có: màn hình đăng nhập, cửa sổ chính nhiều tab, và các chức năng CRUD đầy đủ cho 4 module: Sinh viên, Môn học, Học phần và Bảng điểm.

Thực hành tích hợp GUI ↔ DB, xử lý input/validation, và áp dụng các nguyên tắc an toàn truy vấn cơ bản (truy vấn tham số hóa).

Yêu cầu / Phụ thuộc
Python 3.8+

MS SQL Server (Đã được cài đặt và đang chạy)

ODBC Driver 17 (hoặc 18) for SQL Server

Cài đặt Thư viện Python
(Khuyên dùng) Bạn nên tạo và kích hoạt một môi trường ảo (venv) trước khi cài đặt.

Cách 1: Dùng requirements.txt (Khuyên dùng)

Tạo một file mới trong thư mục gốc của dự án tên là requirements.txt.

Copy và dán nội dung sau vào file:

Plaintext

customtkinter
pillow
pyodbc
tkcalendar
Chạy lệnh sau để cài đặt tất cả thư viện cùng một lúc:

Bash

pip install -r requirements.txt
Cách 2: Cài đặt thủ công

Bạn cũng có thể cài đặt từng thư viện riêng lẻ bằng lệnh:

Bash

pip install customtkinter pillow pyodbc tkcalendar
Cấu trúc project (chính)
constants.py — hằng số dùng trong app (màu, font, style widget).

db_manager.py — lớp DB_Manager: quản lý kết nối ODBC và các hàm CRUD cho cả 4 module (Sinh viên, Môn học, Học phần, Kết quả).

login_view.py — giao diện đăng nhập (toggle password, xử lý xác thực demo và khởi tạo MainApp).

main_app.py — giao diện chính (MainApp) xây dựng Notebook/tab, chứa các tab module.

run_app.py — entry-point: thiết lập theme CTk, khởi tạo DB_Manager và khởi động ứng dụng.

gui/ — thư mục chứa các module UI tách rời:

student_tab.py

subject_tab.py

course_tab.py

grade_tab.py

ui_utils.py — helper UI (hàm setup_themed_treeview dùng chung).

items/ — chứa tài nguyên ảnh/icon dùng cho UI (open_eye.png, closed_eye.png).

Chi tiết chức năng (hiện có trong mã)
Màn hình đăng nhập

Nhập username và password.

Toggle hiển thị/ẩn mật khẩu bằng icon mắt.

Xác thực demo (hardcoded admin / 123) — khi thành công, mở MainApp.

Module Quản lý Sinh viên (student_tab.py)

CRUD và Tìm kiếm sinh viên.

Sử dụng tkcalendar cho ô nhập Ngày sinh.

Validate dữ liệu đầu vào (ví dụ: regex cho MASV, email).

Module Quản lý Môn học (subject_tab.py)

CRUD và Tìm kiếm môn học.

Validate dữ liệu đầu vào (ví dụ: regex cho MAMH, SOTC trong khoảng 1-10).

Module Quản lý Học phần (course_tab.py)

CRUD và Tìm kiếm học phần.

Sử dụng CTkComboBox (đã readonly) để chọn MAMH từ danh sách môn học đang có trong DB.

Module Quản lý Bảng điểm (grade_tab.py)

Tìm kiếm sinh viên theo MASV để xem bảng điểm.

Hiển thị Điểm trung bình (GPA) và Xếp loại tự động.

Cho phép Thêm/Cập nhật hoặc Xóa điểm của sinh viên cho một học phần cụ thể.

Data layer (db_manager.py)

Kết nối MS SQL Server qua ODBC driver.

Sử dụng _execute_query làm hàm thực thi trung tâm, áp dụng truy vấn tham số hóa (chống SQL Injection).

Xử lý lỗi pyodbc.IntegrityError (ví dụ: lỗi khóa chính, khóa ngoại) và ném (raise) lỗi để lớp UI bắt và hiển thị thông báo.

Đã triển khai đầy đủ các phương thức CRUD cho cả 4 module, bao gồm các truy vấn phức tạp như MERGE (cho add_or_update_grade) và SUM/JOIN (cho calculate_gpa_raw).

Sơ đồ DB (Chính xác theo code)
Bảng SVIEN:

MASV (PK, varchar)

TEN (nvarchar)

GIOITINH (nvarchar)

NGAYSINH (date)

DIACHI (nvarchar)

KHOAHOC (int)

KHOA (nvarchar)

EMAIL (nvarchar)

Bảng MHOC:

MAMH (PK, varchar)

TEN_MH (nvarchar)

SOTINCHI (int)

KHOA (nvarchar)

Bảng HOCPHAN:

MAHP (PK, int)

MAMH (FK -> MHOC)

HOCKY (int)

NAMHOC (varchar)

GV (nvarchar)

Bảng KETQUA:

MASV (FK -> SVIEN)

MAHP (FK -> HOCPHAN)

DIEM (float)

PRIMARY KEY (MASV, MAHP)

Hướng dẫn chạy nhanh
Đảm bảo bạn đã cài đặt xong CSDL, Python và các thư viện (xem phần "Yêu cầu / Phụ thuộc").

Cấu hình thông tin DB: Mở file run_app.py và chỉnh sửa các hằng số: SERVER_NAME, DATABASE_NAME, SQL_USER, SQL_PASSWORD cho khớp với máy của bạn.

Chạy ứng dụng:

PowerShell

python run_app.py
Đăng nhập bằng tài khoản demo:

Username: admin

Password: 123
