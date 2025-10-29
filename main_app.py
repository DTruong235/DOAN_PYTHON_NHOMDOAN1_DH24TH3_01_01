# main_app.py (Updated with New Colors and CTk)

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import re
from datetime import datetime

# --- Define New Colors (from image_aa6640.jpg) ---
NEW_DARK_BLUE = "#142143"
NEW_YELLOW = "#ffaf00"
NEW_LIGHT_GREY = "#e4e4e4" # Use this for white text
NEW_MID_BLUE = "#1a5d94"
COLOR_WHITE = "#FFFFFF"

# Darker Yellow for hover
BUTTON_HOVER_YELLOW = "#EAA000"

class MainApp(ctk.CTkToplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.db_manager = db_manager
        self.title("Quản Lý Sinh Viên")
        self.geometry("1100x700")

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # === 1. MainApp Background: Mid-Blue ===
        self.configure(fg_color=NEW_MID_BLUE)

        # Adjust title label color for new background
        self.label_Title = ctk.CTkLabel(
            self,
            text=" QUẢN LÝ SINH VIÊN",
            font=ctk.CTkFont(family="Segoe UI", size=27, weight="bold"),
            text_color=NEW_LIGHT_GREY # Use light grey/white for title text
        )
        self.label_Title.pack(side='top', padx=20, pady=20, anchor="center")

        self._setup_tabs()

    def _on_closing(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát ứng dụng?"):
            self.db_manager.disconnect()
            self.master.destroy()
            self.destroy()

    def _setup_tabs(self):
        notebook = ctk.CTkTabview(
            self,
            height=500,
            fg_color=NEW_MID_BLUE, # Match main background
            segmented_button_fg_color=NEW_DARK_BLUE,
            segmented_button_selected_color=NEW_MID_BLUE,
            segmented_button_selected_hover_color=NEW_MID_BLUE,
            segmented_button_unselected_color=NEW_DARK_BLUE,
            segmented_button_unselected_hover_color=NEW_DARK_BLUE,
            text_color_disabled=NEW_LIGHT_GREY
        )
        notebook.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        self.tab_sinhvien = notebook.add("Sinh viên")
        self.tab_mohoc = notebook.add("Môn học")
        self.tab_hocphan = notebook.add("Học phần")
        self.tab_bangdiem = notebook.add("Bảng điểm")
        notebook.set("Sinh viên")

        self._setup_layout_sinhvien(self.tab_sinhvien)
        self._setup_layout_monhoc(self.tab_mohoc)
        self._setup_layout_hocphan(self.tab_hocphan)
        self._setup_layout_bangdiem(self.tab_bangdiem)

    def _setup_layout_sinhvien(self, parent):
        # Configure parent grid layout
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0) # Input frame row
        parent.rowconfigure(1, weight=0) # Search frame row
        parent.rowconfigure(2, weight=1) # Treeview row (expands)

        # === 2. Frame Background: Dark Blue ===
        frame_fg_color = NEW_DARK_BLUE

        self.input_frame = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")

        self.search_bar_frame = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        self.search_bar_frame.grid(row=1, column=0, padx=10, pady=5, sticky="new")

        # Treeview frame also dark blue
        tree_frame = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_frame = tree_frame

        self._setup_input_fields()
        self._setup_student_treeview()
        self.load_students()

    def _setup_input_fields(self):
        input_frame = self.input_frame
        self.entries = {}

        # === 4. Labels in Frames: White Text ===
        label_font = ctk.CTkFont(weight="bold")
        label_text_color = NEW_LIGHT_GREY # Use light grey for "white"

        # === 3. Entries: Keep white bg, yellow border ===
        entry_border_color = NEW_YELLOW
        entry_fg_color = COLOR_WHITE
        entry_text_color = NEW_DARK_BLUE # Keep dark text in entries

        # --- Input Widgets ---
        ctk.CTkLabel(input_frame, text="MSSV", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        entry_masv = ctk.CTkEntry(input_frame, width=150, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_masv.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        self.entries['masv'] = entry_masv

        ctk.CTkLabel(input_frame, text="Họ và tên", font=label_font, text_color=label_text_color).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        entry_ten = ctk.CTkEntry(input_frame, width=200, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_ten.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        self.entries['ten'] = entry_ten

        rad_gt = ctk.StringVar(value="Nam")
        ctk.CTkLabel(input_frame, text="Giới tính", font=label_font, text_color=label_text_color).grid(row=2, column=0, padx=(15, 5), pady=8, sticky="w")
        # Radio buttons need white text too
        radio_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        ctk.CTkRadioButton(radio_frame, text="Nam", value="Nam", variable=rad_gt, text_color=label_text_color).pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="Nữ", value="Nu", variable=rad_gt, text_color=label_text_color).pack(side="left", padx=10)
        radio_frame.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        self.entries['gioitinh'] = rad_gt

        ctk.CTkLabel(input_frame, text="Ngày sinh", font=label_font, text_color=label_text_color).grid(row=3, column=0, padx=(15, 5), pady=8, sticky="w")
        entry_ngaysinh = DateEntry(input_frame, width=20, date_pattern='dd/MM/yyyy', borderwidth=2,font=("Segoe UI", 13))
        style = ttk.Style() # Style DateEntry
        style.configure('DateEntry', fieldbackground=entry_fg_color, foreground=entry_text_color, bordercolor=entry_border_color, arrowcolor=entry_text_color)
        entry_ngaysinh.grid(row=3, column=1, padx=5, pady=8, sticky="w")
        entry_ngaysinh.delete(0, tk.END)
        self.entries['ngaysinh'] = entry_ngaysinh

        # Second column of inputs
        ctk.CTkLabel(input_frame, text="Địa chỉ", font=label_font, text_color=label_text_color).grid(row=0, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_diachi = ctk.CTkEntry(input_frame, width=200, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_diachi.grid(row=0, column=3, padx=5, pady=8, sticky="w")
        self.entries['diachi'] = entry_diachi

        ctk.CTkLabel(input_frame, text="Khóa học", font=label_font, text_color=label_text_color).grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_khoahoc = ctk.CTkEntry(input_frame, width=80, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_khoahoc.grid(row=1, column=3, padx=5, pady=8, sticky="w")
        self.entries['khoahoc'] = entry_khoahoc

        ctk.CTkLabel(input_frame, text="Khoa", font=label_font, text_color=label_text_color).grid(row=2, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_khoa = ctk.CTkEntry(input_frame, width=150, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_khoa.grid(row=2, column=3, padx=5, pady=8, sticky="w")
        self.entries['khoa'] = entry_khoa

        ctk.CTkLabel(input_frame, text="Email", font=label_font, text_color=label_text_color).grid(row=3, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_email = ctk.CTkEntry(input_frame, width=200, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_email.grid(row=3, column=3, padx=5, pady=8, sticky="w")
        self.entries['email'] = entry_email

        # --- Buttons ---
        # === 5. Buttons in Frames: Yellow Bg, White Text ===
        button_font = ctk.CTkFont(weight="bold")
        button_fg_color = NEW_YELLOW
        button_hover_color = BUTTON_HOVER_YELLOW
        button_text_color = COLOR_WHITE # Change text to white

        ctk.CTkButton(input_frame, text="Thêm SV", command=self.handle_add_student,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=0, column=4, padx=15, pady=8, sticky="ew")
        # Delete button stays red, but text white
        ctk.CTkButton(input_frame, text="Xóa SV", command=self.handle_delete_student,
                      font=button_font, fg_color="#D32F2F", hover_color="#B71C1C", text_color=button_text_color
                      ).grid(row=1, column=4, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(input_frame, text="Sửa SV", command=self.handle_update_student,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=2, column=4, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(input_frame, text="Làm Mới", command=self.handle_refresh_data,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=3, column=4, padx=15, pady=8, sticky="ew")

        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(4, weight=0)

        # --- Search Bar ---
        search_frame = self.search_bar_frame
        search_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Tìm kiếm Mã SV:", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_masv = ctk.CTkEntry(search_frame, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color,placeholder_text="Nhập mã sinh viên...")
        entry_search_masv.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.entries['search_masv'] = entry_search_masv
        # Search button: Yellow Bg, White Text
        ctk.CTkButton(search_frame, text="Tìm", command=self.handle_search_and_load, width=80,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=0, column=2, padx=15, pady=10)

    
    def _setup_student_treeview(self):
        style = ttk.Style()
        style.theme_use("clam") # Essential for ttk styling

        # Colors (Keep as before for white treeview)
        bg_color = "white"
        text_color = "black"
        header_bg = ctk.ThemeManager.theme["CTkButton"]["fg_color"][0] # Use CTk default blue for header
        header_fg = "white"
        selected_bg = NEW_YELLOW # Use yellow selection to match buttons
        selected_fg = NEW_DARK_BLUE # Dark blue text when selected

        style.configure("Treeview",
                        background=bg_color,
                        fieldbackground=bg_color,
                        foreground=text_color,
                        rowheight=28,
                        relief="flat",
                        font=("Segoe UI", 11))

        style.configure("Treeview.Heading",
                        background=header_bg,
                        foreground=header_fg,
                        font=("Segoe UI", 11, "bold"),
                        relief="flat",
                        padding=(10, 5))

        style.map("Treeview.Heading",
                  background=[('active', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        style.map("Treeview",
                  background=[('selected', selected_bg)],
                  foreground=[('selected', selected_fg)])

        columns = ("MASV", "TEN", "GIOITINH","NGAYSINH","DIACHI","KHOAHOC", "KHOA","EMAIL")
        # Ensure master is self.tree_frame (the dark blue CTkFrame)
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', style="Treeview")

        # Column configuration (Keep as before)
        self.tree.column('#0', width=0, stretch=False)
        self.tree.heading("MASV", text="Mã SV", anchor='center')
        self.tree.heading("TEN", text="Họ Tên", anchor='w')
        self.tree.heading("GIOITINH", text="Giới tính", anchor='center')
        self.tree.heading("NGAYSINH", text="Ngày sinh", anchor='w')
        self.tree.heading("DIACHI", text="Địa chỉ", anchor='w')
        self.tree.heading("KHOAHOC", text="Khóa học", anchor='center')
        self.tree.heading("KHOA", text="Khoa", anchor='w')
        self.tree.heading("EMAIL", text="Email", anchor='w')

        self.tree.column("MASV", width=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("TEN", width=180, anchor=tk.W)
        self.tree.column("GIOITINH", width=70, anchor=tk.CENTER, stretch=False)
        self.tree.column("NGAYSINH", width=100, anchor=tk.W, stretch=False)
        self.tree.column("DIACHI", width=200, anchor=tk.W)
        self.tree.column("KHOAHOC", width=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("KHOA", width=120, anchor=tk.W)
        self.tree.column("EMAIL", width=200, anchor=tk.W)

        # Use CTkScrollbar, place inside tree_frame
        scrollbar_y = ctk.CTkScrollbar(self.tree_frame, command=self.tree.yview)
        scrollbar_x = ctk.CTkScrollbar(self.tree_frame, command=self.tree.xview, orientation="horizontal")
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Place Treeview and scrollbars within the dark blue tree_frame
        self.tree.grid(row=0, column=0, sticky='nsew', padx=(5,0), pady=(5,0))
        scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(0,5), pady=5)
        scrollbar_x.grid(row=1, column=0, sticky='ew', padx=5, pady=(0,5))
        # Configure grid for tree_frame
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)


        self.tree.bind("<<TreeviewSelect>>", self._on_student_select)
    
    def _populate_treeview(self, students_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for student_row in students_list:
            self.tree.insert("", tk.END, values=student_row)

    def load_students(self):
        columns, students = self.db_manager.fetch_all_students()
        if columns is not None:
            self._populate_treeview(students)

    def _get_and_validate_form_data(self):
        try:
            masv_raw = self.entries['masv'].get().strip()
            ten = self.entries['ten'].get().strip()
            gioitinh = self.entries['gioitinh'].get()
            ngaysinh_raw = self.entries['ngaysinh'].get().strip()
            diachi_raw = self.entries['diachi'].get().strip()
            khoahoc_str = self.entries['khoahoc'].get().strip()
            khoa_raw = self.entries['khoa'].get().strip()
            email_raw = self.entries['email'].get().strip()
        except KeyError as e:
            messagebox.showerror("Lỗi Cấu hình", f"Lỗi truy cập Entry field {e}.")
            return None

        if not masv_raw:
             messagebox.showwarning("Thiếu thông tin", "Mã sinh viên (MASV) không được để trống.")
             return None
        masv = masv_raw.upper()
        if not re.match(r'^[A-Z]\d{3}$', masv):
            messagebox.showwarning("Lỗi Dữ liệu", "Định dạng Mã sinh viên không hợp lệ. (Yêu cầu: 1 chữ cái và 3 số, ví dụ: 'A123')")
            return None
        if not ten or not khoahoc_str:
             messagebox.showwarning("Thiếu thông tin", "Họ Tên và Khóa học không được để trống.")
             return None
        try:
            khoahoc = int(khoahoc_str)
            if khoahoc <= 0:
                 messagebox.showwarning("Lỗi dữ liệu", "Khóa học phải là số dương.")
                 return None
        except ValueError:
            messagebox.showwarning("Lỗi dữ liệu", "Khóa học phải là một con số.")
            return None

        email = None
        if email_raw:
            email_regex = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
            if not re.match(email_regex, email_raw):
                messagebox.showwarning("Lỗi Dữ liệu", "Định dạng Email không hợp lệ. (Yêu cầu: gmail.com)")
                return None
            email = email_raw

        ngaysinh = None
        if ngaysinh_raw:
            try:
                date_obj = datetime.strptime(ngaysinh_raw, '%d/%m/%Y')
                ngaysinh = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Lỗi Dữ liệu", "Định dạng Ngày sinh không hợp lệ. (Yêu cầu: DD/MM/YYYY)")
                return None

        diachi = diachi_raw if diachi_raw else None
        khoa = khoa_raw if khoa_raw else None

        return (masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email)

    def handle_add_student(self):
        data = self._get_and_validate_form_data()
        if data is None: return
        masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email = data
        if self.db_manager.add_student(masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email):
            messagebox.showinfo("Thành công", f"Đã thêm sinh viên {ten} ({masv}).")
            self.handle_refresh_data()

    def handle_delete_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lựa chọn", "Vui lòng chọn một sinh viên trong danh sách để xóa.")
            return
        values = self.tree.item(selected_item[0], 'values')
        try:
            masv = values[0]; ten = values[1]
        except IndexError:
            messagebox.showerror("Lỗi", "Không thể lấy thông tin sinh viên để xóa.")
            return
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa sinh viên {ten} ({masv})?"):
            if self.db_manager.delete_student(masv):
                messagebox.showinfo("Thành công", f"Đã xóa sinh viên {ten} ({masv}).")
                self.handle_refresh_data()

    def _clear_entries(self):
        for key, entry_widget in self.entries.items():
            if isinstance(entry_widget, (ctk.CTkEntry, DateEntry)):
                if key == 'search_masv':
                    continue
                if key == 'masv':
                    entry_widget.configure(state='normal') # Use configure
                    entry_widget.delete(0, 'end')
                else:
                    entry_widget.delete(0, 'end')
            elif isinstance(entry_widget, ctk.StringVar): # Use CTkStringVar
                if key == 'gioitinh':
                    entry_widget.set("Nam")

    def handle_refresh_data(self):
        self._clear_entries()
        self.entries['search_masv'].delete(0, 'end')
        self.load_students()

    def handle_search_and_load(self):
        try:
            search_keyword = self.entries['search_masv'].get().strip()
            columns, students = None, []
            results = self.db_manager.find_student(search_keyword)
            if results and len(results) == 2:
                columns, students = results
            if not students:
                if search_keyword:
                    messagebox.showinfo("Tìm kiếm", f"Không tìm thấy sinh viên nào khớp với '{search_keyword}'.")
                self._populate_treeview([])
                return
            self._populate_treeview(students)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn Hệ thống", f"Đã xảy ra lỗi khi thực hiện tìm kiếm:\n{e}")

    def _on_student_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        values = self.tree.item(selected_item[0], 'values')
        
        try:
            self._clear_entries()
            self.entries['masv'].insert(0, values[0])
            self.entries['ten'].insert(0, values[1])
            self.entries['gioitinh'].set(values[2])
            self.entries['ngaysinh'].insert(0, values[3])
            self.entries['diachi'].insert(0, values[4])
            self.entries['khoahoc'].insert(0, values[5])
            self.entries['khoa'].insert(0, values[6])
            self.entries['email'].insert(0, values[7])
            self.entries['masv'].configure(state='disabled') # Use 'disabled' for CTkEntry
        except (IndexError, KeyError) as e:
             messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải thông tin sinh viên. Lỗi: {e}")

    def handle_update_student(self):
        data = self._get_and_validate_form_data()
        if data is None: return
        masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email = data
        if self.db_manager.update_student(masv, ten, gioitinh, ngaysinh, diachi, khoahoc, khoa, email):
            messagebox.showinfo("Thành công", f"Đã cập nhật sinh viên {ten} ({masv}).")
            self.handle_refresh_data()
        else:
            pass

    def _setup_layout_monhoc(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0); parent.rowconfigure(1, weight=0); parent.rowconfigure(2, weight=1)

        frame_fg_color = NEW_DARK_BLUE

        input_frame_mh = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        input_frame_mh.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self.subject_entries = {}

        input_frame_mh.columnconfigure((0, 2), weight=0); input_frame_mh.columnconfigure((1, 3), weight=1)
        label_font = ctk.CTkFont(weight="bold"); label_text_color = NEW_LIGHT_GREY
        entry_border_color = NEW_YELLOW; entry_fg_color = COLOR_WHITE; entry_text_color = NEW_DARK_BLUE

        # MaMH
        ctk.CTkLabel(input_frame_mh, text="Mã Môn Học (MAMH)", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_mamh = ctk.CTkEntry(input_frame_mh, width=150, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_mamh.grid(row=0, column=1, padx=5, pady=10, sticky="w"); self.subject_entries['mamh'] = entry_mamh

        # TenMH
        ctk.CTkLabel(input_frame_mh, text="Tên Môn Học (TENMH)", font=label_font, text_color=label_text_color).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_tenmh = ctk.CTkEntry(input_frame_mh, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_tenmh.grid(row=1, column=1, columnspan=3, padx=5, pady=10, sticky="ew"); self.subject_entries['tenmh'] = entry_tenmh
        
        # SoTC
        ctk.CTkLabel(input_frame_mh, text="Số Tín Chỉ (SOTC)", font=label_font, text_color=label_text_color).grid(row=0, column=2, padx=(15, 5), pady=10, sticky="w")
        entry_sotc = ctk.CTkEntry(input_frame_mh, width=80, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_sotc.grid(row=0, column=3, padx=5, pady=10, sticky="w"); self.subject_entries['sotc'] = entry_sotc
        
        # Button Frame
        button_frame_mh = ctk.CTkFrame(input_frame_mh, fg_color="transparent")
        button_frame_mh.grid(row=2, column=0, columnspan=4, pady=(15, 10)); button_frame_mh.columnconfigure((0, 1, 2, 3), weight=1)
        button_font = ctk.CTkFont(weight="bold"); button_fg_color = NEW_YELLOW; button_hover_color = BUTTON_HOVER_YELLOW; button_text_color = COLOR_WHITE
        ctk.CTkButton(button_frame_mh, text="Thêm MH", command=self.handle_add_subject, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame_mh, text="Xóa MH", command=self.handle_delete_subject, font=button_font, fg_color="#D32F2F", hover_color="#B71C1C", text_color=COLOR_WHITE).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame_mh, text="Sửa MH", command=self.handle_update_subject, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(button_frame_mh, text="Làm Mới MH", command=self.handle_refresh_subjects, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=3, padx=10, pady=5)
        
        # Search Frame
        search_frame_mh = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        search_frame_mh.grid(row=1, column=0, padx=10, pady=5, sticky="new"); search_frame_mh.columnconfigure(1, weight=1)
        ctk.CTkLabel(search_frame_mh, text="Tìm Mã Môn Học:", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_mamh = ctk.CTkEntry(search_frame_mh, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color, placeholder_text="Nhập mã môn học...")
        entry_search_mamh.grid(row=0, column=1, padx=5, pady=10, sticky="ew"); self.subject_entries['search_mamh'] = entry_search_mamh
        ctk.CTkButton(search_frame_mh, text="Tìm MH", command=self.handle_search_subject, width=80, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=2, padx=15, pady=10)
        
        # Treeview Frame
        tree_frame_mh = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        tree_frame_mh.grid(row=2, column=0, padx=10, pady=10, sticky="nsew"); tree_frame_mh.rowconfigure(0, weight=1); tree_frame_mh.columnconfigure(0, weight=1)
        self._setup_subject_treeview(tree_frame_mh)
        self.load_subjects()

    def _setup_subject_treeview(self, parent_frame):
        style = ttk.Style(); style.theme_use("clam")
        bg_color = COLOR_WHITE; text_color = "black"; header_bg = ctk.ThemeManager.theme["CTkButton"]["fg_color"][0]; header_fg = COLOR_WHITE; selected_bg = NEW_YELLOW; selected_fg = NEW_DARK_BLUE
        
        style.configure("Subject.Treeview", background=bg_color, fieldbackground=bg_color, foreground=text_color, rowheight=28, relief="flat", font=("Segoe UI", 11))
        style.configure("Subject.Treeview.Heading", background=header_bg, foreground=header_fg, font=("Segoe UI", 11, "bold"), relief="flat", padding=(10, 5))
        
        style.map("Subject.Treeview.Heading", background=[('active', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        style.map("Subject.Treeview", background=[('selected', selected_bg)], foreground=[('selected', selected_fg)])
        
        columns_mh = ("MAMH", "TENMH", "SOTC")
        self.tree_mh = ttk.Treeview(parent_frame, columns=columns_mh, show='headings', style="Subject.Treeview")
        self.tree_mh.column('#0', width=0, stretch=False)
        self.tree_mh.heading("MAMH", text="Mã Môn Học", anchor='w'); self.tree_mh.column("MAMH", width=150, anchor=tk.W, stretch=False)
        self.tree_mh.heading("TENMH", text="Tên Môn Học", anchor='w'); self.tree_mh.column("TENMH", width=400, anchor=tk.W)
        self.tree_mh.heading("SOTC", text="Số Tín Chỉ", anchor='center'); self.tree_mh.column("SOTC", width=100, anchor=tk.CENTER, stretch=False)
        
        scrollbar_y_mh = ctk.CTkScrollbar(parent_frame, command=self.tree_mh.yview); scrollbar_x_mh = ctk.CTkScrollbar(parent_frame, command=self.tree_mh.xview, orientation="horizontal")
        
        self.tree_mh.configure(yscrollcommand=scrollbar_y_mh.set, xscrollcommand=scrollbar_x_mh.set)
        self.tree_mh.grid(row=0, column=0, sticky='nsew', padx=(5,0), pady=(5,0)); scrollbar_y_mh.grid(row=0, column=1, sticky='ns', padx=(0,5), pady=5); scrollbar_x_mh.grid(row=1, column=0, sticky='ew', padx=5, pady=(0,5))
        parent_frame.rowconfigure(0, weight=1); parent_frame.columnconfigure(0, weight=1)
        self.tree_mh.bind("<<TreeviewSelect>>", self._on_subject_select)

    def _populate_subject_treeview(self, subjects_list):
        if hasattr(self, 'tree_mh'):
            for item in self.tree_mh.get_children(): self.tree_mh.delete(item)
            for subject_row in subjects_list:
                if len(subject_row) >= 3: display_values = (subject_row[0], subject_row[1], subject_row[2]); self.tree_mh.insert("", tk.END, values=display_values)

    def load_subjects(self):
        columns, subjects = self.db_manager.fetch_all_subjects()
        self._populate_subject_treeview(subjects)

    def _clear_subject_entries(self):
        if hasattr(self, 'subject_entries'):
            for key, entry_widget in self.subject_entries.items():
                if isinstance(entry_widget, ctk.CTkEntry):
                    if key == 'mamh':
                        if entry_widget.cget('state') == 'disabled': entry_widget.configure(state='normal')
                    if key != 'search_mamh': # Không xóa ô tìm kiếm khi clear form
                         entry_widget.delete(0, 'end')
            if 'mamh' in self.subject_entries: self.subject_entries['mamh'].focus()

    def _get_and_validate_subject_data(self):
        if not hasattr(self, 'subject_entries'): messagebox.showerror("Lỗi Giao Diện", "Chưa khởi tạo các ô nhập liệu môn học."); return None
        
        try: mamh_raw = self.subject_entries['mamh'].get().strip(); ten_mh = self.subject_entries['tenmh'].get().strip(); sotc_str = self.subject_entries['sotc'].get().strip(); khoa = 'CNTT'
        except KeyError as e: messagebox.showerror("Lỗi Cấu Hình", f"Lỗi truy cập ô nhập liệu môn học '{e}'."); return None
        
        if not mamh_raw: messagebox.showwarning("Thiếu thông tin", "Mã môn học (MAMH) không được để trống."); return None
        mamh = mamh_raw.lower()
        
        if not re.match(r'^[a-z]{3}\d{3}$', mamh): messagebox.showwarning("Lỗi Dữ Liệu", "Định dạng Mã Môn Học không hợp lệ (Yêu cầu: 3 chữ thường và 3 số, ví dụ: 'abc123')."); return None
        
        if not ten_mh: messagebox.showwarning("Thiếu thông tin", "Tên môn học không được để trống."); return None
        
        if not sotc_str: messagebox.showwarning("Thiếu thông tin", "Số tín chỉ không được để trống."); return None
        
        try:
            sotinchi = int(sotc_str)
            if not (1 <= sotinchi <= 10): messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải là số nguyên từ 1 đến 10."); return None
        except ValueError: messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải là một con số (số nguyên)."); return None
        
        return (mamh, ten_mh, sotinchi, khoa)

    def _on_subject_select(self, event):
        
        if not hasattr(self, 'tree_mh') or not hasattr(self, 'subject_entries'): return
        selected_item = self.tree_mh.selection()
        
        if not selected_item: return
        values = self.tree_mh.item(selected_item[0], 'values')
        
        try:
            self._clear_subject_entries() # Xóa và bật lại MAMH
            mamh = values[0]; ten_mh = values[1]; sotc = values[2]
            self.subject_entries['mamh'].insert(0, mamh); self.subject_entries['tenmh'].insert(0, ten_mh); self.subject_entries['sotc'].insert(0, sotc)
            self.subject_entries['mamh'].configure(state='disabled') # Vô hiệu hóa MAMH
        except (IndexError, KeyError, tk.TclError) as e: messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải thông tin môn học lên form. Lỗi: {e}")

    def handle_add_subject(self):
        if self.subject_entries['mamh'].cget('state') == 'disabled': messagebox.showwarning("Trạng thái không hợp lệ", "Đang chọn môn học để sửa. Nhấn 'Làm Mới MH' trước khi thêm."); return
        data = self._get_and_validate_subject_data()
        
        if data is None: return
        mamh, ten_mh, sotinchi, khoa = data
        
        if self.db_manager.add_subject(mamh, ten_mh, sotinchi, khoa): messagebox.showinfo("Thành công", f"Đã thêm môn học '{ten_mh}' ({mamh})."); self.handle_refresh_subjects()

    def handle_delete_subject(self):
        if not hasattr(self, 'tree_mh'): return
        selected_item = self.tree_mh.selection()
        
        if not selected_item: messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một môn học trong danh sách để xóa."); return
        values = self.tree_mh.item(selected_item[0], 'values')
        
        try: mamh_to_delete = values[0]; ten_mh_to_delete = values[1]
        except IndexError: messagebox.showerror("Lỗi", "Không thể lấy thông tin môn học để xóa."); return
        
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa môn học '{ten_mh_to_delete}' ({mamh_to_delete})?"):
            if self.db_manager.delete_subject(mamh_to_delete): messagebox.showinfo("Thành công", f"Đã xóa môn học '{ten_mh_to_delete}'."); self.handle_refresh_subjects()

    def handle_update_subject(self):
        if self.subject_entries['mamh'].cget('state') == 'normal': messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một môn học từ danh sách trước khi sửa."); return
        data = self._get_and_validate_subject_data()
        
        if data is None: return
        mamh = self.subject_entries['mamh'].get().strip().lower()
        _, ten_mh, sotinchi, khoa = data
        
        if not mamh: messagebox.showwarning("Lỗi", "Không xác định được Mã Môn Học cần sửa."); return
        
        if self.db_manager.update_subject(mamh, ten_mh, sotinchi, khoa): messagebox.showinfo("Thành công", f"Đã cập nhật môn học '{ten_mh}' ({mamh})."); self.handle_refresh_subjects()

    def handle_refresh_subjects(self):
        
        self._clear_subject_entries()
        
        if hasattr(self, 'subject_entries') and 'search_mamh' in self.subject_entries: self.subject_entries['search_mamh'].delete(0, 'end')
        self.load_subjects()

    def handle_search_subject(self):
        if not hasattr(self, 'subject_entries') or 'search_mamh' not in self.subject_entries: messagebox.showerror("Lỗi Giao Diện", "Chưa khởi tạo ô tìm kiếm môn học."); return
        
        try:
            search_keyword = self.subject_entries['search_mamh'].get().strip()
            columns, subjects = self.db_manager.find_subject(search_keyword)
            self._populate_subject_treeview(subjects)
            if not subjects and search_keyword: messagebox.showinfo("Tìm kiếm", f"Không tìm thấy môn học nào khớp với '{search_keyword}'.")
        except Exception as e: messagebox.showerror("Lỗi Tìm Kiếm", f"Có lỗi xảy ra khi tìm kiếm môn học:\n{e}"); self._populate_subject_treeview([])

    def _setup_layout_hocphan(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0); parent.rowconfigure(1, weight=0); parent.rowconfigure(2, weight=1)
        frame_fg_color = NEW_DARK_BLUE
        input_frame_hp = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        input_frame_hp.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self.hocphan_entries = {}
        self._setup_hp_input_fields(input_frame_hp) # Gọi hàm tạo widget
        search_frame_hp = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        search_frame_hp.grid(row=1, column=0, padx=10, pady=5, sticky="new")
        self._setup_hp_search_bar(search_frame_hp) # Gọi hàm tạo thanh tìm kiếm
        tree_frame_hp = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        tree_frame_hp.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tree_frame_hp.rowconfigure(0, weight=1); tree_frame_hp.columnconfigure(0, weight=1)
        self._setup_hp_treeview(tree_frame_hp)
        self.load_hocphan()

    def _setup_hp_input_fields(self, input_frame_hp):
        input_frame_hp.columnconfigure((0, 2), weight=0); input_frame_hp.columnconfigure((1, 3), weight=1)
        label_font = ctk.CTkFont(weight="bold"); label_text_color = NEW_LIGHT_GREY
        entry_border_color = NEW_YELLOW; entry_fg_color = COLOR_WHITE; entry_text_color = NEW_DARK_BLUE
        # MaHP
        ctk.CTkLabel(input_frame_hp, text="Mã Học Phần (MAHP)", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_mahp = ctk.CTkEntry(input_frame_hp, width=120, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_mahp.grid(row=0, column=1, padx=5, pady=10, sticky="w"); self.hocphan_entries['mahp'] = entry_mahp
        # MaMH ComboBox
        ctk.CTkLabel(input_frame_hp, text="Mã Môn Học (MAMH)", font=label_font, text_color=label_text_color).grid(row=0, column=2, padx=(15, 5), pady=10, sticky="w")
        entry_mamh_hp = ctk.CTkComboBox(input_frame_hp, width=150, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color, dropdown_fg_color=entry_fg_color, button_color=NEW_YELLOW, dropdown_hover_color=BUTTON_HOVER_YELLOW, state='readonly')
        entry_mamh_hp.grid(row=0, column=3, padx=5, pady=10, sticky="w"); self.hocphan_entries['mamh_hp'] = entry_mamh_hp; self._populate_mamh_combobox()
        # HocKy
        ctk.CTkLabel(input_frame_hp, text="Học Kỳ", font=label_font, text_color=label_text_color).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_hocky = ctk.CTkEntry(input_frame_hp, width=80, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_hocky.grid(row=1, column=1, padx=5, pady=10, sticky="w"); self.hocphan_entries['hocky'] = entry_hocky
        # NamHoc
        ctk.CTkLabel(input_frame_hp, text="Năm Học", font=label_font, text_color=label_text_color).grid(row=1, column=2, padx=(15, 5), pady=10, sticky="w")
        entry_namhoc = ctk.CTkEntry(input_frame_hp, width=150, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color, placeholder_text="vd: 2024-2025")
        entry_namhoc.grid(row=1, column=3, padx=5, pady=10, sticky="w"); self.hocphan_entries['namhoc'] = entry_namhoc
        # GiangVien
        ctk.CTkLabel(input_frame_hp, text="Giảng Viên", font=label_font, text_color=label_text_color).grid(row=2, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_gv = ctk.CTkEntry(input_frame_hp, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color)
        entry_gv.grid(row=2, column=1, columnspan=3, padx=5, pady=10, sticky="ew"); self.hocphan_entries['gv'] = entry_gv
        # Button Frame
        button_frame_hp = ctk.CTkFrame(input_frame_hp, fg_color="transparent")
        button_frame_hp.grid(row=3, column=0, columnspan=4, pady=(15, 10)); button_frame_hp.columnconfigure((0, 1, 2, 3), weight=1)
        button_font = ctk.CTkFont(weight="bold"); button_fg_color = NEW_YELLOW; button_hover_color = BUTTON_HOVER_YELLOW; button_text_color = COLOR_WHITE
        ctk.CTkButton(button_frame_hp, text="Thêm HP", command=self.handle_add_hp, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame_hp, text="Xóa HP", command=self.handle_delete_hp, font=button_font, fg_color="#D32F2F", hover_color="#B71C1C", text_color=COLOR_WHITE).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame_hp, text="Sửa HP", command=self.handle_update_hp, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(button_frame_hp, text="Làm Mới HP", command=self.handle_refresh_hp, font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color).grid(row=0, column=3, padx=10, pady=5)

    def _setup_hp_search_bar(self, search_frame_hp):
        """Thiết lập thanh tìm kiếm cho tab Học phần."""
        search_frame_hp.columnconfigure(1, weight=1)
        label_font = ctk.CTkFont(weight="bold"); label_text_color = NEW_LIGHT_GREY
        entry_border_color = NEW_YELLOW; entry_fg_color = COLOR_WHITE; entry_text_color = NEW_DARK_BLUE
        button_font = ctk.CTkFont(weight="bold"); button_fg_color = NEW_YELLOW; button_hover_color = BUTTON_HOVER_YELLOW; button_text_color = COLOR_WHITE

        ctk.CTkLabel(search_frame_hp, text="Tìm HP (MãHP/MãMH/TênMH/GV):", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_hp = ctk.CTkEntry(search_frame_hp, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color, placeholder_text="Nhập từ khóa...")
        entry_search_hp.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.hocphan_entries['search_hp'] = entry_search_hp # Lưu ô tìm kiếm

        ctk.CTkButton(search_frame_hp, text="Tìm HP", command=self.handle_search_hp, width=80,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=0, column=2, padx=15, pady=10)

    def _setup_hp_treeview(self, parent_frame):
        style = ttk.Style(); style.theme_use("clam")
        bg_color = COLOR_WHITE; text_color = "black"; header_bg = ctk.ThemeManager.theme["CTkButton"]["fg_color"][0]; header_fg = COLOR_WHITE; selected_bg = NEW_YELLOW; selected_fg = NEW_DARK_BLUE
        style.configure("HocPhan.Treeview", background=bg_color, fieldbackground=bg_color, foreground=text_color, rowheight=28, relief="flat", font=("Segoe UI", 11))
        style.configure("HocPhan.Treeview.Heading", background=header_bg, foreground=header_fg, font=("Segoe UI", 11, "bold"), relief="flat", padding=(10, 5))
        style.map("HocPhan.Treeview.Heading", background=[('active', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        style.map("HocPhan.Treeview", background=[('selected', selected_bg)], foreground=[('selected', selected_fg)])
        columns_hp = ("MAHP", "MAMH", "TENMH", "HOCKY", "NAMHOC", "GV")
        self.tree_hp = ttk.Treeview(parent_frame, columns=columns_hp, show='headings', style="HocPhan.Treeview")
        self.tree_hp.column('#0', width=0, stretch=False)
        self.tree_hp.heading("MAHP", text="Mã HP", anchor='center'); self.tree_hp.column("MAHP", width=80, anchor=tk.CENTER, stretch=False)
        self.tree_hp.heading("MAMH", text="Mã MH", anchor='w'); self.tree_hp.column("MAMH", width=100, anchor=tk.W, stretch=False)
        self.tree_hp.heading("TENMH", text="Tên Môn Học", anchor='w'); self.tree_hp.column("TENMH", width=250, anchor=tk.W)
        self.tree_hp.heading("HOCKY", text="Học Kỳ", anchor='center'); self.tree_hp.column("HOCKY", width=80, anchor=tk.CENTER, stretch=False)
        self.tree_hp.heading("NAMHOC", text="Năm Học", anchor='w'); self.tree_hp.column("NAMHOC", width=120, anchor=tk.W, stretch=False)
        self.tree_hp.heading("GV", text="Giảng Viên", anchor='w'); self.tree_hp.column("GV", width=200, anchor=tk.W)
        scrollbar_y_hp = ctk.CTkScrollbar(parent_frame, command=self.tree_hp.yview); scrollbar_x_hp = ctk.CTkScrollbar(parent_frame, command=self.tree_hp.xview, orientation="horizontal")
        self.tree_hp.configure(yscrollcommand=scrollbar_y_hp.set, xscrollcommand=scrollbar_x_hp.set)
        self.tree_hp.grid(row=0, column=0, sticky='nsew', padx=(5,0), pady=(5,0)); scrollbar_y_hp.grid(row=0, column=1, sticky='ns', padx=(0,5), pady=5); scrollbar_x_hp.grid(row=1, column=0, sticky='ew', padx=5, pady=(0,5))
        parent_frame.rowconfigure(0, weight=1); parent_frame.columnconfigure(0, weight=1)
        self.tree_hp.bind("<<TreeviewSelect>>", self._on_hp_select)

    def _populate_mamh_combobox(self):
        if hasattr(self, 'hocphan_entries') and 'mamh_hp' in self.hocphan_entries:
            try:
                _, subjects = self.db_manager.fetch_all_subjects()
                mamh_list = sorted([subject[0] for subject in subjects])
                self.hocphan_entries['mamh_hp'].configure(values=mamh_list)
                # Xóa giá trị hiện tại để người dùng phải chọn lại sau khi refresh
                self.hocphan_entries['mamh_hp'].set("")
            except Exception as e:
                messagebox.showerror("Lỗi Tải Môn Học", f"Không thể tải danh sách Mã Môn Học: {e}")
                self.hocphan_entries['mamh_hp'].configure(values=[])
                self.hocphan_entries['mamh_hp'].set("")

    def _populate_hp_treeview(self, hocphan_list):
        if hasattr(self, 'tree_hp'):
            for item in self.tree_hp.get_children(): self.tree_hp.delete(item)
            for hp_row in hocphan_list:
                if len(hp_row) >= 6: display_values = (hp_row[0], hp_row[1], hp_row[2], hp_row[3], hp_row[4], hp_row[5]); self.tree_hp.insert("", tk.END, values=display_values)

    def load_hocphan(self):
        columns, hocphans = self.db_manager.fetch_all_hocphan()
        self._populate_hp_treeview(hocphans)

    def _clear_hp_entries(self):
        if hasattr(self, 'hocphan_entries'):
            for key, entry_widget in self.hocphan_entries.items():
                if isinstance(entry_widget, ctk.CTkEntry):
                    if key == 'mahp':
                        if entry_widget.cget('state') == 'disabled': entry_widget.configure(state='normal')
                    if key != 'search_hp': entry_widget.delete(0, 'end')
                elif isinstance(entry_widget, ctk.CTkComboBox): entry_widget.set("")
            if 'mahp' in self.hocphan_entries: self.hocphan_entries['mahp'].focus()

    def _get_and_validate_hp_data(self):
        if not hasattr(self, 'hocphan_entries'): return None
        try: mahp_str = self.hocphan_entries['mahp'].get().strip(); mamh = self.hocphan_entries['mamh_hp'].get().strip(); hocky_str = self.hocphan_entries['hocky'].get().strip(); namhoc = self.hocphan_entries['namhoc'].get().strip(); gv = self.hocphan_entries['gv'].get().strip()
        except KeyError as e: messagebox.showerror("Lỗi", f"Lỗi truy cập ô nhập '{e}'."); return None
        if not mahp_str: messagebox.showwarning("Thiếu", "Mã Học Phần không được trống."); return None
        try: mahp = int(mahp_str); assert mahp > 0
        except (ValueError, AssertionError): messagebox.showwarning("Lỗi", "Mã Học Phần phải là số nguyên dương."); return None
        if not mamh: messagebox.showwarning("Thiếu", "Vui lòng chọn Mã Môn Học."); return None
        if not hocky_str: messagebox.showwarning("Thiếu", "Học Kỳ không được trống."); return None
        try: hocky = int(hocky_str)
        except ValueError: messagebox.showwarning("Lỗi", "Học Kỳ phải là số."); return None
        if not namhoc: messagebox.showwarning("Thiếu", "Năm Học không được trống."); return None
        return (mahp, mamh, hocky, namhoc, gv)

    def _on_hp_select(self, event):
        if not hasattr(self, 'tree_hp') or not hasattr(self, 'hocphan_entries'): return
        selected = self.tree_hp.selection()
        if not selected: return
        values = self.tree_hp.item(selected[0], 'values')
        try:
            self._clear_hp_entries()
            mahp, mamh, tenmh, hocky, namhoc, gv = values
            self.hocphan_entries['mahp'].insert(0, mahp); self.hocphan_entries['mamh_hp'].set(mamh); self.hocphan_entries['hocky'].insert(0, hocky); self.hocphan_entries['namhoc'].insert(0, namhoc); self.hocphan_entries['gv'].insert(0, gv)
            self.hocphan_entries['mahp'].configure(state='disabled')
        except (IndexError, ValueError, KeyError, tk.TclError) as e: messagebox.showerror("Lỗi", f"Không tải được dữ liệu HP: {e}")

    def handle_add_hp(self):
        if self.hocphan_entries['mahp'].cget('state') == 'disabled': messagebox.showwarning("Lỗi", "Đang chọn sửa, nhấn 'Làm Mới HP' trước."); return
        data = self._get_and_validate_hp_data()
        if data is None: return
        mahp, mamh, hocky, namhoc, gv = data
        if self.db_manager.add_hocphan(mahp, mamh, hocky, namhoc, gv): messagebox.showinfo("OK", f"Thêm HP {mahp} thành công."); self.handle_refresh_hp()

    def handle_delete_hp(self):
        if not hasattr(self, 'tree_hp'): return
        selected = self.tree_hp.selection()
        if not selected: messagebox.showwarning("Lỗi", "Chọn HP cần xóa."); return
        values = self.tree_hp.item(selected[0], 'values')
        try: mahp = values[0]; tenmh = values[2] if len(values) > 2 else f"(Mã MH: {values[1]})"
        except IndexError: messagebox.showerror("Lỗi", "Không lấy được thông tin HP."); return
        if messagebox.askyesno("Xóa?", f"Xóa học phần '{tenmh}' (Mã HP: {mahp})?"):
            if self.db_manager.delete_hocphan(mahp): messagebox.showinfo("OK", f"Xóa HP {mahp} thành công."); self.handle_refresh_hp()

    def handle_update_hp(self):
        if self.hocphan_entries['mahp'].cget('state') == 'normal': messagebox.showwarning("Lỗi", "Chọn HP cần sửa từ danh sách."); return
        data = self._get_and_validate_hp_data()
        if data is None: return
        try: mahp_goc = int(self.hocphan_entries['mahp'].get())
        except ValueError: messagebox.showerror("Lỗi", "Mã Học Phần trên form không hợp lệ."); return
        _, mamh_moi, hocky_moi, namhoc_moi, gv_moi = data
        if self.db_manager.update_hocphan(mahp_goc, mamh_moi, hocky_moi, namhoc_moi, gv_moi): messagebox.showinfo("OK", f"Cập nhật HP {mahp_goc} thành công."); self.handle_refresh_hp()

    def handle_refresh_hp(self):
        self._clear_hp_entries()
        if hasattr(self, 'hocphan_entries') and 'search_hp' in self.hocphan_entries: self.hocphan_entries['search_hp'].delete(0, 'end')
        self.load_hocphan()
        self._populate_mamh_combobox() # Tải lại danh sách môn học

    def handle_search_hp(self):
        if not hasattr(self, 'hocphan_entries') or 'search_hp' not in self.hocphan_entries: messagebox.showerror("Lỗi", "Chưa có ô tìm kiếm học phần."); return
        try:
            search_keyword = self.hocphan_entries['search_hp'].get().strip()
            columns, hocphans = self.db_manager.find_hocphan(search_keyword)
            self._populate_hp_treeview(hocphans)
            if not hocphans and search_keyword: messagebox.showinfo("Tìm kiếm", f"Không tìm thấy học phần nào khớp với '{search_keyword}'.")
        except Exception as e: messagebox.showerror("Lỗi Tìm Kiếm", f"Lỗi khi tìm học phần: {e}"); self._populate_hp_treeview([])

    def _setup_layout_bangdiem(self, parent):
        parent.columnconfigure(0, weight=1)
        
        # === THAY ĐỔI CẤU HÌNH HÀNG ===
        parent.rowconfigure(0, weight=0) # Frame Tìm kiếm
        parent.rowconfigure(1, weight=0) # Frame Cập nhật (weight=0)
        parent.rowconfigure(2, weight=1) # Frame Treeview (weight=1, để co giãn)

        frame_fg_color = NEW_DARK_BLUE
        label_font = ctk.CTkFont(weight="bold"); label_text_color = NEW_LIGHT_GREY
        entry_border_color = NEW_YELLOW; entry_fg_color = COLOR_WHITE; entry_text_color = NEW_DARK_BLUE
        button_font = ctk.CTkFont(weight="bold"); button_fg_color = NEW_YELLOW; button_hover_color = BUTTON_HOVER_YELLOW; button_text_color = COLOR_WHITE

        # --- 1. Frame Tìm Kiếm (Luôn hiển thị) ---
        frame_top_diem = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        frame_top_diem.grid(row=0, column=0, padx=10, pady=10, sticky="new") # Vẫn ở row=0
        frame_top_diem.columnconfigure(1, weight=1)
        
        self.diem_entries = {}
        self.hocphan_data_diem = {}

        ctk.CTkLabel(frame_top_diem, text="Tìm Mã Sinh Viên:", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_masv_diem = ctk.CTkEntry(frame_top_diem, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color, placeholder_text="Nhập MASV (ví dụ: A123)")
        entry_search_masv_diem.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.diem_entries['search_masv'] = entry_search_masv_diem

        ctk.CTkButton(frame_top_diem, text="Tìm SV", command=self.handle_search_student_grades, width=80,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkButton(frame_top_diem, text="Làm Mới", command=self.handle_refresh_grades, width=80,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=0, column=3, padx=(0, 15), pady=10)
        
        # --- 2. Frame Cập Nhật & Thông Tin (Ẩn ban đầu) ---
        # === THAY ĐỔI: Chuyển lên row=1 ===
        self.frame_edit_diem = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        self.frame_edit_diem.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="new")
        self.frame_edit_diem.columnconfigure((1, 3, 5), weight=1)

        self.diem_info_labels = {} 

        # Hàng 1: Thông tin SV
        ctk.CTkLabel(self.frame_edit_diem, text="MSSV:", font=label_font, text_color=label_text_color).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        lbl_masv = ctk.CTkLabel(self.frame_edit_diem, text="...", font=label_font, text_color=COLOR_WHITE)
        lbl_masv.grid(row=0, column=1, padx=5, pady=8, sticky="w"); self.diem_info_labels['masv'] = lbl_masv

        ctk.CTkLabel(self.frame_edit_diem, text="Họ Tên:", font=label_font, text_color=label_text_color).grid(row=0, column=2, padx=(15, 5), pady=8, sticky="w")
        lbl_ten = ctk.CTkLabel(self.frame_edit_diem, text="...", font=label_font, text_color=COLOR_WHITE)
        lbl_ten.grid(row=0, column=3, padx=5, pady=8, sticky="w"); self.diem_info_labels['ten'] = lbl_ten
        
        # Hàng 2: Thông tin Điểm TB và Xếp Loại
        ctk.CTkLabel(self.frame_edit_diem, text="Điểm TB:", font=label_font, text_color=label_text_color).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        lbl_dtb = ctk.CTkLabel(self.frame_edit_diem, text="...", font=label_font, text_color=NEW_YELLOW)
        lbl_dtb.grid(row=1, column=1, padx=5, pady=8, sticky="w"); self.diem_info_labels['dtb'] = lbl_dtb

        ctk.CTkLabel(self.frame_edit_diem, text="Xếp Loại:", font=label_font, text_color=label_text_color).grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")
        lbl_xeploai = ctk.CTkLabel(self.frame_edit_diem, text="...", font=label_font, text_color=NEW_YELLOW)
        lbl_xeploai.grid(row=1, column=3, padx=5, pady=8, sticky="w"); self.diem_info_labels['xeploai'] = lbl_xeploai

        # Hàng 3: Chọn Học Phần (DÙNG COMBOBOX)
        ctk.CTkLabel(self.frame_edit_diem, text="Chọn Học Phần:", font=label_font, text_color=label_text_color).grid(row=2, column=0, padx=(15, 5), pady=10, sticky="w")
        combo_mahp_diem = ctk.CTkComboBox(self.frame_edit_diem, width=400, border_color=entry_border_color, 
                                          fg_color=entry_fg_color, text_color=entry_text_color, 
                                          dropdown_fg_color=entry_fg_color, button_color=NEW_YELLOW, 
                                          dropdown_hover_color=BUTTON_HOVER_YELLOW, state='readonly',
                                          values=[])
        combo_mahp_diem.grid(row=2, column=1, columnspan=3, padx=5, pady=10, sticky="ew")
        self.diem_entries['mahp_combo'] = combo_mahp_diem
        self._populate_hp_combobox_diem() 

        # Hàng 4: Nhập điểm và nút Cập nhật
        ctk.CTkLabel(self.frame_edit_diem, text="Điểm Mới:", font=label_font, text_color=label_text_color).grid(row=3, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_diem = ctk.CTkEntry(self.frame_edit_diem, width=100, border_color=entry_border_color, fg_color=entry_fg_color, text_color=entry_text_color, placeholder_text="0-10")
        entry_diem.grid(row=3, column=1, padx=5, pady=10, sticky="w"); self.diem_entries['diem'] = entry_diem

        ctk.CTkButton(self.frame_edit_diem, text="Cập Nhật Điểm", command=self.handle_update_grade,
                      font=button_font, fg_color=button_fg_color, hover_color=button_hover_color, text_color=button_text_color
                      ).grid(row=3, column=2, padx=15, pady=10, sticky="w")


        # --- 3. Frame Treeview (Ẩn ban đầu) ---
        # === THAY ĐỔI: Chuyển xuống row=2 ===
        self.frame_tree_diem = ctk.CTkFrame(parent, fg_color=frame_fg_color, corner_radius=10)
        self.frame_tree_diem.grid(row=2, column=0, padx=10, pady=10, sticky="nsew") # Chuyển sang row=2
        self.frame_tree_diem.rowconfigure(0, weight=1); self.frame_tree_diem.columnconfigure(0, weight=1)
        self._setup_diem_treeview(self.frame_tree_diem)

        # Ẩn các frame ban đầu
        self.frame_tree_diem.grid_remove()
        self.frame_edit_diem.grid_remove()

    def _setup_diem_treeview(self, parent_frame):
        """Khởi tạo Treeview cho tab Bảng Điểm."""
        style = ttk.Style(); style.theme_use("clam")
        bg_color = COLOR_WHITE; text_color = "black"; header_bg = ctk.ThemeManager.theme["CTkButton"]["fg_color"][0]; header_fg = COLOR_WHITE; selected_bg = NEW_YELLOW; selected_fg = NEW_DARK_BLUE
        
        style.configure("Diem.Treeview", background=bg_color, fieldbackground=bg_color, foreground=text_color, rowheight=28, relief="flat", font=("Segoe UI", 11))
        style.configure("Diem.Treeview.Heading", background=header_bg, foreground=header_fg, font=("Segoe UI", 11, "bold"), relief="flat", padding=(10, 5))
        
        style.map("Diem.Treeview.Heading", background=[('active', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        style.map("Diem.Treeview", background=[('selected', selected_bg)], foreground=[('selected', selected_fg)])
        
        # Giữ nguyên các cột
        columns_diem = ("MAHP", "TENMH", "SOTC", "DIEM")
        self.tree_diem = ttk.Treeview(parent_frame, columns=columns_diem, show='headings', style="Diem.Treeview")
        self.tree_diem.column('#0', width=0, stretch=False)
        self.tree_diem.heading("MAHP", text="Mã Học Phần", anchor='center'); self.tree_diem.column("MAHP", width=120, anchor=tk.CENTER, stretch=False)
        self.tree_diem.heading("TENMH", text="Tên Môn Học", anchor='w'); self.tree_diem.column("TENMH", width=400, anchor=tk.W)
        self.tree_diem.heading("SOTC", text="Số Tín Chỉ", anchor='center'); self.tree_diem.column("SOTC", width=100, anchor=tk.CENTER, stretch=False)
        self.tree_diem.heading("DIEM", text="Điểm (Hệ 10)", anchor='center'); self.tree_diem.column("DIEM", width=120, anchor=tk.CENTER, stretch=False)
        
        scrollbar_y_diem = ctk.CTkScrollbar(parent_frame, command=self.tree_diem.yview)
        scrollbar_x_diem = ctk.CTkScrollbar(parent_frame, command=self.tree_diem.xview, orientation="horizontal")
        
        self.tree_diem.configure(yscrollcommand=scrollbar_y_diem.set, xscrollcommand=scrollbar_x_diem.set)
        self.tree_diem.grid(row=0, column=0, sticky='nsew', padx=(5,0), pady=(5,0)); scrollbar_y_diem.grid(row=0, column=1, sticky='ns', padx=(0,5), pady=5); scrollbar_x_diem.grid(row=1, column=0, sticky='ew', padx=5, pady=(0,5))
        parent_frame.rowconfigure(0, weight=1); parent_frame.columnconfigure(0, weight=1)
        
        self.tree_diem.bind("<<TreeviewSelect>>", self._on_diem_select)
    
    def _populate_hp_combobox_diem(self):
        """(HÀM MỚI) Tải danh sách học phần vào ComboBox của tab Bảng điểm."""
        if not hasattr(self, 'hocphan_data_diem'):
            self.hocphan_data_diem = {}
            
        self.hocphan_data_diem.clear()
        
        try:
            _, hocphans = self.db_manager.fetch_all_hocphan()
            # hocphans = (MAHP, MAMH, TENMH, HOCKY, NAMHOC, GV)
            
            display_list = []
            for hp in hocphans:
                mahp = hp[0]
                ten_mh = hp[2]
                hocky = hp[3]
                namhoc = hp[4]
                # Tạo chuỗi hiển thị
                display_string = f"{mahp} - {ten_mh} (HK{hocky}, {namhoc})"
                
                # Lưu vào map
                self.hocphan_data_diem[display_string] = mahp
                display_list.append(display_string)

            self.diem_entries['mahp_combo'].configure(values=display_list)
            self.diem_entries['mahp_combo'].set("")
            
        except Exception as e:
            messagebox.showerror("Lỗi Tải Học Phần", f"Không thể tải danh sách Học Phần cho ComboBox: {e}")
            self.diem_entries['mahp_combo'].configure(values=[])
            self.diem_entries['mahp_combo'].set("")

    def _populate_diem_treeview(self, grades_list):
        if hasattr(self, 'tree_diem'):
            for item in self.tree_diem.get_children(): self.tree_diem.delete(item)
            for grade_row in grades_list:
                if len(grade_row) >= 4:
                    display_values = (grade_row[0], grade_row[1], grade_row[2], grade_row[3])
                    self.tree_diem.insert("", tk.END, values=display_values)

    def _calculate_xep_loai(self, gpa):
        if gpa >= 9.0: return "Xuất sắc"
        if gpa >= 8.0: return "Giỏi"
        if gpa >= 7.0: return "Khá"
        if gpa >= 5.0: return "Trung bình"
        if gpa >= 4.0: return "Yếu"
        return "Kém"

    def _clear_diem_entries(self):
        """Xóa các ô nhập liệu và thông tin sinh viên."""
        if hasattr(self, 'diem_entries'):
            # Xóa ô điểm
            if 'diem' in self.diem_entries:
                self.diem_entries['diem'].delete(0, 'end')
            # Đặt lại ComboBox
            if 'mahp_combo' in self.diem_entries:
                self.diem_entries['mahp_combo'].set("")
            
        if hasattr(self, 'diem_info_labels'):
            for key, label in self.diem_info_labels.items():
                label.configure(text="...")

    def handle_search_student_grades(self):
        """Tìm sinh viên và hiển thị bảng điểm."""
        search_masv = self.diem_entries['search_masv'].get().strip().upper()
        if not search_masv:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã Sinh Viên (MASV) để tìm.")
            return

        student_info = self.db_manager.fetch_student_info(search_masv)
        if not student_info:
            messagebox.showerror("Không tìm thấy", f"Không tìm thấy sinh viên có mã '{search_masv}'.")
            self.handle_refresh_grades()
            return
        
        student_name = student_info[0]

        # Hiển thị các frame
        self.frame_tree_diem.grid()
        self.frame_edit_diem.grid()
        
        # Tải lại danh sách HP vào combobox (phòng trường hợp có HP mới)
        self._populate_hp_combobox_diem()
        
        # Tải bảng điểm
        cols, grades = self.db_manager.fetch_grades_for_student(search_masv)
        self._populate_diem_treeview(grades)
        
        # Tính toán và hiển thị GPA
        gpa_data = self.db_manager.calculate_gpa_raw(search_masv)
        gpa_str = "N/A"
        xep_loai = "Chưa có điểm"

        if gpa_data and gpa_data[0] is not None and gpa_data[1] is not None:
            try:
                total_weighted_score = float(gpa_data[0])
                total_credits = int(gpa_data[1])
                
                if total_credits > 0:
                    gpa = total_weighted_score / total_credits
                    gpa_str = f"{gpa:.2f}"
                    xep_loai = self._calculate_xep_loai(gpa)
                else:
                    gpa_str = "0.00"
                    xep_loai = "Chưa có tín chỉ"
            except (ValueError, TypeError):
                 gpa_str = "Lỗi"; xep_loai = "Lỗi"

        # Cập nhật các Label thông tin
        self._clear_diem_entries() # Xóa các entry cũ trước
        self.diem_info_labels['masv'].configure(text=search_masv)
        self.diem_info_labels['ten'].configure(text=student_name)
        self.diem_info_labels['dtb'].configure(text=gpa_str)
        self.diem_info_labels['xeploai'].configure(text=xep_loai)

    def _on_diem_select(self, event):
        """(CẬP NHẬT) Khi click vào một dòng điểm, CẬP NHẬT ComboBox và ô Điểm."""
        selected_item = self.tree_diem.selection()
        if not selected_item:
            return
        
        values = self.tree_diem.item(selected_item[0], 'values')
        
        try:
            # Lấy dữ liệu (MAHP, TENMH, SOTC, DIEM)
            mahp_selected = values[0]
            diem_selected = values[3]
            
            # 1. Tìm chuỗi hiển thị tương ứng trong ComboBox
            target_display_string = None
            # self.hocphan_data_diem là dict { "Display String": MAHP }
            for display_str, mahp_id in self.hocphan_data_diem.items():
                # So sánh MAHP (kiểu dữ liệu có thể khác, int vs str)
                if str(mahp_id) == str(mahp_selected):
                    target_display_string = display_str
                    break
            
            # 2. Cập nhật ComboBox và ô Điểm
            if target_display_string:
                self.diem_entries['mahp_combo'].set(target_display_string)
            else:
                # Trường hợp HP này đã bị xóa khỏi bảng HOCPHAN nhưng vẫn còn trong KETQUA
                self.diem_entries['mahp_combo'].set(f"LỖI: Không tìm thấy HP {mahp_selected}")

            self.diem_entries['diem'].delete(0, 'end')
            self.diem_entries['diem'].insert(0, diem_selected)

        except (IndexError, KeyError) as e:
             messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải thông tin điểm. Lỗi: {e}")

    def handle_update_grade(self):
        """(CẬP NHẬT) Cập nhật điểm (hoặc thêm mới) cho môn học đã chọn."""
        
        # 1. Lấy MASV (từ label)
        masv = self.diem_info_labels['masv'].cget('text')
        if not masv or masv == "...":
            messagebox.showwarning("Lỗi", "Không xác định được Sinh viên. Vui lòng 'Tìm SV' trước.")
            return

        # 2. Lấy MAHP (từ ComboBox)
        selected_display_string = self.diem_entries['mahp_combo'].get()
        if not selected_display_string:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một Học Phần từ danh sách.")
            return
            
        try:
            # Lấy MAHP thật từ dictionary
            mahp = self.hocphan_data_diem[selected_display_string]
        except KeyError:
            messagebox.showerror("Lỗi", f"Học phần '{selected_display_string}' không hợp lệ hoặc không tìm thấy.")
            return

        # 3. Lấy và xác thực Điểm
        diem_str = self.diem_entries['diem'].get().strip()
        if not diem_str:
            messagebox.showwarning("Thiếu điểm", "Vui lòng nhập điểm mới (từ 0 đến 10).")
            return
            
        try:
            diem = float(diem_str)
            if not (0 <= diem <= 10):
                raise ValueError("Điểm ngoài phạm vi")
        except ValueError:
            messagebox.showwarning("Lỗi Dữ Liệu", "Điểm phải là một số hợp lệ từ 0 đến 10.")
            return

        # 4. Thực hiện cập nhật DB (MERGE sẽ lo INSERT hoặc UPDATE)
        if self.db_manager.add_or_update_grade(masv, mahp, diem):
            messagebox.showinfo("Thành công", f"Đã cập nhật/thêm điểm cho HP {mahp} của SV {masv} thành {diem}.")
            # Tự động tìm kiếm lại để làm mới Treeview và GPA
            self.handle_search_student_grades()
        else:
            pass # Lỗi đã được báo bởi db_manager

    def handle_refresh_grades(self):
        """Làm mới tab Bảng điểm, ẩn các frame và xóa dữ liệu."""
        if hasattr(self, 'diem_entries') and 'search_masv' in self.diem_entries:
            self.diem_entries['search_masv'].delete(0, 'end')
            
        self._clear_diem_entries()
        
        if hasattr(self, 'tree_diem'):
            for item in self.tree_diem.get_children():
                self.tree_diem.delete(item)
                
        if hasattr(self, 'frame_tree_diem'):
            self.frame_tree_diem.grid_remove()
        if hasattr(self, 'frame_edit_diem'):
            self.frame_edit_diem.grid_remove()
            
        # Tải lại danh sách HP mới nhất vào combobox (khi bị ẩn)
        self._populate_hp_combobox_diem()