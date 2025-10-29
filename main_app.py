import customtkinter as ctk
from tkinter import messagebox

# Import các hằng số
from constants import (
    APP_MID_BLUE, APP_LIGHT_GREY, APP_DARK_BLUE,
    FONT_BOLD_TITLE_APP
)

# Import các Class Tab từ thư mục 'gui'
from gui.student_tab import StudentTab
from gui.subject_tab import SubjectTab
from gui.course_tab import CourseTab
from gui.grade_tab import GradeTab

class MainApp(ctk.CTkToplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.db_manager = db_manager
        self.title("Quản Lý Sinh Viên")
        self.geometry("1100x700")

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Dùng hằng số
        self.configure(fg_color=APP_MID_BLUE)

        self.label_title = ctk.CTkLabel(
            self,
            text=" HỆ THỐNG QUẢN LÝ SINH VIÊN",
            font=FONT_BOLD_TITLE_APP,
            text_color=APP_LIGHT_GREY
        )
        self.label_title.pack(side='top', padx=20, pady=20, anchor="center")

        self._setup_tabs()

    def _on_closing(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát ứng dụng?"):
            self.db_manager.disconnect()
            self.master.destroy() # Phá hủy root (từ LoginView)
            self.destroy()

    def _setup_tabs(self):
        notebook = ctk.CTkTabview(
            self,
            height=500,
            fg_color=APP_MID_BLUE, 
            segmented_button_fg_color=APP_DARK_BLUE,
            segmented_button_selected_color=APP_MID_BLUE,
            segmented_button_selected_hover_color=APP_MID_BLUE,
            segmented_button_unselected_color=APP_DARK_BLUE,
            segmented_button_unselected_hover_color=APP_DARK_BLUE,
            text_color_disabled=APP_LIGHT_GREY
        )
        notebook.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        # 1. Thêm các Tab (chỉ là cái 'vỏ')
        self.tab_sinhvien = notebook.add("Sinh viên")
        self.tab_mohoc = notebook.add("Môn học")
        self.tab_hocphan = notebook.add("Học phần")
        self.tab_bangdiem = notebook.add("Bảng điểm")
        
        # 2. Tạo các Class quản lý và đặt vào Tab
        
        # Tạo instance của StudentTab, đặt nó vào self.tab_sinhvien
        # và truyền db_manager cho nó
        self.student_manager = StudentTab(self.tab_sinhvien, self.db_manager)
        self.student_manager.pack(expand=True, fill="both")
        
        self.subject_manager = SubjectTab(self.tab_mohoc, self.db_manager)
        self.subject_manager.pack(expand=True, fill="both")

        self.course_manager = CourseTab(self.tab_hocphan, self.db_manager)
        self.course_manager.pack(expand=True, fill="both")
        
        self.grade_manager = GradeTab(self.tab_bangdiem, self.db_manager)
        self.grade_manager.pack(expand=True, fill="both")


        # Đặt Tab mặc định
        notebook.set("Sinh viên")

