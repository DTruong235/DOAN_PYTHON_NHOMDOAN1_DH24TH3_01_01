# main.py (Đã sửa)

import tkinter as tk
from db_manager import DB_Manager
from main_app import MainApp
from login_view import LoginView # Đảm bảo tên file là login_view
import tkinter.messagebox as messagebox
import sys # Import sys

# --- THÔNG SỐ KẾT NỐI DATABASE ---
# Cần giữ lại để MainApp có thể truy cập sinh viên
SERVER_NAME = r'LAPTOP-O68GMDB5' 
DATABASE_NAME = 'QLSV'
SQL_USER = 'sa'
SQL_PASSWORD = '123' 


def main():
    root = tk.Tk()
    root.withdraw() # Ẩn cửa sổ gốc mặc định của Tkinter
    
    # 1. Khởi tạo DB Manager và Kết nối
    db_manager = DB_Manager(SERVER_NAME, DATABASE_NAME, SQL_USER, SQL_PASSWORD)

    if not db_manager.connect():
        # Nếu kết nối thất bại, thoát ứng dụng
        root.destroy()
        sys.exit() # Dùng sys.exit() để thoát triệt để

    # 2. KHỞI CHẠY ỨNG DỤNG BẰNG CỬA SỔ ĐĂNG NHẬP
    login_window = tk.Toplevel(root)
    
    # Truyền db_manager và MainApp Class vào LoginView.
    # LoginView sẽ dùng chúng để mở cửa sổ chính sau khi xác thực cứng thành công.
    LoginView(master=login_window, db_manager=db_manager, main_app_class=MainApp)
    
    # 3. Chạy vòng lặp chính của ứng dụng
    root.mainloop()
    
    # Đảm bảo đóng kết nối khi ứng dụng chính kết thúc
    db_manager.disconnect()

if __name__ == "__main__":
    main()