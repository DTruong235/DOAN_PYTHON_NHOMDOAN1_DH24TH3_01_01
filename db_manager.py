# db_manager.py

import pyodbc
import tkinter.messagebox as messagebox

class DB_Manager:
    """
    Quản lý kết nối và các thao tác CRUD an toàn với MSSQL Server.
    Sử dụng truy vấn tham số hóa (Parameterized Queries) để ngăn chặn SQL Injection.[1]
    """
    def __init__(self, server_name, database_name, username, password):
        self.server_name = server_name
        self.database_name = database_name
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None
        self.connection_string = self._build_connection_string()

    # db_manager.py

    def _build_connection_string(self):
        """Xây dựng chuỗi kết nối dựa trên loại xác thực."""
        # Giả sử bạn đang dùng Driver 18 (Cần phải cài đặt)
        DRIVER_NAME = '{ODBC Driver 18 for SQL Server}' 

        if self.username and self.password:
            # Xác thực SQL Server (UID/PWD)
            return (
                f'DRIVER={DRIVER_NAME};'
                f'SERVER={self.server_name};'
                f'DATABASE={self.database_name};'
                f'UID={self.username};'
                f'PWD={self.password};'
                # DÒNG MỚI BẮT BUỘC ĐỂ KHẮC PHỤC LỖI SSL:
                f'TrustServerCertificate=yes;'
            )
        else:
            # Xác thực Windows (Nếu bạn chuyển sang chế độ này)
            return (
                f'DRIVER={DRIVER_NAME};'
                f'SERVER={self.server_name};'
                f'DATABASE={self.database_name};'
                f'Trusted_Connection=yes;'
                # THÊM CẢ VÀO ĐÂY ĐỂ ĐẢM BẢO
                f'TrustServerCertificate=yes;'
            )

    #... (phần còn lại của lớp DB_Manager)

    def connect(self):
        """Mở kết nối database."""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            return True
        except pyodbc.Error as ex:
            # Bắt lỗi pyodbc và hiển thị thông báo [3]
            sqlstate = ex.args
            messagebox.showerror("Lỗi Kết Nối Database", f"Không thể kết nối tới SQL Server.\nLỗi: {sqlstate}")
            self.conn = None
            self.cursor = None
            return False

    def disconnect(self):
        """Đóng kết nối database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    # --- READ (Đọc dữ liệu) ---
    def fetch_all_students(self):
        """Lấy tất cả sinh viên từ bảng SVIEN."""
        sql = "SELECT MASV, TEN, NAM, KHOA FROM SVIEN ORDER BY MASV"
        try:
            self.cursor.execute(sql)
            # Lấy tên cột (ví dụ sử dụng trong main_app.py)
            columns = [column for column in self.cursor.description]
            # Lấy tất cả hàng dữ liệu
            rows = self.cursor.fetchall()
            return columns, rows
        except Exception as e:
            messagebox.showerror("Lỗi Truy Vấn", f"Không thể tải dữ liệu sinh viên.\nLỗi: {e}")
            return

    # --- CREATE (Thêm dữ liệu) ---
    def add_student(self, masv, ten, nam, khoa):
        """Thêm sinh viên mới (sử dụng tham số hóa)."""
        sql_insert = "INSERT INTO SVIEN (MASV, TEN, NAM, KHOA) VALUES (?,?,?,?)"
        data_to_insert = (masv, ten, nam, khoa)
        
        try:
            self.cursor.execute(sql_insert, data_to_insert)
            self.conn.commit()
            return True
        except pyodbc.IntegrityError:
            # Lỗi trùng lặp Khóa Chính MASV (IntegrityError) [3]
            messagebox.showwarning("Lỗi Dữ Liệu", "Mã sinh viên (MASV) này đã tồn tại trong hệ thống.")
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Mới", f"Có lỗi xảy ra khi thêm sinh viên: {e}")
            self.conn.rollback()
            return False

    # --- DELETE (Xóa dữ liệu) ---
    def delete_student(self, masv):
        """Xóa sinh viên (sử dụng tham số hóa)."""
        sql_delete = "DELETE FROM SVIEN WHERE MASV =?"
        
        try:
            self.cursor.execute(sql_delete, masv)
            self.conn.commit()
            # Kiểm tra xem có hàng nào bị xóa không
            if self.cursor.rowcount > 0:
                return True
            else:
                messagebox.showwarning("Không tìm thấy", "Không tìm thấy sinh viên có mã này để xóa.")
                return False
        except pyodbc.IntegrityError:
            # Lỗi khóa ngoại (FK error) - Sinh viên có điểm trong KETQUA
            messagebox.showwarning("Lỗi Ràng Buộc", "Không thể xóa sinh viên này vì đang có dữ liệu điểm (KETQUA) liên quan.")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Xóa", f"Có lỗi xảy ra khi xóa sinh viên: {e}")
            self.conn.rollback()
            return False

    # Các hàm UPDATE, Tìm kiếm, và CRUD cho các bảng khác (MHOC, KETQUA) sẽ được thêm sau.