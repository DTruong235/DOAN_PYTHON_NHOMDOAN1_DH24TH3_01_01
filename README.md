DTH235802_LAMDUCTRUONG_DOAN — Giới thiệu đồ án

Phiên bản: 30/10/2025

Tổng quan
---------
Đây là một prototype ứng dụng desktop quản lý sinh viên viết bằng Python. Giao diện sử dụng CustomTkinter (CTk) để có giao diện hiện đại hơn so với Tkinter thuần. Ứng dụng kết nối tới Microsoft SQL Server thông qua `pyodbc` và bao gồm các chức năng CRUD cơ bản cho sinh viên, màn hình đăng nhập, và một cửa sổ chính có nhiều tab (Sinh viên, Môn học, Bảng điểm).

Mục tiêu
--------
- Xây dựng prototype quản lý sinh viên (thêm, xóa, tìm kiếm, hiển thị danh sách).
- Thực hành tích hợp GUI với DB (pyodbc + MSSQL).
- Áp dụng nguyên tắc an toàn cơ bản khi thao tác DB (parameterized queries, transaction handling).

Cấu trúc chính của dự án
# DTH235802_LAMDUCTRUONG_DOAN

Phiên bản tài liệu: 30/10/2025

Tóm tắt
-------
Đây là một ứng dụng desktop prototype để quản lý sinh viên, phát triển bằng Python. Giao diện chính sử dụng CustomTkinter (CTk) để cung cấp giao diện hiện đại; project kết hợp GUI với Data Access Layer (MS SQL Server qua `pyodbc`).

Mục tiêu
--------
- Cung cấp prototype có: màn hình đăng nhập, cửa sổ chính nhiều tab, CRUD cho sinh viên, và nền tảng để phát triển các module môn học/bảng điểm.
- Thực hành tích hợp GUI ↔ DB, xử lý input/validation, và áp dụng các nguyên tắc an toàn truy vấn cơ bản.

Yêu cầu / Phụ thuộc
-------------------
- Python 3.8+
- Thư viện chính: `customtkinter`, `pillow`, `pyodbc`

Cài nhanh (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install customtkinter pillow pyodbc
```

Hoặc tạo `requirements.txt` bằng cách yêu cầu tôi làm (tôi có thể tạo file này).

Cấu trúc project (chính)
-------------------------
- `constants.py` — hằng số dùng trong app (màu, kích thước, ...).
- `db_manager.py` — lớp `DB_Manager`: quản lý kết nối ODBC và các hàm CRUD (SV; có thể mở rộng MH/Score).
- `login_view.py` — giao diện đăng nhập (toggle password, xử lý xác thực demo và khởi tạo `MainApp`).
- `main_app.py` — giao diện chính (MainApp) xây dựng Notebook/tab, tab Sinh viên (form + Treeview). Có thể tham chiếu tới `gui/` để tách bớt UI.
- `run_app.py` — entry-point: thiết lập theme CTk và khởi động ứng dụng.
- `gui/` — thư mục chứa các module UI tách rời (nếu đã chia):
	- `student_tab.py`, `subject_tab.py`, `grade_tab.py`, `course_tab.py` — (tab UI modular)
	- `ui_utils.py` — helper UI (chung cho các tab)
- `items/` — chứa tài nguyên ảnh/icon dùng cho UI (ví dụ `open_eye.png`, `closed_eye.png`).

Cây cấu trúc dự án (ASCII)
---------------------------
DTH235802_LAMDUCTRUONG_DOAN/
├─ constants.py            # Hằng số (màu, kích thước, config)
├─ db_manager.py          # Data access layer — kết nối pyodbc + CRUD
├─ login_view.py          # Màn hình đăng nhập (toggle mật khẩu)
├─ main_app.py            # Cửa sổ chính (Notebook, tab Sinh viên, handlers)
├─ README.md              # Tài liệu dự án
├─ run_app.py             # Entry-point: thiết lập theme CTk và khởi chạy app
├─ gui/                   # UI modular (mỗi tab tách file riêng)
│  ├─ student_tab.py      # Tab Sinh viên
│  ├─ subject_tab.py      # Tab Môn học
│  ├─ grade_tab.py        # Tab Bảng điểm
│  ├─ course_tab.py       # Tab Course / Khóa học (nếu dùng)
│  └─ ui_utils.py         # Helper UI chung
└─ items/                 # Tài nguyên ảnh/icon (open_eye.png, closed_eye.png, ...)

Chi tiết chức năng (hiện có trong mã)
-------------------------------------
1) Màn hình đăng nhập
	- Nhập username và password.
	- Toggle hiển thị/ẩn mật khẩu bằng icon mắt.
	- Xác thực demo (hardcoded `admin` / `123` trong phiên bản prototype) — khi thành công, mở `MainApp`.

2) Quản lý Sinh viên
	- Xem danh sách sinh viên (Treeview) — cột: MASV, TEN, GIOITINH, NGAYSINH, DIACHI, KHOAHOC, KHOA, EMAIL.
	- Thêm sinh viên (form với validation cơ bản).
	- Xóa sinh viên (chọn hàng rồi xóa).
	- Tìm kiếm theo MASV.
	- Load/Refresh danh sách từ DB bằng `DB_Manager.fetch_all_students()`.

3) (Modular) Môn học & Bảng điểm
	- Project đã chứa thư mục `gui/` với các tab modular (subject_tab, grade_tab, course_tab, student_tab).
	- Các tab có thể cung cấp: xem/ thêm/ xóa môn học, ghi/xóa điểm; những chức năng này sẽ gọi tương ứng đến các hàm DB (nếu `DB_Manager` triển khai: fetch_all_subjects, add_subject, add_score, v.v.).

4) Data layer — `DB_Manager`
	- Kết nối MS SQL Server qua ODBC driver (chuỗi kết nối được xây dựng trong `db_manager.py`).
	- Các phương thức hiện có: connect(), disconnect(), fetch_all_students(), add_student(), delete_student(), find_student().
	- Các hàm subject/score có thể được thêm vào `DB_Manager` để tương thích với UI modular.

Sơ đồ DB
----------------------------
- Bảng SVIEN:
	- MASV (PK, varchar)
	- TEN (nvarchar)
	- GIOITINH (nvarchar)
	- NGAYSINH (date)
	- DIACHI (nvarchar)
	- KHOAHOC (int)
	- KHOA (nvarchar)
	- EMAIL (nvarchar)

- Bảng MONHOC:
	- MAMH (PK)
	- TENMH
	- SOCHI

- Bảng KETQUA / DIEM:
	- MASV (FK -> SVIEN)
	- MAMH (FK -> MONHOC)
	- DIEM (float)
	- PRIMARY KEY (MASV, MAMH)

Hướng dẫn chạy nhanh
---------------------
1. Kích hoạt virtualenv và cài phụ thuộc (xem phần "Yêu cầu / Phụ thuộc").
2. Cấu hình thông tin DB: tốt nhất tạo file `.env` hoặc chỉnh `run_app.py` tạm thời để đặt `SERVER_NAME`, `DATABASE_NAME`, `SQL_USER`, `SQL_PASSWORD`.
3. Chạy ứng dụng bằng PowerShell:

```powershell
python run_app.py
```

Ghi chú: `run_app.py` sẽ khởi tạo theme CTk, kết nối DB và mở cửa sổ đăng nhập.
