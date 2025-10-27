# login_view.py (Đã nâng cấp lên CustomTkinter)

import customtkinter as ctk
from tkinter import messagebox  
from PIL import Image, ImageTk

class LoginView:
    def __init__(self, master, db_manager, main_app_class, colors):
        self.master = master
        self.db_manager = db_manager       
        self.MainAppClass = main_app_class 
        self.colors = colors # Lưu lại các mã màu

        self.master.title("Login")
        self.master.geometry("550x300")
        self.master.resizable(False, False)

        # === YÊU CẦU 1: MÀU NỀN LÀ XANH ĐẬM ===
        self.master.configure(fg_color=colors["dark_blue"])

        # === YÊU CẦU 2: LBL_TITLE MÀU VÀNG, IN ĐẬM ===
        self.label_Title = ctk.CTkLabel(
            master, 
            text="PHẦN MỀM QUẢN LÝ SINH VIÊN",
            font=ctk.CTkFont(family="Segoe UI", size=25, weight="bold"),
            text_color=colors["light_gold"]
        )
        self.label_Title.place(anchor="center", x=275, y=40)
        
        # === YÊU CẦU 3: LBL USER/PASS MÀU TRẮNG, IN ĐẬM ===
        self.label_username = ctk.CTkLabel(
            master, 
            text="Username:",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=colors["white"]
        )
        self.label_username.place(x=130, y=100)
        
        # === YÊU CẦU 4: ENTRY NỀN TRẮNG, CHỮ ĐEN/ĐẬM ===
        self.entry_username = ctk.CTkEntry(
            master, 
            width=220, # Tăng độ rộng 1 chút
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=colors["white"],
            text_color=colors["dark_blue"],
            border_width=0, # Bỏ viền
            corner_radius=5
        )
        self.entry_username.place(x=230, y=100)

        # Lable password
        self.label_password = ctk.CTkLabel(
            master, 
            text="Password:",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=colors["white"]
        )
        self.label_password.place(x=130, y=150)
        
        # Entry password
        self.entry_password = ctk.CTkEntry(
            master, 
            show="*", 
            width=220,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=colors["white"],
            text_color=colors["dark_blue"],
            border_width=0,
            corner_radius=5
        )
        self.entry_password.place(x=230, y=150)

        # Hình ảnh con mắt
        open_eye_img = ctk.CTkImage(Image.open(r"D:\Python\DOAN_PYTHON_NHOMDOAN1_DH24TH3_01_01\Items\open_eye.png").resize((20, 19)))
        closed_eye_img = ctk.CTkImage(Image.open(r"D:\Python\DOAN_PYTHON_NHOMDOAN1_DH24TH3_01_01\Items\closed_eye.png").resize((20, 19)))
        
        # Dùng CTkButton cho con mắt (để click dễ hơn)
        self.button_toggle = ctk.CTkButton(
            master, 
            image=closed_eye_img, 
            text="", 
            width=20, 
            fg_color=colors["white"], 
            hover_color=colors["white"], 
            command=self.toggle_password,
            corner_radius=0
        )
        
        # Dùng .place() để đặt đè lên Entry
        self.button_toggle.place(in_=self.entry_password, relx=1.0, rely=0.48, anchor="e", x=-5)
        self.open_eye_img = open_eye_img
        self.closed_eye_img = closed_eye_img
        
        # Button Đăng nhập
        self.button_login = ctk.CTkButton(
            master, 
            text="Login", 
            command=self.login,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=colors["light_gold"],
            text_color=colors["dark_blue"],
            hover_color=colors["dark_gold"]
        )
        self.button_login.place(anchor="center", x=275, y=230)
    
    def toggle_password(self):
        if self.entry_password.cget('show') == '*':
            self.entry_password.configure(show='')
            self.button_toggle.configure(image=self.open_eye_img)
        else:
            self.entry_password.configure(show='*')
            self.button_toggle.configure(image=self.closed_eye_img)

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if username == "admin" and password == "123":
            login_window_to_close = self.master
            login_window_to_close.destroy() 
            root = login_window_to_close.master 
            self.MainAppClass(master=root, db_manager=self.db_manager) 
        else:
            messagebox.showerror("Đăng nhập thất bại", "Tên người dùng hoặc Mật khẩu không hợp lệ.")
            self.entry_password.delete(0, 'end')