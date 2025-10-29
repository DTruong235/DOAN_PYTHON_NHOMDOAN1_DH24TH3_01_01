import pyodbc
import tkinter.messagebox as messagebox # CHỈ DÙNG CHO HÀM connect() ban đầu

class DB_Manager:
    """
    Quản lý kết nối và các thao tác CRUD an toàn với MSSQL Server.
    Sử dụng truy vấn tham số hóa (Parameterized Queries) để ngăn chặn SQL Injection.[1]
    [1] https://learn.microsoft.com/en-us/sql/relational-databases/security/sql-injection?view=sql-server-ver16

    """
    def __init__(self, server_name, database_name, username, password):
        self.server_name = server_name
        self.database_name = database_name
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None
        self.connection_string = self._build_connection_string()

    def _build_connection_string(self):
        DRIVER_NAME = '{ODBC Driver 18 for SQL Server}' 
        if self.username and self.password:
            return (
                f'DRIVER={DRIVER_NAME};'
                f'SERVER={self.server_name};'
                f'DATABASE={self.database_name};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'TrustServerCertificate=yes;'
            )
        else:
            return (
                f'DRIVER={DRIVER_NAME};'
                f'SERVER={self.server_name};'
                f'DATABASE={self.database_name};'
                f'Trusted_Connection=yes;'
                f'TrustServerCertificate=yes;'
            )

    def connect(self):
        """Mở kết nối database. Đây là nơi duy nhất dùng messagebox."""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            return True
        except pyodbc.Error as ex:
            sqlstate = ex.args
            # Đây là trường hợp ngoại lệ duy nhất được phép dùng messagebox,
            # vì nếu kết nối thất bại, app không thể chạy.
            messagebox.showerror("Lỗi Kết Nối Database", f"Không thể kết nối tới SQL Server.\nLỗi: {sqlstate}")
            self.conn = None
            self.cursor = None
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def _execute_query(self, sql, params=None, fetch_mode="all"):
        """
        Thực thi truy vấn và xử lý lỗi chung.
        TỐI ƯU: Ném (raise) lỗi thay vì hiển thị messagebox.
        """
        if not self.conn or not self.cursor:
            # Nếu mất kết nối, ném lỗi để app xử lý
            raise ConnectionError("Mất kết nối đến database.")

        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            if fetch_mode == "all":
                columns = [desc[0] for desc in self.cursor.description]
                rows = [tuple(str(item) if item is not None else "" for item in row) for row in self.cursor.fetchall()]
                return columns, rows
            elif fetch_mode == "one":
                result = self.cursor.fetchone()
                processed_result = tuple(str(item) if item is not None else "" for item in result) if result else None
                return processed_result
            elif fetch_mode == "commit":
                rowcount = self.cursor.rowcount
                self.conn.commit()
                return rowcount
            elif fetch_mode == "no_fetch_commit":
                self.conn.commit()
                return True
            else: 
                return None

        except (pyodbc.IntegrityError, pyodbc.Error) as e:
             if self.conn: self.conn.rollback() # QUAN TRỌNG: Rollback
             print(f"LỖI DB (pyodbc): {e}")
             raise e # Ném lỗi lên cho lớp UI (Tab) xử lý
        except Exception as e:
            print(f"LỖI PYTHON (_execute_query): {e}")
            raise e

    # --- READ (Sinh Viên) ---
    def fetch_all_students(self):
        sql = """
            SELECT MASV, TEN, GIOITINH, 
                   CONVERT(varchar, NGAYSINH, 103) AS NGAYSINH_FORMATTED, 
                   DIACHI, KHOAHOC, KHOA, EMAIL 
            FROM SVIEN 
            ORDER BY MASV
            """
        # _execute_query sẽ ném lỗi nếu có
        return self._execute_query(sql, fetch_mode="all")

    # --- CREATE (Sinh Viên) ---
    def add_student(self, masv, ten, gioitinh,ngaysinh, diachi ,khoahoc, khoa, email):
        sql_insert = "INSERT INTO SVIEN (MASV, TEN, GIOITINH, NGAYSINH, DIACHI, KHOAHOC, KHOA, EMAIL) VALUES (?,?,?,?,?,?,?,?)"
        data_to_insert = (masv, ten, gioitinh, ngaysinh, diachi ,khoahoc, khoa, email)
        
        # _execute_query sẽ ném (raise) pyodbc.IntegrityError nếu thất bại
        self._execute_query(sql_insert, data_to_insert, fetch_mode="no_fetch_commit")
        return True # Trả về True nếu không có lỗi

    # --- DELETE (Sinh Viên) ---
    def delete_student(self, masv):
        sql_delete = "DELETE FROM SVIEN WHERE MASV =?"
        
        # _execute_query sẽ ném (raise) pyodbc.IntegrityError nếu thất bại (lỗi FK)
        rowcount = self._execute_query(sql_delete, (masv,), fetch_mode="commit")
        
        if rowcount > 0:
            return True
        else:
            # Ném lỗi tùy chỉnh nếu không tìm thấy
            raise ValueError(f"Không tìm thấy sinh viên có mã '{masv}' để xóa.")

    # --- UPDATE (Sinh Viên) ---
    def update_student(self, masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email):
        sql_update = """
            UPDATE SVIEN 
            SET TEN = ?, GIOITINH = ?, NGAYSINH = ?, DIACHI = ?, 
                KHOAHOC = ?, KHOA = ?, EMAIL = ?
            WHERE MASV = ?
        """
        data_to_update = (ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email, masv)
        
        rowcount = self._execute_query(sql_update, data_to_update, fetch_mode="commit")
        
        if rowcount > 0:
            return True
        else:
            raise ValueError(f"Không tìm thấy sinh viên '{masv}' hoặc không có thông tin thay đổi.")

    # --- FIND (Sinh Viên) ---
    def find_student(self,masv):
        if not masv:
            return self.fetch_all_students()
        
        search_term = f"%{masv.upper()}%" # Thường tìm MASV theo chữ hoa
        sql_find = """
            SELECT MASV, TEN, GIOITINH, 
                   CONVERT(varchar, NGAYSINH, 103) AS NGAYSINH_FORMATTED, 
                   DIACHI, KHOAHOC, KHOA, EMAIL 
            FROM SVIEN 
            WHERE MASV LIKE ?
            ORDER BY MASV
        """
        params = (search_term,)
        return self._execute_query(sql_find, params, fetch_mode="all")
        
    # --- CRUD MÔN HỌC ---
    
    def fetch_all_subjects(self):
        sql = "SELECT MAMH, TEN_MH, SOTINCHI, KHOA FROM MHOC ORDER BY MAMH"
        return self._execute_query(sql, fetch_mode="all")
    
    def add_subject(self, mamh, ten_mh, sotinchi, khoa='CNTT'):
        sql_insert = "INSERT INTO MHOC (MAMH, TEN_MH, SOTINCHI, KHOA) VALUES (?, ?, ?, ?)"
        data_to_insert = (mamh.lower(), ten_mh, sotinchi, khoa)
        self._execute_query(sql_insert, data_to_insert, fetch_mode="no_fetch_commit")
        return True

    def update_subject(self, mamh, ten_mh, sotinchi, khoa='CNTT'):
        sql_update = "UPDATE MHOC SET TEN_MH = ?, SOTINCHI = ?, KHOA = ? WHERE MAMH = ?"
        data_to_update = (ten_mh, sotinchi, khoa, mamh)
        rowcount = self._execute_query(sql_update, data_to_update, fetch_mode="commit")
        if rowcount == 0:
            raise ValueError(f"Không tìm thấy môn học '{mamh}' hoặc không có gì thay đổi.")
        return True

    def delete_subject(self, mamh):
        sql_delete = "DELETE FROM MHOC WHERE MAMH = ?"
        rowcount = self._execute_query(sql_delete, (mamh,), fetch_mode="commit")
        if rowcount == 0:
            raise ValueError(f"Không tìm thấy môn học '{mamh}' để xóa.")
        return True
        
    def find_subject(self, search_keyword):
        if not search_keyword:
            return self.fetch_all_subjects()
        search_term = f"%{search_keyword.lower()}%"
        sql_find = "SELECT MAMH, TEN_MH, SOTINCHI, KHOA FROM MHOC WHERE LOWER(MAMH) LIKE ? ORDER BY MAMH"
        return self._execute_query(sql_find, (search_term,), fetch_mode="all")
        
    # --- CRUD HỌC PHẦN ---
    
    def fetch_all_hocphan(self):
        sql = """
            SELECT HP.MAHP, HP.MAMH, MH.TEN_MH, HP.HOCKY, HP.NAMHOC, HP.GV
            FROM HOCPHAN HP
            JOIN MHOC MH ON HP.MAMH = MH.MAMH
            ORDER BY HP.MAHP
        """
        return self._execute_query(sql, fetch_mode="all")

    def add_hocphan(self, mahp, mamh, hocky, namhoc, gv):
        sql_insert = "INSERT INTO HOCPHAN (MAHP, MAMH, HOCKY, NAMHOC, GV) VALUES (?, ?, ?, ?, ?)"
        data_to_insert = (mahp, mamh.lower(), hocky, namhoc, gv)
        self._execute_query(sql_insert, data_to_insert, fetch_mode="no_fetch_commit")
        return True

    def update_hocphan(self, mahp, mamh, hocky, namhoc, gv):
        sql_update = "UPDATE HOCPHAN SET MAMH = ?, HOCKY = ?, NAMHOC = ?, GV = ? WHERE MAHP = ?"
        data_to_update = (mamh.lower(), hocky, namhoc, gv, mahp)
        rowcount = self._execute_query(sql_update, data_to_update, fetch_mode="commit")
        if rowcount == 0:
            raise ValueError(f"Không tìm thấy học phần '{mahp}' hoặc không có gì thay đổi.")
        return True

    def delete_hocphan(self, mahp):
        sql_delete = "DELETE FROM HOCPHAN WHERE MAHP = ?"
        rowcount = self._execute_query(sql_delete, (mahp,), fetch_mode="commit")
        if rowcount == 0:
            raise ValueError(f"Không tìm thấy học phần '{mahp}' để xóa.")
        return True

    def find_hocphan(self, search_keyword):
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
        params = (search_term_like, search_term_like, search_term_like, search_term_like)
        return self._execute_query(sql_find, params, fetch_mode="all")

    # --- (MỚI) CÁC HÀM CHO TAB BẢNG ĐIỂM ---
    # (Các hàm này được gọi trong main_app.py nhưng bị thiếu trong db_manager.py)

    def fetch_student_info(self, masv):
        """Lấy Tên của một SV."""
        sql = "SELECT TEN FROM SVIEN WHERE MASV = ?"
        # Trả về tuple (TEN,) hoặc None
        return self._execute_query(sql, (masv,), fetch_mode="one")

    def fetch_grades_for_student(self, masv):
        """Lấy bảng điểm chi tiết của một SV."""
        sql = """
            SELECT K.MAHP, M.TEN_MH, M.SOTINCHI, K.DIEM
            FROM KETQUA K
            JOIN HOCPHAN H ON K.MAHP = H.MAHP
            JOIN MHOC M ON H.MAMH = M.MAMH
            WHERE K.MASV = ?
            ORDER BY H.NAMHOC, H.HOCKY
        """
        return self._execute_query(sql, (masv,), fetch_mode="all")

    def calculate_gpa_raw(self, masv):
        """Tính tổng điểm * tín chỉ VÀ tổng tín chỉ."""
        sql = """
            SELECT SUM(K.DIEM * M.SOTINCHI), SUM(M.SOTINCHI)
            FROM KETQUA K
            JOIN HOCPHAN H ON K.MAHP = H.MAHP
            JOIN MHOC M ON H.MAMH = M.MAMH
            WHERE K.MASV = ? AND K.DIEM IS NOT NULL
        """
        # Trả về (SUM, SUM) hoặc (None, None)
        return self._execute_query(sql, (masv,), fetch_mode="one")

    def add_or_update_grade(self, masv, mahp, diem):
        """Dùng MERGE để INSERT hoặc UPDATE điểm."""
        sql_merge = """
            MERGE INTO KETQUA AS T
            USING (VALUES (?, ?, ?)) AS S (MASV, MAHP, DIEM)
            ON T.MASV = S.MASV AND T.MAHP = S.MAHP
            WHEN MATCHED THEN
                UPDATE SET DIEM = S.DIEM
            WHEN NOT MATCHED THEN
                INSERT (MASV, MAHP, DIEM) VALUES (S.MASV, S.MAHP, S.DIEM);
        """
        try:
            mahp_int = int(mahp)
        except ValueError:
            raise ValueError("Mã học phần phải là một số.")
        
        # Sẽ ném IntegrityError nếu MASV hoặc MAHP không tồn tại (lỗi FK)
        return self._execute_query(sql_merge, (masv, mahp_int, diem), fetch_mode="no_fetch_commit")
    
    def delete_grade(self, masv, mahp):
        """Xóa một dòng điểm cụ thể khỏi bảng KETQUA."""
        sql_delete = "DELETE FROM KETQUA WHERE MASV = ? AND MAHP = ?"
        
        try:
            mahp_int = int(mahp)
        except ValueError:
            raise ValueError("Mã học phần phải là một số.")
            
        params = (masv, mahp_int)
        
        # _execute_query sẽ ném lỗi nếu có
        # Dùng fetch_mode="commit" để lấy rowcount
        rowcount = self._execute_query(sql_delete, params, fetch_mode="commit")
        
        if rowcount == 0:
            # Ném lỗi tùy chỉnh nếu không tìm thấy
            raise ValueError(f"Không tìm thấy điểm cho SV '{masv}' và HP '{mahp}' để xóa.")
        
        return True # Xóa thành công