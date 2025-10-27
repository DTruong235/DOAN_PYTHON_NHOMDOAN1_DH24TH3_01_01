# main.py (Đã nâng cấp lên CustomTkinter)

import customtkinter as ctk
from db_manager import DB_Manager
from main_app import MainApp
from login_view import LoginView 
import sys 

# --- THÔNG SỐ KẾT NỐI DATABASE ---
SERVER_NAME = r'LAPTOP-O68GMDB5' 
DATABASE_NAME = 'QLSV'
SQL_USER = 'sa'
SQL_PASSWORD = '123' 

# --- MÃ MÀU TÙY CHỈNH (TỪ ẢNH) ---
# Dùng cho LoginView
COLOR_DARK_BLUE = "#0f1e3f"
COLOR_LIGHT_GOLD = "#cdaa80"
COLOR_DARK_GOLD = "#997953"
COLOR_WHITE = "#FFFFFF"

def main():
    
    # 1. CÀI ĐẶT THEME CHUNG
    # MainApp nền trắng, nên ta đặt theme chung là "light"
    ctk.set_appearance_mode("light") 
    ctk.set_default_color_theme("blue")

    # 2. KHỞI TẠO CỬA SỔ GỐC
    root = ctk.CTk() # Dùng CTk() thay vì tk.Tk()
    root.withdraw() # Ẩn cửa sổ gốc
    
    # 3. Khởi tạo DB Manager
    db_manager = DB_Manager(SERVER_NAME, DATABASE_NAME, SQL_USER, SQL_PASSWORD)
    if not db_manager.connect():
        root.destroy()
        sys.exit() 

    # 4. Khởi chạy LoginView
    # Dùng CTkToplevel thay vì tk.Toplevel
    login_window = ctk.CTkToplevel(root)
    
    # Truyền các mã màu tùy chỉnh vào LoginView
    LoginView(
        master=login_window, 
        db_manager=db_manager, 
        main_app_class=MainApp,
        colors={
            "dark_blue": COLOR_DARK_BLUE,
            "light_gold": COLOR_LIGHT_GOLD,
            "dark_gold": COLOR_DARK_GOLD,
            "white": COLOR_WHITE
        }
    )
    
    root.mainloop()
    
    db_manager.disconnect()

if __name__ == "__main__":
    main()