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
        # Lỗi kết nối DB ban đầu (từ db_manager) đã hiển thị messagebox
        root.destroy()
        sys.exit() 

    # 4. Khởi chạy LoginView
    # Dùng CTkToplevel thay vì tk.Toplevel
    login_window = ctk.CTkToplevel(root)
    
    # LoginView sẽ tự import hằng số màu, không cần truyền vào nữa
    LoginView(
        master=login_window, 
        db_manager=db_manager, 
        main_app_class=MainApp
    )
    
    root.mainloop()
    
    # Chỉ disconnect khi root.mainloop() kết thúc (app đóng)
    db_manager.disconnect()

if __name__ == "__main__":
    main()