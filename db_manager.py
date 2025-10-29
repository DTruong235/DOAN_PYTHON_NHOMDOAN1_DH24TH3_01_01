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

    def _execute_query(self, sql, params=None, fetch_mode="all"):
        """Thực thi truy vấn và xử lý lỗi chung."""
        if not self.conn or not self.cursor:
            messagebox.showerror("Lỗi Kết Nối", "Chưa kết nối đến database.")
            # Trả về giá trị mặc định phù hợp với fetch_mode
            if fetch_mode in ["all", "one"]: return [], [] if fetch_mode == "all" else None
            return None

        try:
            print(f"Executing SQL: {sql} with params: {params}") # In ra để debug
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            if fetch_mode == "all":
                # Lấy tên cột (có thể không cần nếu không dùng)
                columns = [desc[0] for desc in self.cursor.description]
                # Xử lý NULL thành chuỗi rỗng
                rows = [tuple(str(item) if item is not None else "" for item in row) for row in self.cursor.fetchall()]
                print(f"Fetched rows: {len(rows)}") # Debug số lượng dòng lấy được
                return columns, rows
            elif fetch_mode == "one":
                result = self.cursor.fetchone()
                # Xử lý NULL thành chuỗi rỗng cho fetchone
                processed_result = tuple(str(item) if item is not None else "" for item in result) if result else None
                return processed_result
            elif fetch_mode == "commit":
                # Chỉ commit và trả về số dòng bị ảnh hưởng
                rowcount = self.cursor.rowcount
                self.conn.commit()
                print(f"Committed. Rows affected: {rowcount}") # Debug
                return rowcount
            elif fetch_mode == "no_fetch_commit":
                # Chỉ commit, không cần rowcount (cho INSERT/MERGE)
                self.conn.commit()
                print("Committed (no fetch).") # Debug
                return True
            else: # fetch_mode == "none" hoặc không xác định
                return None # Không fetch, không commit

        except pyodbc.IntegrityError as e:
            error_message = str(e)
            print(f"LỖI DB (Integrity): {error_message}")
            if self.conn: self.conn.rollback() # QUAN TRỌNG: Rollback
            raise e # Ném lại lỗi để hàm gọi xử lý thông báo cụ thể
        except pyodbc.Error as e:
             error_message = str(e)
             print(f"LỖI DB (pyodbc): {error_message}")
             messagebox.showerror("Lỗi Database", f"Lỗi thực thi truy vấn:\n{error_message}")
             if self.conn: self.conn.rollback()
             # Trả về giá trị mặc định phù hợp với fetch_mode
             if fetch_mode in ["all", "one"]: return [], [] if fetch_mode == "all" else None
             return None
        except Exception as e:
            print(f"LỖI PYTHON (_execute_query): {e}")
            messagebox.showerror("Lỗi Chương Trình", f"Lỗi không xác định khi thực thi truy vấn:\n{e}")
            
            # Trả về giá trị mặc định phù hợp với fetch_mode
            if fetch_mode in ["all", "one"]: return [], [] if fetch_mode == "all" else None
            return None

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
        
    def fetch_all_hocphan(self):
        """Lấy tất cả học phần, JOIN với MHOC để lấy Tên Môn Học."""
        sql = """
            SELECT HP.MAHP, HP.MAMH, MH.TEN_MH, HP.HOCKY, HP.NAMHOC, HP.GV
            FROM HOCPHAN HP
            JOIN MHOC MH ON HP.MAMH = MH.MAMH
            ORDER BY HP.MAHP
        """
        try:
            self.cursor.execute(sql)
            columns = [desc[0] for desc in self.cursor.description] # MAHP, MAMH, TEN_MH, HOCKY, NAMHOC, GV
            rows = self.cursor.fetchall()
            return columns, rows
        except Exception as e:
            messagebox.showerror("Lỗi Truy Vấn Học Phần", f"Không thể tải dữ liệu học phần.\nLỗi: {e}")
            return [], []

    def add_hocphan(self, mahp, mamh, hocky, namhoc, gv):
        """Thêm học phần mới."""
        sql_insert = "INSERT INTO HOCPHAN (MAHP, MAMH, HOCKY, NAMHOC, GV) VALUES (?, ?, ?, ?, ?)"
        # Đảm bảo mamh chữ thường nếu cần khớp foreign key
        data_to_insert = (mahp, mamh.lower(), hocky, namhoc, gv)
        try:
            self.cursor.execute(sql_insert, data_to_insert)
            self.conn.commit()
            return True
        except pyodbc.IntegrityError as e:
            error_message = str(e)
            print(f"LỖI DB (Add HocPhan): {error_message}")
            if "PRIMARY KEY" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", f"Mã học phần '{mahp}' đã tồn tại.")
            elif "FOREIGN KEY constraint 'FK_HOCPHAN'" in error_message:
                 messagebox.showwarning("Lỗi Dữ Liệu", f"Mã môn học '{mamh}' không tồn tại trong bảng Môn Học.")
            elif "CHECK constraint" in error_message: # Bắt lỗi CHECK MAHP > 0
                 messagebox.showwarning("Lỗi Dữ Liệu", "Mã học phần phải lớn hơn 0.")
            else:
                 messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Học Phần", f"Có lỗi xảy ra khi thêm học phần: {e}")
            self.conn.rollback()
            return False

    def update_hocphan(self, mahp, mamh, hocky, namhoc, gv):
        """Cập nhật thông tin học phần."""
        sql_update = """
            UPDATE HOCPHAN
            SET MAMH = ?, HOCKY = ?, NAMHOC = ?, GV = ?
            WHERE MAHP = ?
        """
        # Đảm bảo mamh chữ thường nếu cần khớp foreign key
        data_to_update = (mamh.lower(), hocky, namhoc, gv, mahp)
        try:
            self.cursor.execute(sql_update, data_to_update)
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True
            else:
                messagebox.showwarning("Không Cập Nhật", f"Không tìm thấy mã học phần '{mahp}' hoặc không có gì thay đổi.")
                return False
        except pyodbc.IntegrityError as e: # Bắt lỗi FK khi sửa MAMH
            error_message = str(e)
            print(f"LỖI DB (Update HocPhan): {error_message}")
            if "FOREIGN KEY constraint 'FK_HOCPHAN'" in error_message:
                 messagebox.showwarning("Lỗi Dữ Liệu", f"Mã môn học '{mamh}' không tồn tại trong bảng Môn Học.")
            # CHECK constraint ít khả năng xảy ra khi update trừ khi sửa MAHP (đang bị cấm)
            else:
                 messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật Học Phần", f"Có lỗi xảy ra khi cập nhật học phần: {e}")
            self.conn.rollback()
            return False

    def delete_hocphan(self, mahp):
        """Xóa học phần."""
        sql_delete = "DELETE FROM HOCPHAN WHERE MAHP = ?"
        try:
            self.cursor.execute(sql_delete, (mahp,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True
            else:
                messagebox.showwarning("Không Tìm Thấy", f"Không tìm thấy mã học phần '{mahp}' để xóa.")
                return False
        except pyodbc.IntegrityError:
            # Lỗi khóa ngoại (nếu HOCPHAN được tham chiếu bởi bảng KETQUA chẳng hạn)
            messagebox.showwarning("Lỗi Ràng Buộc", f"Không thể xóa học phần '{mahp}' vì có thể đang có dữ liệu điểm hoặc đăng ký liên quan.")
            self.conn.rollback()
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Xóa Học Phần", f"Có lỗi xảy ra khi xóa học phần: {e}")
            self.conn.rollback()
            return False

    def find_hocphan(self, search_keyword):
        """Tìm kiếm học phần theo MAHP (số) hoặc MAMH (chữ)."""
        if not search_keyword:
            return self.fetch_all_hocphan()

        sql_find = """
            SELECT HP.MAHP, HP.MAMH, MH.TEN_MH, HP.HOCKY, HP.NAMHOC, HP.GV
            FROM HOCPHAN HP
            JOIN MHOC MH ON HP.MAMH = MH.MAMH
            WHERE CAST(HP.MAHP AS VARCHAR) LIKE ? OR LOWER(HP.MAMH) LIKE ? OR LOWER(MH.TEN_MH) LIKE ? OR LOWER(HP.GV) LIKE ?
            ORDER BY HP.NAMHOC DESC, HP.HOCKY, HP.MAHP
        """
        search_term_like = f"%{search_keyword.lower()}%"
        # Tuple tham số cho 4 vị trí LIKE
        params = (search_term_like, search_term_like, search_term_like, search_term_like)

        try:
            self.cursor.execute(sql_find, params)
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            return columns, rows
        except Exception as e:
            messagebox.showerror("Lỗi Tìm Học Phần", f"Có lỗi xảy ra khi tìm kiếm học phần:\n{e}")
            return [], []
        
    def fetch_student_info(self, masv):
        """Lấy TÊN của sinh viên dựa trên MASV."""
        sql = "SELECT TEN FROM SVIEN WHERE MASV = ?"
        # fetch_mode="one" sẽ trả về một tuple (TEN,) hoặc None
        return self._execute_query(sql, (masv,), fetch_mode="one")

    def fetch_grades_for_student(self, masv):
        """
        Lấy bảng điểm chi tiết cho một sinh viên, JOIN để lấy Tên Môn Học và Số Tín Chỉ.
        """
        sql = """
            SELECT K.MAHP, MH.TEN_MH, MH.SOTINCHI, K.DIEM
            FROM KETQUA K
            JOIN HOCPHAN HP ON K.MAHP = HP.MAHP
            JOIN MHOC MH ON HP.MAMH = MH.MAMH
            WHERE K.MASV = ?
            ORDER BY K.MAHP
        """
        # fetch_mode="all" trả về (columns, rows)
        return self._execute_query(sql, (masv,), fetch_mode="all")

    def calculate_gpa_raw(self, masv):
        """
        Lấy dữ liệu thô để tính GPA: Tổng(Điểm * Tín Chỉ) và Tổng(Tín Chỉ).
        Việc tính toán (chia) sẽ được thực hiện trong Python để tránh lỗi chia cho 0.
        """
        sql = """
            SELECT SUM(K.DIEM * MH.SOTINCHI), SUM(MH.SOTINCHI)
            FROM KETQUA K
            JOIN HOCPHAN HP ON K.MAHP = HP.MAHP
            JOIN MHOC MH ON HP.MAMH = MH.MAMH
            WHERE K.MASV = ? AND K.DIEM IS NOT NULL
        """
        # fetch_mode="one" trả về (SUM_DIEM_TC, SUM_TC)
        return self._execute_query(sql, (masv,), fetch_mode="one")

    def add_or_update_grade(self, masv, mahp, diem):
        """
        Thêm mới hoặc cập nhật điểm (UPSERT) cho sinh viên trong bảng KETQUA.
        Sử dụng MERGE để xử lý cả hai trường hợp (INSERT nếu chưa có, UPDATE nếu đã có).
        """
        sql_merge = """
            MERGE INTO KETQUA AS T
            USING (VALUES (?, ?, ?)) AS S (MASV, MAHP, DIEM)
            ON T.MASV = S.MASV AND T.MAHP = S.MAHP
            WHEN MATCHED THEN 
                UPDATE SET T.DIEM = S.DIEM
            WHEN NOT MATCHED THEN 
                INSERT (MASV, MAHP, DIEM) VALUES (S.MASV, S.MAHP, S.DIEM);
        """
        try:
            # fetch_mode="no_fetch_commit" (đã có trong file của bạn)
            return self._execute_query(sql_merge, (masv, mahp, diem), fetch_mode="no_fetch_commit")
        except pyodbc.IntegrityError as e:
            error_message = str(e)
            print(f"LỖI DB (Update Grade): {error_message}")
            if "CHECK constraint" in error_message and "DIEM" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", "Điểm phải là một số hợp lệ từ 0 đến 10.")
            elif "FOREIGN KEY constraint 'FK_KETQUA'" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", f"Mã sinh viên '{masv}' không tồn tại trong bảng SVIEN.")
            # Lưu ý: Bạn nên thêm FK từ KETQUA(MAHP) -> HOCPHAN(MAHP)
            # Nếu bạn đã thêm, lỗi FK đó cũng sẽ được bắt ở đây.
            else:
                messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật Điểm", f"Đã xảy ra lỗi: {e}")
            return False
    