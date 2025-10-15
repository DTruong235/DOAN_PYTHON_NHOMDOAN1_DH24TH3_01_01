# main.py

import tkinter as tk
from db_manager import DB_Manager
from main_app import MainApp
import tkinter.messagebox as messagebox

# --- THÔNG SỐ KẾT NỐI DATABASE ---

SERVER_NAME = 'LAPTOP-O68GMDB5' 
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
        return

    # --- SIMULATE LOGIN SUCCESS ---
    
    app = MainApp(master=root, db_manager=db_manager)
    
    # 3. Chạy vòng lặp chính của ứng dụng
    root.mainloop()

if __name__ == "__main__":
    main()