import customtkinter as ctk
from tkinter import messagebox  
from PIL import Image
import os # Import os để lấy đường dẫn tương đối
import sys

# Import hằng số
from constants import (
    COLOR_DARK_BLUE, COLOR_LIGHT_GOLD, COLOR_DARK_GOLD, COLOR_WHITE,
    FONT_LOGIN_TITLE, FONT_LOGIN_LABEL, FONT_LOGIN_ENTRY, FONT_LOGIN_BUTTON
)

class LoginView:
    # Bỏ tham số 'colors'
    def __init__(self, master, db_manager, main_app_class):
        self.master = master
        self.db_manager = db_manager       
        self.MainAppClass = main_app_class 

        self.master.title("Login")
        self.master.geometry("550x300")
        self.master.resizable(False, False)

        # Lấy đường dẫn thư mục hiện tại của file script
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Nếu 'gui' là một thư mục, bạn cần lùi ra 1 cấp:
        # base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        # Tạm thời dùng đường dẫn tuyệt đối cho 'items'
        # và dùng: base_path = os.path.dirname(sys.argv[0])
        
        # GIẢ ĐỊNH 'items' nằm cùng cấp với 'run_app.py'
        items_path = os.path.join(os.path.dirname(sys.argv[0]), "items")


        # === Dùng hằng số ===
        self.master.configure(fg_color=COLOR_DARK_BLUE)

        # Sửa tên biến: label_Title -> label_title (PEP 8)
        self.label_title = ctk.CTkLabel(
            master, 
            text="QUẢN LÝ SINH VIÊN",
            font=FONT_LOGIN_TITLE,
            text_color=COLOR_LIGHT_GOLD
        )
        self.label_title.place(anchor="center", x=275, y=40)
        
        self.label_username = ctk.CTkLabel(
            master, 
            text="Username:",
            font=FONT_LOGIN_LABEL,
            text_color=COLOR_WHITE
        )
        self.label_username.place(x=130, y=100)
        
        self.entry_username = ctk.CTkEntry(
            master, 
            width=220,
            font=FONT_LOGIN_ENTRY,
            fg_color=COLOR_WHITE,
            text_color=COLOR_DARK_BLUE,
            border_width=0,
            corner_radius=5
        )
        self.entry_username.place(x=230, y=100)

        self.label_password = ctk.CTkLabel(
            master, 
            text="Password:",
            font=FONT_LOGIN_LABEL,
            text_color=COLOR_WHITE
        )
        self.label_password.place(x=130, y=150)
        
        self.entry_password = ctk.CTkEntry(
            master, 
            show="*", 
            width=220,
            font=FONT_LOGIN_ENTRY,
            fg_color=COLOR_WHITE,
            text_color=COLOR_DARK_BLUE,
            border_width=0,
            corner_radius=5
        )
        self.entry_password.place(x=230, y=150)

        # === SỬA ĐƯỜNG DẪN ẢNH ===
        try:
            open_eye_path = os.path.join(items_path, "open_eye.png")
            closed_eye_path = os.path.join(items_path, "closed_eye.png")
            
            open_eye_img = ctk.CTkImage(Image.open(open_eye_path).resize((20, 19)))
            closed_eye_img = ctk.CTkImage(Image.open(closed_eye_path).resize((20, 19)))
        except FileNotFoundError:
            messagebox.showerror("Lỗi Ảnh", f"Không tìm thấy file ảnh trong thư mục: {items_path}\nHãy đảm bảo thư mục 'items' tồn tại.")
            # Tạo ảnh placeholder nếu lỗi
            open_eye_img = None
            closed_eye_img = None
        
        self.button_toggle = ctk.CTkButton(
            master, 
            image=closed_eye_img, 
            text="", 
            width=20, 
            fg_color=COLOR_WHITE, 
            hover_color=COLOR_WHITE, 
            command=self.toggle_password,
            corner_radius=0
        )
        
        self.button_toggle.place(in_=self.entry_password, relx=1.0, rely=0.48, anchor="e", x=-5)
        self.open_eye_img = open_eye_img
        self.closed_eye_img = closed_eye_img
        
        self.button_login = ctk.CTkButton(
            master, 
            text="Login", 
            command=self.login,
            font=FONT_LOGIN_BUTTON,
            fg_color=COLOR_LIGHT_GOLD,
            text_color=COLOR_DARK_BLUE,
            hover_color=COLOR_DARK_GOLD
        )
        self.button_login.place(anchor="center", x=275, y=230)
    
    def toggle_password(self):
        if self.entry_password.cget('show') == '*':
            self.entry_password.configure(show='')
            if self.open_eye_img: self.button_toggle.configure(image=self.open_eye_img)
        else:
            self.entry_password.configure(show='*')
            if self.closed_eye_img: self.button_toggle.configure(image=self.closed_eye_img)

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        # === CẢNH BÁO BẢO MẬT ===
        if username == "admin" and password == "123":
            login_window_to_close = self.master
            login_window_to_close.destroy() 
            root = login_window_to_close.master 
            
            # Khởi chạy MainApp
            try:
                self.MainAppClass(master=root, db_manager=self.db_manager) 
            except Exception as e:
                messagebox.showerror("Lỗi Khởi Chạy", f"Không thể mở ứng dụng chính:\n{e}")
                root.destroy()
        else:
            messagebox.showerror("Đăng nhập thất bại", "Tên người dùng hoặc Mật khẩu không hợp lệ.")
            self.entry_password.delete(0, 'end')