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
        sql = """
            SELECT MASV, TEN, GIOITINH, 
                   CONVERT(varchar, NGAYSINH, 103) AS NGAYSINH_FORMATTED, 
                   DIACHI, KHOAHOC, KHOA, EMAIL 
            FROM SVIEN 
            ORDER BY MASV
            """
        try:
            self.cursor.execute(sql)
            # Lấy tên cột
            columns = [desc[0] for desc in self.cursor.description]

            # Lấy tất cả hàng và làm phẳng tuple (nếu có tuple lồng)
            rows = [
                tuple(item[0] if isinstance(item, tuple) else item for item in row)
                for row in self.cursor.fetchall()
            ]

            return columns, rows
        except Exception as e:
            messagebox.showerror("Lỗi Truy Vấn", f"Không thể tải dữ liệu sinh viên.\nLỗi: {e}")
            return

    # --- CREATE (Thêm dữ liệu) ---
    def add_student(self, masv, ten, gioitinh,ngaysinh, diachi ,khoahoc, khoa, email):
        """Thêm sinh viên mới (sử dụng tham số hóa)."""
        sql_insert = "INSERT INTO SVIEN (MASV, TEN, GIOITINH, NGAYSINH, DIACHI, KHOAHOC, KHOA, EMAIL) VALUES (?,?,?,?,?,?,?,?)"
        data_to_insert = (masv, ten, gioitinh, ngaysinh, diachi ,khoahoc, khoa, email)
        
        try:
            self.cursor.execute(sql_insert, data_to_insert)
            self.conn.commit()
            return True
        except pyodbc.IntegrityError as e:
            # In lỗi chi tiết ra cửa sổ terminal/console của bạn
            print("--- LỖI DATABASE CHI TIẾT ---")
            print(e)
            print("-----------------------------")

            # Phân tích lỗi để hiển thị thông báo chính xác hơn
            error_message = str(e)
            
            if "PRIMARY KEY" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", "Mã sinh viên (MASV) này đã tồn tại trong hệ thống.")
            elif "UNIQUE constraint" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", "Lỗi trùng lặp: Email, SĐT hoặc một trường duy nhất nào đó đã tồn tại.")
            elif "FOREIGN KEY" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", "Lỗi khóa ngoại: Khoa hoặc một trường tham chiếu không tồn tại.")
            else:
                messagebox.showwarning("Lỗi Dữ Liệu", "Lỗi định dạng Mã sinh viên (MSV): MSV phải theo định dạng [a-z][0-9][0-9][0-9]")
            
            self.conn.rollback() 
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
            self.cursor.execute(sql_delete, (masv))
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
    # --- HÀM TÌM SINH VIÊN THEO MSV ---
    def find_student(self,masv):
        if not masv:
            # Nếu từ khóa trống, trả về tất cả sinh viên
            return self.fetch_all_students()
        
        # Chuẩn hóa từ khóa để tìm kiếm không phân biệt chữ hoa/thường và khớp một phần
        search_term = f"%{masv}%"

        sql_find = "SELECT * FROM SVIEN WHERE MASV LIKE ?"

        params = (search_term,) # Tuple tham số

        try:
            # Thực thi câu lệnh SQL
            self.cursor.execute(sql_find, params)
            
            # Lấy tên cột
            columns = [desc[0] for desc in self.cursor.description]

            
            # Lấy tất cả hàng dữ liệu khớp
            rows = [
                tuple(item[0] if isinstance(item, tuple) else item for item in row)
                for row in self.cursor.fetchall()
            ]
            
            return columns, rows
            
        except Exception as e:
            # Xử lý lỗi DB mà không làm sập ứng dụng
            print(f"Lỗi truy vấn tìm kiếm theo MASV: {e}")
            return None,[] # Trả về list rỗng
        
    # --- UPDATE (Cập nhật dữ liệu) ---
    def update_student(self, masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email):
        """Cập nhật thông tin sinh viên (sử dụng tham số hóa)."""
        
        # Câu lệnh SQL UPDATE
        sql_update = """
            UPDATE SVIEN 
            SET TEN = ?, GIOITINH = ?, NGAYSINH = ?, DIACHI = ?, 
                KHOAHOC = ?, KHOA = ?, EMAIL = ?
            WHERE MASV = ?
        """
        
        # MASV (khóa chính) nằm ở cuối cùng cho mệnh đề WHERE
        data_to_update = (ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email, masv)
        
        try:
            self.cursor.execute(sql_update, data_to_update)
            self.conn.commit()
            
            # Kiểm tra xem có hàng nào thực sự được cập nhật không
            if self.cursor.rowcount > 0:
                return True
            else:
                # Trường hợp người dùng nhấn "Sửa" nhưng không thay đổi gì
                # Hoặc MASV không tồn tại (dù trường hợp này khó xảy ra nếu làm đúng)
                messagebox.showwarning("Không Cập Nhật", "Không tìm thấy sinh viên hoặc không có thông tin nào thay đổi.")
                return False
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật", f"Có lỗi xảy ra khi cập nhật sinh viên: {e}")
            self.conn.rollback()
            return False
        
    def fetch_all_subjects(self):
        """Lấy tất cả môn học từ bảng MHOC."""
        sql = "SELECT MAMH, TEN_MH, SOTINCHI, KHOA FROM MHOC ORDER BY MAMH" # Lấy đủ cột
        try:
            self.cursor.execute(sql)
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall() # fetchall trả về list các tuple
            return columns, rows
        except Exception as e:
            messagebox.showerror("Lỗi Truy Vấn Môn Học", f"Không thể tải dữ liệu môn học.\nLỗi: {e}")
            return [], []
    
    # --- CREATE (Thêm Môn Học) ---
    def add_subject(self, mamh, ten_mh, sotinchi, khoa='CNTT'): # Khoa có giá trị mặc định
        """Thêm môn học mới (dùng tham số hóa)."""
        sql_insert = "INSERT INTO MHOC (MAMH, TEN_MH, SOTINCHI, KHOA) VALUES (?, ?, ?, ?)"
        # Đảm bảo mamh là chữ thường để khớp CHECK constraint
        data_to_insert = (mamh.lower(), ten_mh, sotinchi, khoa)
        try:
            self.cursor.execute(sql_insert, data_to_insert)
            self.conn.commit()
            return True
        except pyodbc.IntegrityError as e:
            error_message = str(e)
            print(f"LỖI DB (Add Subject): {error_message}") # In lỗi chi tiết
            if "PRIMARY KEY" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", f"Mã môn học '{mamh}' đã tồn tại.")
            elif "CHECK constraint" in error_message:
                 if "SOTINCHI" in error_message:
                     messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải từ 1 đến 10.")
                 elif "MAMH" in error_message:
                     messagebox.showwarning("Lỗi Dữ Liệu", "Mã môn học phải theo định dạng 'aaa###' (vd: dsg101).")
                 else:
                     messagebox.showwarning("Lỗi Dữ Liệu", f"Dữ liệu vi phạm ràng buộc CHECK: {e}")
            else:
                 messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Môn Học", f"Có lỗi xảy ra khi thêm môn học: {e}")
            self.conn.rollback()
            return False

    # --- UPDATE (Sửa Môn Học) ---
    def update_subject(self, mamh, ten_mh, sotinchi, khoa='CNTT'):
        """Cập nhật thông tin môn học (dùng tham số hóa)."""
        sql_update = """
            UPDATE MHOC
            SET TEN_MH = ?, SOTINCHI = ?, KHOA = ?
            WHERE MAMH = ?
        """
        # mamh trong WHERE clause không cần lower() nếu dữ liệu gốc đã đúng
        data_to_update = (ten_mh, sotinchi, khoa, mamh)
        try:
            self.cursor.execute(sql_update, data_to_update)
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True
            else:
                # Có thể không tìm thấy mamh hoặc không có gì thay đổi
                messagebox.showwarning("Không Cập Nhật", f"Không tìm thấy mã môn học '{mamh}' để cập nhật hoặc không có thông tin nào thay đổi.")
                return False
        except pyodbc.IntegrityError as e: # Bắt lỗi CHECK khi cập nhật
            error_message = str(e)
            print(f"LỖI DB (Update Subject): {error_message}") # In lỗi chi tiết
            if "CHECK constraint" in error_message:
                 if "SOTINCHI" in error_message:
                     messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải từ 1 đến 10.")
                 else:
                     messagebox.showwarning("Lỗi Dữ Liệu", f"Dữ liệu vi phạm ràng buộc CHECK: {e}")
            else:
                 messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật Môn Học", f"Có lỗi xảy ra khi cập nhật môn học: {e}")
            self.conn.rollback()
            return False

    # --- DELETE (Xóa Môn Học) ---
    def delete_subject(self, mamh):
        """Xóa môn học (dùng tham số hóa)."""
        sql_delete = "DELETE FROM MHOC WHERE MAMH = ?"
        try:
            self.cursor.execute(sql_delete, (mamh,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True
            else:
                # Không tìm thấy mamh để xóa
                messagebox.showwarning("Không Tìm Thấy", f"Không tìm thấy mã môn học '{mamh}' để xóa.")
                return False
        except pyodbc.IntegrityError:
            # Lỗi khóa ngoại (nếu MHOC được tham chiếu bởi bảng KETQUA chẳng hạn)
            messagebox.showwarning("Lỗi Ràng Buộc", f"Không thể xóa môn học '{mamh}' vì có thể đang có dữ liệu điểm liên quan.")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Xóa Môn Học", f"Có lỗi xảy ra khi xóa môn học: {e}")
            self.conn.rollback()
            return False
        
    # === HÀM TÌM KIẾM MÔN HỌC ===
    def find_subject(self, search_keyword):
        """Tìm kiếm môn học theo MAMH (LIKE)."""
        # Nếu keyword rỗng, trả về tất cả
        if not search_keyword:
            return self.fetch_all_subjects()

        # Tìm kiếm gần đúng (LIKE) và không phân biệt hoa thường
        # Chuyển keyword sang chữ thường để khớp với CHECK constraint
        search_term = f"%{search_keyword.lower()}%"
        sql_find = "SELECT MAMH, TEN_MH, SOTINCHI, KHOA FROM MHOC WHERE LOWER(MAMH) LIKE ? ORDER BY MAMH"
        params = (search_term,)

        try:
            self.cursor.execute(sql_find, params)
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            return columns, rows
        except Exception as e:
            messagebox.showerror("Lỗi Tìm Môn Học", f"Có lỗi xảy ra khi tìm kiếm môn học:\n{e}")
            return [], []