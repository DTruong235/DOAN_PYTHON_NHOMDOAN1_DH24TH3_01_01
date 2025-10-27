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
        # Configure tabview colors to blend better
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
        self.tab_bangdiem = notebook.add("Bảng điểm")
        notebook.set("Sinh viên")

        self._setup_layout_sinhvien(self.tab_sinhvien)
        self._setup_layout_monhoc(self.tab_mohoc)

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

    # --- === 6. Treeview: Keep Existing Style === ---
    # The _setup_student_treeview method should remain exactly as it was
    # in the previous version (white background, black text, blue header).
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