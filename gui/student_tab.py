import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import re
from datetime import datetime
import pyodbc # Import để bắt lỗi

# Import từ các file local
from constants import (
    APP_DARK_BLUE, APP_LIGHT_GREY,
    APP_ENTRY_STYLE, APP_LABEL_STYLE, APP_BUTTON_STYLE_YELLOW, APP_BUTTON_STYLE_RED
)
from gui.ui_utils import setup_themed_treeview

class StudentTab(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color="transparent") # Nền trong suốt để khớp với TabView
        self.db_manager = db_manager
        self.entries = {}
        
        self._setup_layout()

    def _setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) 

        frame_fg_color = APP_DARK_BLUE

        self.input_frame = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")

        self.search_bar_frame = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        self.search_bar_frame.grid(row=1, column=0, padx=10, pady=5, sticky="new")

        tree_frame = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.tree_frame = tree_frame 

        self._setup_input_fields()
        self._setup_student_treeview()
        self.load_students()

    def _setup_input_fields(self):
        input_frame = self.input_frame
        
        # --- Input Widgets ---
        ctk.CTkLabel(input_frame, text="MSSV", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        entry_masv = ctk.CTkEntry(input_frame, width=150, **APP_ENTRY_STYLE)
        entry_masv.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        self.entries['masv'] = entry_masv

        ctk.CTkLabel(input_frame, text="Họ và tên", **APP_LABEL_STYLE).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        entry_ten = ctk.CTkEntry(input_frame, width=200, **APP_ENTRY_STYLE)
        entry_ten.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        self.entries['ten'] = entry_ten

        rad_gt = ctk.StringVar(value="Nam")
        ctk.CTkLabel(input_frame, text="Giới tính", **APP_LABEL_STYLE).grid(row=2, column=0, padx=(15, 5), pady=8, sticky="w")
        radio_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        ctk.CTkRadioButton(radio_frame, text="Nam", value="Nam", variable=rad_gt, text_color=APP_LIGHT_GREY).pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="Nữ", value="Nữ", variable=rad_gt, text_color=APP_LIGHT_GREY).pack(side="left", padx=10)
        radio_frame.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        self.entries['gioitinh'] = rad_gt

        ctk.CTkLabel(input_frame, text="Ngày sinh", **APP_LABEL_STYLE).grid(row=3, column=0, padx=(15, 5), pady=8, sticky="w")
        entry_ngaysinh = DateEntry(input_frame, width=20, date_pattern='dd/MM/yyyy', borderwidth=2,font=("Segoe UI", 13))
        style = ttk.Style()
        style.configure('DateEntry', 
                        fieldbackground=APP_ENTRY_STYLE["fg_color"], 
                        foreground=APP_ENTRY_STYLE["text_color"], 
                        bordercolor=APP_ENTRY_STYLE["border_color"], 
                        arrowcolor=APP_ENTRY_STYLE["text_color"])
        entry_ngaysinh.grid(row=3, column=1, padx=5, pady=8, sticky="w")
        entry_ngaysinh.delete(0, tk.END)
        self.entries['ngaysinh'] = entry_ngaysinh

        # Second column
        ctk.CTkLabel(input_frame, text="Địa chỉ", **APP_LABEL_STYLE).grid(row=0, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_diachi = ctk.CTkEntry(input_frame, width=200, **APP_ENTRY_STYLE)
        entry_diachi.grid(row=0, column=3, padx=5, pady=8, sticky="w")
        self.entries['diachi'] = entry_diachi

        ctk.CTkLabel(input_frame, text="Khóa học", **APP_LABEL_STYLE).grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_khoahoc = ctk.CTkEntry(input_frame, width=80, **APP_ENTRY_STYLE)
        entry_khoahoc.grid(row=1, column=3, padx=5, pady=8, sticky="w")
        self.entries['khoahoc'] = entry_khoahoc

        ctk.CTkLabel(input_frame, text="Khoa", **APP_LABEL_STYLE).grid(row=2, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_khoa = ctk.CTkEntry(input_frame, width=150, **APP_ENTRY_STYLE)
        entry_khoa.grid(row=2, column=3, padx=5, pady=8, sticky="w")
        self.entries['khoa'] = entry_khoa

        ctk.CTkLabel(input_frame, text="Email", **APP_LABEL_STYLE).grid(row=3, column=2, padx=(15, 5), pady=8, sticky="w")
        entry_email = ctk.CTkEntry(input_frame, width=200, **APP_ENTRY_STYLE)
        entry_email.grid(row=3, column=3, padx=5, pady=8, sticky="w")
        self.entries['email'] = entry_email

        # --- Buttons ---
        ctk.CTkButton(input_frame, text="Thêm SV", command=self.handle_add_student, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=4, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(input_frame, text="Xóa SV", command=self.handle_delete_student, **APP_BUTTON_STYLE_RED).grid(row=1, column=4, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(input_frame, text="Sửa SV", command=self.handle_update_student, **APP_BUTTON_STYLE_YELLOW).grid(row=2, column=4, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(input_frame, text="Làm Mới", command=self.handle_refresh_data, **APP_BUTTON_STYLE_YELLOW).grid(row=3, column=4, padx=15, pady=8, sticky="ew")

        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(4, weight=0)

        # --- Search Bar ---
        search_frame = self.search_bar_frame
        search_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Tìm kiếm Mã SV:", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_masv = ctk.CTkEntry(search_frame, placeholder_text="Nhập mã sinh viên...", **APP_ENTRY_STYLE)
        entry_search_masv.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.entries['search_masv'] = entry_search_masv
        
        ctk.CTkButton(search_frame, text="Tìm", command=self.handle_search_and_load, width=80, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=2, padx=15, pady=10)
    
    def _setup_student_treeview(self):
        columns_config = {
            "MASV": "Mã SV", "TEN": "Họ Tên", "GIOITINH": "Giới tính",
            "NGAYSINH": "Ngày sinh", "DIACHI": "Địa chỉ", "KHOAHOC": "Khóa học",
            "KHOA": "Khoa", "EMAIL": "Email"
        }
        
        # Gọi hàm tiện ích
        self.tree = setup_themed_treeview(
            self.tree_frame, 
            columns_config, 
            style_name="Student.Treeview"
        )

        self.tree.column("MASV", width=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("TEN", width=180, anchor=tk.W)
        self.tree.column("GIOITINH", width=70, anchor=tk.CENTER, stretch=False)
        self.tree.column("NGAYSINH", width=100, anchor=tk.W, stretch=False)
        self.tree.column("DIACHI", width=200, anchor=tk.W)
        self.tree.column("KHOAHOC", width=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("KHOA", width=120, anchor=tk.W)
        self.tree.column("EMAIL", width=200, anchor=tk.W)

        self.tree.bind("<<TreeviewSelect>>", self._on_student_select)
    
    def _populate_treeview(self, students_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for student_row in students_list:
            self.tree.insert("", tk.END, values=student_row)

    def load_students(self):
        try:
            columns, students = self.db_manager.fetch_all_students()
            if columns is not None:
                self._populate_treeview(students)
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải danh sách sinh viên:\n{e}")

    def _get_and_validate_form_data(self):
        # (Giữ nguyên logic validate của bạn)
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
                messagebox.showwarning("Lỗi Dữ Liệu", "Định dạng Email không hợp lệ. (Yêu cầu: gmail.com)")
                return None
            email = email_raw

        ngaysinh = None
        if ngaysinh_raw:
            try:
                date_obj = datetime.strptime(ngaysinh_raw, '%d/%m/%Y')
                ngaysinh = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Lỗi Dữ Liệu", "Định dạng Ngày sinh không hợp lệ. (Yêu cầu: DD/MM/YYYY)")
                return None

        diachi = diachi_raw if diachi_raw else None
        khoa = khoa_raw if khoa_raw else None

        # TỐI ƯU: Trả về dict
        return {
            "masv": masv, "ten": ten, "gioitinh": gioitinh, "ngaysinh": ngaysinh,
            "diachi": diachi, "khoahoc": khoahoc, "khoa": khoa, "email": email
        }

    def _handle_student_integrity_error(self, e, masv):
        """(MỚI) Xử lý lỗi Integrity từ DB."""
        error_message = str(e)
        if "PRIMARY KEY" in error_message:
            messagebox.showwarning("Lỗi Dữ Liệu", f"Mã sinh viên (MASV) '{masv}' đã tồn tại trong hệ thống.")
        elif "UNIQUE constraint" in error_message:
            messagebox.showwarning("Lỗi Dữ Liệu", "Lỗi trùng lặp: Email hoặc một trường duy nhất nào đó đã tồn tại.")
        elif "FOREIGN KEY" in error_message:
            messagebox.showwarning("Lỗi Dữ Liệu", "Lỗi khóa ngoại: Khoa hoặc một trường tham chiếu không tồn tại.")
        elif "CHECK constraint" in error_message:
            messagebox.showwarning("Lỗi Dữ Liệu", "Dữ liệu vi phạm ràng buộc CHECK. (Ví dụ: Sai định dạng MASV, Khóa học không hợp lệ,...)")
        else:
            messagebox.showwarning("Lỗi Toàn Vẹn", f"Vui lòng nhập đủ thônng tin và đảm bảo dữ liệu hợp lệ.\nChi tiết lỗi: {error_message}")

    def handle_add_student(self):
        data = self._get_and_validate_form_data()
        if data is None: 
            return
        
        try:
            # TỐI ƯU: Dùng **data để "unpack" dict
            self.db_manager.add_student(**data)
            messagebox.showinfo("Thành công", f"Đã thêm sinh viên {data['ten']} ({data['masv']}).")
            self.handle_refresh_data()
        except pyodbc.IntegrityError as e:
            self._handle_student_integrity_error(e, data.get('masv', ''))
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Mới", f"Có lỗi xảy ra khi thêm sinh viên: {e}")

    def handle_delete_student(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lựa chọn", "Vui lòng chọn một sinh viên trong danh sách để xóa.")
            return
        
        try:
            values = self.tree.item(selected_item[0], 'values')
            masv = values[0]; ten = values[1]
        except IndexError:
            messagebox.showerror("Lỗi", "Không thể lấy thông tin sinh viên để xóa.")
            return

        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa sinh viên {ten} ({masv})?"):
            try:
                self.db_manager.delete_student(masv)
                messagebox.showinfo("Thành công", f"Đã xóa sinh viên {ten} ({masv}).")
                self.handle_refresh_data()
            except pyodbc.IntegrityError:
                messagebox.showwarning("Lỗi Ràng Buộc", "Không thể xóa sinh viên này vì đang có dữ liệu điểm (KETQUA) liên quan.")
            except Exception as e:
                messagebox.showerror("Lỗi Xóa", f"Có lỗi xảy ra khi xóa sinh viên: {e}")

    def _clear_entries(self):
        # (Logic giống hệt file cũ)
        for key, entry_widget in self.entries.items():
            if isinstance(entry_widget, (ctk.CTkEntry, DateEntry)):
                if key == 'search_masv':
                    continue
                if key == 'masv':
                    entry_widget.configure(state='normal')
                    entry_widget.delete(0, 'end')
                else:
                    entry_widget.delete(0, 'end')
            elif isinstance(entry_widget, ctk.StringVar):
                if key == 'gioitinh':
                    entry_widget.set("Nam")

    def handle_refresh_data(self):
        self._clear_entries()
        self.entries['search_masv'].delete(0, 'end')
        self.load_students()

    def handle_search_and_load(self):
        try:
            search_keyword = self.entries['search_masv'].get().strip()
            columns, students = self.db_manager.find_student(search_keyword)
            
            self._populate_treeview(students)
            if not students and search_keyword:
                messagebox.showinfo("Tìm kiếm", f"Không tìm thấy sinh viên nào khớp với '{search_keyword}'.")
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn Hệ thống", f"Đã xảy ra lỗi khi thực hiện tìm kiếm:\n{e}")

    def _on_student_select(self, event):
        # (Logic giống hệt file cũ)
        selected_item = self.tree.selection()
        if not selected_item: return
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
            self.entries['masv'].configure(state='disabled')
        except (IndexError, KeyError, tk.TclError) as e:
             messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải thông tin sinh viên. Lỗi: {e}")

    def handle_update_student(self):
        data = self._get_and_validate_form_data()
        if data is None: 
            return
        
        try:
            self.db_manager.update_student(**data)
            messagebox.showinfo("Thành công", f"Đã cập nhật sinh viên {data['ten']} ({data['masv']}).")
            self.handle_refresh_data()
        except pyodbc.IntegrityError as e: # Lỗi CHECK hoặc UNIQUE khi update
             self._handle_student_integrity_error(e, data['masv'])
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật", f"Có lỗi xảy ra khi cập nhật sinh viên: {e}")