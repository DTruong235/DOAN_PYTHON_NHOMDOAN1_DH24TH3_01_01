# 🎓 DTH235802_LAMDUCTRUONG_DOAN  
**Phiên bản tài liệu:** 30/10/2025  

## 🧩 Tóm tắt  
Đây là một **ứng dụng desktop prototype để quản lý sinh viên**, được phát triển bằng **Python**.  
Giao diện chính sử dụng **CustomTkinter (CTk)** để mang lại trải nghiệm hiện đại, kết hợp với **Data Access Layer (MS SQL Server qua pyodbc)**.  

---

## 🎯 Mục tiêu  
Prototype này cung cấp:  
- Màn hình **đăng nhập**.  
- Cửa sổ chính có **nhiều tab (Notebook)**.  
- Các chức năng **CRUD đầy đủ** cho 4 module:
  - **Sinh viên**
  - **Môn học**
  - **Học phần**
  - **Bảng điểm**  

Ứng dụng nhằm giúp sinh viên **thực hành tích hợp GUI ↔ DB**, xử lý **input/validation**, và **áp dụng truy vấn tham số hóa an toàn**.

---

## ⚙️ Yêu cầu / Phụ thuộc  
- **Python** 3.8+  
- **MS SQL Server** (đã cài đặt và đang chạy)  
- **ODBC Driver 17 hoặc 18 for SQL Server**  

---

## 📦 Cài đặt Thư viện Python  

### 🔹 Khuyến nghị: Dùng môi trường ảo (venv)
Trước tiên, tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
venv\Scripts\activate
```

### 🔹 Cách 1: Dùng `requirements.txt` (Khuyên dùng)
Tạo file `requirements.txt` trong thư mục gốc, với nội dung sau:
```
customtkinter
pillow
pyodbc
tkcalendar
```

Cài đặt toàn bộ thư viện:
```bash
pip install -r requirements.txt
```

### 🔹 Cách 2: Cài đặt thủ công
```bash
pip install customtkinter pillow pyodbc tkcalendar
```

---

## 🗂️ Cấu trúc Project (chính)

```
📁 project_root/
├── constants.py         # Hằng số dùng chung (màu, font, style)
├── db_manager.py        # Quản lý kết nối DB, thực hiện CRUD
├── login_view.py        # Màn hình đăng nhập (toggle password)
├── main_app.py          # Cửa sổ chính (MainApp) - chứa các tab module
├── run_app.py           # Entry point khởi chạy ứng dụng
│
├── gui/
│   ├── student_tab.py   # Quản lý Sinh viên
│   ├── subject_tab.py   # Quản lý Môn học
│   ├── course_tab.py    # Quản lý Học phần
│   ├── grade_tab.py     # Quản lý Bảng điểm
│   └── ui_utils.py      # Hàm hỗ trợ giao diện (TreeView, Style)
│
├── items/
│   ├── open_eye.png
│   └── closed_eye.png
│
└── requirements.txt
```

---

## 🖥️ Chi tiết Chức năng  

### 🔐 **Màn hình Đăng nhập**
- Nhập **username** và **password**.  
- Toggle ẩn/hiện mật khẩu bằng **icon mắt**.  
- Xác thực demo (`admin / 123`) → mở **MainApp** khi thành công.  

---

### 🎓 **Module Quản lý Sinh viên (`student_tab.py`)**
- CRUD và **tìm kiếm sinh viên**.  
- Ô nhập ngày sinh dùng `tkcalendar`.  
- Validate đầu vào (regex cho **MASV**, **email**, v.v.).  

---

### 📘 **Module Quản lý Môn học (`subject_tab.py`)**
- CRUD và tìm kiếm môn học.  
- Validate (regex cho **MAMH**, kiểm tra **SOTINCHI** từ 1–10).  

---

### 📚 **Module Quản lý Học phần (`course_tab.py`)**
- CRUD và tìm kiếm học phần.  
- `CTkComboBox` (readonly) hiển thị **MAMH** từ danh sách môn học.  

---

### 🧮 **Module Quản lý Bảng điểm (`grade_tab.py`)**
- Tìm kiếm sinh viên theo **MASV** để xem bảng điểm.  
- Tính toán **Điểm trung bình (GPA)** và **Xếp loại tự động**.  
- Cho phép **Thêm / Cập nhật / Xóa** điểm cho từng học phần.  

---

## 🗄️ Data Layer (`db_manager.py`)
- Kết nối **MS SQL Server** qua **ODBC Driver**.  
- Sử dụng `_execute_query()` làm hàm trung tâm cho mọi truy vấn.  
- Truy vấn **tham số hóa** (phòng chống SQL Injection).  
- Xử lý lỗi `pyodbc.IntegrityError` (khóa chính, khóa ngoại).  
- Hỗ trợ các truy vấn nâng cao:
  - `MERGE` (cho `add_or_update_grade`)  
  - `JOIN`, `SUM` (cho `calculate_gpa_raw`)  

---

## 🧱 Sơ đồ Cơ sở Dữ liệu  

### 🧍‍♂️ **SVIEN**
| Cột | Kiểu dữ liệu | Ghi chú |
|------|---------------|---------|
| MASV | `varchar` | **PK** |
| TEN | `nvarchar` |  |
| GIOITINH | `nvarchar` |  |
| NGAYSINH | `date` |  |
| DIACHI | `nvarchar` |  |
| KHOAHOC | `int` |  |
| KHOA | `nvarchar` |  |
| EMAIL | `nvarchar` |  |

### 📘 **MHOC**
| Cột | Kiểu | Ghi chú |
|------|------|---------|
| MAMH | `varchar` | **PK** |
| TEN_MH | `nvarchar` |  |
| SOTINCHI | `int` |  |
| KHOA | `nvarchar` |  |

### 📚 **HOCPHAN**
| Cột | Kiểu | Ghi chú |
|------|------|---------|
| MAHP | `int` | **PK** |
| MAMH | `varchar` | **FK → MHOC** |
| HOCKY | `int` |  |
| NAMHOC | `varchar` |  |
| GV | `nvarchar` |  |

### 🧮 **KETQUA**
| Cột | Kiểu | Ghi chú |
|------|------|---------|
| MASV | `varchar` | **FK → SVIEN** |
| MAHP | `int` | **FK → HOCPHAN** |
| DIEM | `float` |  |
| **PRIMARY KEY** | `(MASV, MAHP)` |  |

---

## 🚀 Hướng dẫn Chạy Nhanh  

### 1️⃣ Cấu hình thông tin DB  
Mở file `run_app.py` và chỉnh sửa các hằng số:
```python
SERVER_NAME = 'LAPTOP-XXXX\\SQLEXPRESS'
DATABASE_NAME = 'QLSV'
SQL_USER = 'sa'
SQL_PASSWORD = '123'
```

### 2️⃣ Chạy ứng dụng
```bash
python run_app.py
```

### 3️⃣ Đăng nhập Demo
- **Username:** `admin`  
- **Password:** `123`  

---

## 💡 Ghi chú
- Ứng dụng được xây dựng theo mô hình **Prototype**, chưa hoàn thiện tất cả nghiệp vụ thực tế.  
- Mục đích chính: **Thực hành tích hợp GUI – Database và xử lý dữ liệu an toàn.**

---

## 👨‍💻 Tác giả
**Lâm Đức Trường — DTH235802**  
Trường Đại học An Giang 
Khoa Công nghệ Thông tin  
