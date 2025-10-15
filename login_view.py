import tkinter as tk
from tkinter import messagebox  
from tkinter import ttk
from tkinter import font
from PIL import Image, ImageTk

class LoginView:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("550x300")
        self.master.resizable(False, False)

        self.master.config(bg="#FFFFFF")

        style = ttk.Style()
        style.theme_use('clam')

        #Label Tiêu đề
        self.label_Title = ttk.Label(master, text="PHẦN MỀM QUẢN LÝ SINH VIÊN")
        self.label_Title.place(anchor="center", x=275, y=40)
        self.label_Title.config(font=("Arial", 20, 'bold'), foreground="#032E5B", background="#FFFFFF")
        
        #Label user
        self.label_username = ttk.Label(master, text="Username:")
        self.label_username.place(x=130, y=100)
        self.label_username.config(font=("Arial", 12, 'bold'), foreground="#000000", background="#FFFFFF")
        
        style.configure("NoBorder.TEntry", relief="flat", padding=3)                   
        #Entry user. Nhập tên người dùng
        self.entry_username = ttk.Entry(master, width=20,style="NoBorder.TEntry")
        self.entry_username.place(x=230, y=100)
        self.entry_username.config(font=("Arial", 12), foreground="#000000", background="#FFFFFF")

        #Lable password
        self.label_password = ttk.Label(master, text="Password:")
        self.label_password.place(x=130, y=150)
        self.label_password.config(font=("Arial", 12, 'bold'), foreground="#000000", background="#FFFFFF")
        
        #Entry password. Nhập Mật khẩu
        self.entry_password = ttk.Entry(master, show="*",width=20,style="NoBorder.TEntry")
        self.entry_password.place(x=230, y=150)
        self.entry_password.config(font=("Arial", 12), foreground="#000000", background="#FFFFFF")

        #Hình ảnh con mắt mở và nhắm. Dùng để hiện thị hoặc ẩn mật khẩu
        open_eye= ImageTk.PhotoImage(Image.open("D:\Python\DTH235802_LAMDUCTRUONG_DOAN\Items\open_eye.png").resize((20, 19)))
        closed_eye= ImageTk.PhotoImage(Image.open("D:\Python\DTH235802_LAMDUCTRUONG_DOAN\Items\closed_eye.png").resize((20, 19)))
        self.label_toggle = ttk.Label(master, image=closed_eye)
        self.label_toggle.image = closed_eye
        self.label_toggle.place(x=394, y=152)
        self.open_eye = open_eye
        self.closed_eye = closed_eye
        self.label_toggle.bind("<Button-1>", lambda e: self.toggle_password())
        self.label_toggle.config(background="#FFFFFF")
        
        #Button Đăng nhập
        style.configure('TButton', font=('Arial', 12,'bold'), background="#031B34", foreground="#F6F4F4")
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

    #Kiểm tra tài khoảng đăng nhập
    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username == "admin" and password == "123":
            #Xử lý chuyển đổi cửa sổ an toàn:
            self.master.withdraw()
            main_window = tk.Toplevel(self.master) 
            self.MainApp(master=main_window, db_manager=self.db_manager)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        

