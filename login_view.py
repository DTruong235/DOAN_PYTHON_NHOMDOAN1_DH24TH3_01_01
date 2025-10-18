import tkinter as tk
from tkinter import messagebox  
from tkinter import ttk
from tkinter import font
from PIL import Image, ImageTk

class LoginView:
    def __init__(self, master,db_manager, main_app_class):
        self.master = master
        self.db_manager = db_manager       # Lưu trữ để dùng cho MainApp
        self.MainAppClass = main_app_class # Class của MainApp

        self.master.title("Login")
        self.master.geometry("550x300")
        self.master.resizable(False, False)

        self.master.config(bg="#FFFFFF")

        style = ttk.Style()
        style.theme_use('clam')

        #Label Tiêu đề
        self.label_Title = ttk.Label(master, text="PHẦN MỀM QUẢN LÝ SINH VIÊN")
        self.label_Title.place(anchor="center", x=275, y=40)
        self.label_Title.config(font=("Segoe UI", 20, 'bold'), foreground="#032E5B", background="#FFFFFF")
        
        #Label user
        self.label_username = ttk.Label(master, text="Username:")
        self.label_username.place(x=130, y=100)
        self.label_username.config(font=("Segoe UI", 12, 'bold'), foreground="#000000", background="#FFFFFF")
        
        style.configure("NoBorder.TEntry", relief="flat", padding=3)                   
        #Entry user. Nhập tên người dùng
        self.entry_username = ttk.Entry(master, width=20,style="NoBorder.TEntry")
        self.entry_username.place(x=230, y=100)
        self.entry_username.config(font=("Segoe UI", 12), foreground="#000000", background="#FFFFFF")

        #Lable password
        self.label_password = ttk.Label(master, text="Password:")
        self.label_password.place(x=130, y=150)
        self.label_password.config(font=("Segoe UI", 12, 'bold'), foreground="#000000", background="#FFFFFF")
        
        #Entry password. Nhập Mật khẩu
        self.entry_password = ttk.Entry(master, show="*",width=20,style="NoBorder.TEntry")
        self.entry_password.place(x=230, y=150)
        self.entry_password.config(font=("Segoe UI", 12), foreground="#000000", background="#FFFFFF")

        #Hình ảnh con mắt mở và nhắm. Dùng để hiện thị hoặc ẩn mật khẩu
        open_eye= ImageTk.PhotoImage(Image.open(r"D:\Python\DOAN_PYTHON_NHOMDOAN1_DH24TH3_01_01\Items\open_eye.png").resize((20, 19)))
        closed_eye= ImageTk.PhotoImage(Image.open(r"D:\Python\DOAN_PYTHON_NHOMDOAN1_DH24TH3_01_01\Items\closed_eye.png").resize((20, 19)))
        self.label_toggle = ttk.Label(master, image=closed_eye)
        self.label_toggle.image = closed_eye
        self.label_toggle.place(x=394, y=152)
        self.open_eye = open_eye
        self.closed_eye = closed_eye
        self.label_toggle.bind("<Button-1>", lambda e: self.toggle_password())
        self.label_toggle.config(background="#FFFFFF")
        
        #Button Đăng nhập
        style.configure('TButton', font=('Segoe UI', 12,'bold'), background="#031B34", foreground="#F6F4F4")
        style.map('TButton', background=[('active', "#9FB8D3")], foreground=[('active', 'white')])
        self.button_login = ttk.Button(master, text="Login",command=self.login, style='TButton')
        self.button_login.place(anchor="center", x=275, y=230)
    
    #Kiểm tra và hiển thị mật khẩu
    def toggle_password(self):
        if self.entry_password.cget('show') == '':
            self.entry_password.config(show='*')
            self.label_toggle.config(image=self.closed_eye)
        else:
            self.entry_password.config(show='')
            self.label_toggle.config(image=self.open_eye)



    def login(self):
            username = self.entry_username.get().strip()
            password = self.entry_password.get().strip()

        # LOGIC XÁC THỰC CỨNG THEO YÊU CẦU
            if username == "admin" and password == "123":
            
            # 1. ĐÓNG CỬA SỔ LOGIN (Toplevel B)
                login_window_to_close = self.master
                login_window_to_close.destroy() 
            
            # 2. KHỞI TẠO CỬA SỔ CHÍNH MỚI (Toplevel C)
            # Cửa sổ cha của Login là root (đã ẩn)
                root = login_window_to_close.master 
             
            # 3. Khởi tạo MainApp, truyền đối tượng DB_Manager đã kết nối
                self.MainAppClass(master=root, db_manager=self.db_manager) 
            
            else:
                messagebox.showerror("Đăng nhập thất bại", "Tên người dùng hoặc Mật khẩu không hợp lệ.")
                self.entry_password.delete(0, tk.END) # Xóa mật khẩu khỏi Entry

