import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import re
import pyodbc

# Import hằng số và tiện ích
from constants import (
    APP_DARK_BLUE, APP_LIGHT_GREY,
    APP_ENTRY_STYLE, APP_LABEL_STYLE, APP_BUTTON_STYLE_YELLOW, APP_BUTTON_STYLE_RED
)
from gui.ui_utils import setup_themed_treeview

class SubjectTab(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color="transparent")
        self.db_manager = db_manager
        self.subject_entries = {}
        
        self._setup_layout_monhoc()

    def _setup_layout_monhoc(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        frame_fg_color = APP_DARK_BLUE

        input_frame_mh = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        input_frame_mh.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        
        input_frame_mh.columnconfigure((0, 2), weight=0); input_frame_mh.columnconfigure((1, 3), weight=1)
        
        # MaMH
        ctk.CTkLabel(input_frame_mh, text="Mã Môn Học", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_mamh = ctk.CTkEntry(input_frame_mh, width=150, **APP_ENTRY_STYLE)
        entry_mamh.grid(row=0, column=1, padx=5, pady=10, sticky="w"); self.subject_entries['mamh'] = entry_mamh

        # TenMH
        ctk.CTkLabel(input_frame_mh, text="Tên Môn Học", **APP_LABEL_STYLE).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_tenmh = ctk.CTkEntry(input_frame_mh, **APP_ENTRY_STYLE)
        entry_tenmh.grid(row=1, column=1, columnspan=3, padx=5, pady=10, sticky="ew"); self.subject_entries['tenmh'] = entry_tenmh
        
        # SoTC
        ctk.CTkLabel(input_frame_mh, text="Số Tín Chỉ", **APP_LABEL_STYLE).grid(row=0, column=2, padx=(15, 5), pady=10, sticky="w")
        entry_sotc = ctk.CTkEntry(input_frame_mh, width=80, **APP_ENTRY_STYLE)
        entry_sotc.grid(row=0, column=3, padx=5, pady=10, sticky="w"); self.subject_entries['sotc'] = entry_sotc
        
        # Button Frame
        button_frame_mh = ctk.CTkFrame(input_frame_mh, fg_color="transparent")
        button_frame_mh.grid(row=2, column=0, columnspan=4, pady=(15, 10)); button_frame_mh.columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkButton(button_frame_mh, text="Thêm MH", command=self.handle_add_subject, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame_mh, text="Xóa MH", command=self.handle_delete_subject, **APP_BUTTON_STYLE_RED).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame_mh, text="Sửa MH", command=self.handle_update_subject, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(button_frame_mh, text="Làm Mới MH", command=self.handle_refresh_subjects, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=3, padx=10, pady=5)
        
        # Search Frame
        search_frame_mh = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        search_frame_mh.grid(row=1, column=0, padx=10, pady=5, sticky="new"); search_frame_mh.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame_mh, text="Tìm Mã Môn Học:", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_mamh = ctk.CTkEntry(search_frame_mh, placeholder_text="Nhập mã môn học...", **APP_ENTRY_STYLE)
        entry_search_mamh.grid(row=0, column=1, padx=5, pady=10, sticky="ew"); self.subject_entries['search_mamh'] = entry_search_mamh
        ctk.CTkButton(search_frame_mh, text="Tìm MH", command=self.handle_search_subject, width=80, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=2, padx=15, pady=10)
        
        # Treeview Frame
        tree_frame_mh = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        tree_frame_mh.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self._setup_subject_treeview(tree_frame_mh) # Hàm setup_themed_treeview sẽ config grid
        self.load_subjects()

    def _setup_subject_treeview(self, parent_frame):
        columns_config = {
            "MAMH": "Mã Môn Học",
            "TENMH": "Tên Môn Học",
            "SOTC": "Số Tín Chỉ"
        }
        
        self.tree_mh = setup_themed_treeview(
            parent_frame, 
            columns_config, 
            style_name="Subject.Treeview"
        )
        
        self.tree_mh.column("MAMH", width=150, anchor=tk.W, stretch=False)
        self.tree_mh.column("TENMH", width=400, anchor=tk.W)
        self.tree_mh.column("SOTC", width=100, anchor=tk.CENTER, stretch=False)
        
        self.tree_mh.bind("<<TreeviewSelect>>", self._on_subject_select)

    def _populate_subject_treeview(self, subjects_list):
        for item in self.tree_mh.get_children(): self.tree_mh.delete(item)
        for subject_row in subjects_list:
            # Dữ liệu từ DB có 4 cột (thêm KHOA), chỉ hiển thị 3
            if len(subject_row) >= 3: 
                display_values = (subject_row[0], subject_row[1], subject_row[2])
                self.tree_mh.insert("", tk.END, values=display_values)

    def load_subjects(self):
        try:
            columns, subjects = self.db_manager.fetch_all_subjects()
            self._populate_subject_treeview(subjects)
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải danh sách môn học:\n{e}")

    def _clear_subject_entries(self):
        for key, entry_widget in self.subject_entries.items():
            if isinstance(entry_widget, ctk.CTkEntry):
                if key == 'mamh':
                    if entry_widget.cget('state') == 'disabled': 
                        entry_widget.configure(state='normal')
                if key != 'search_mamh':
                     entry_widget.delete(0, 'end')
        if 'mamh' in self.subject_entries: 
            self.subject_entries['mamh'].focus()

    def _get_and_validate_subject_data(self):
        # (Logic validate giống hệt file cũ)
        try: 
            mamh_raw = self.subject_entries['mamh'].get().strip()
            ten_mh = self.subject_entries['tenmh'].get().strip()
            sotc_str = self.subject_entries['sotc'].get().strip()
            khoa = 'CNTT'
        except KeyError as e: 
            messagebox.showerror("Lỗi Cấu Hình", f"Lỗi truy cập ô nhập liệu môn học '{e}'."); return None
        
        if not mamh_raw: messagebox.showwarning("Thiếu thông tin", "Mã môn học (MAMH) không được để trống."); return None
        mamh = mamh_raw.upper()
        
        if not re.match(r'^[A-Z]{3}\d{3}$', mamh): messagebox.showwarning("Lỗi Dữ Liệu", "Định dạng Mã Môn Học không hợp lệ (Yêu cầu: 3 chữ thường và 3 số, ví dụ: 'abc123')."); return None
        if not ten_mh: messagebox.showwarning("Thiếu thông tin", "Tên môn học không được để trống."); return None
        if not sotc_str: messagebox.showwarning("Thiếu thông tin", "Số tín chỉ không được để trống."); return None
        
        try:
            sotinchi = int(sotc_str)
            if not (1 <= sotinchi <= 10): 
                messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải là số nguyên từ 1 đến 10."); return None
        except ValueError: 
            messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải là một con số (số nguyên)."); return None
        
        # TỐI ƯU: Trả về dict
        return {
            "mamh": mamh, 
            "ten_mh": ten_mh, 
            "sotinchi": sotinchi, 
            "khoa": khoa
        }
    
    def _handle_subject_integrity_error(self, e, mamh):
        """ Xử lý lỗi Integrity cho Môn học."""
        error_message = str(e)
        if "PRIMARY KEY" in error_message:
            messagebox.showwarning("Lỗi Dữ Liệu", f"Mã môn học '{mamh}' đã tồn tại.")
        elif "CHECK constraint" in error_message:
             if "SOTINCHI" in error_message:
                 messagebox.showwarning("Lỗi Dữ Liệu", "Số tín chỉ phải từ 1 đến 10.")
             elif "MAMH" in error_message:
                 messagebox.showwarning("Lỗi Dữ Liệu", "Mã môn học phải theo định dạng 'aaa###' (vd: dsg101).")
             else:
                 messagebox.showwarning("Lỗi Dữ Liệu", f"Dữ liệu vi phạm ràng buộc CHECK: {e}")
        elif "FOREIGN KEY" in error_message: # Lỗi khi xóa
             messagebox.showwarning("Lỗi Ràng Buộc", f"Không thể xóa môn học '{mamh}' vì có học phần hoặc điểm liên quan.")
        else:
             messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")

    def _on_subject_select(self, event):
     
        selected_item = self.tree_mh.selection()
        if not selected_item: return
        values = self.tree_mh.item(selected_item[0], 'values')
        
        try:
            self._clear_subject_entries()
            mamh = values[0]; ten_mh = values[1]; sotc = values[2]
            self.subject_entries['mamh'].insert(0, mamh)
            self.subject_entries['tenmh'].insert(0, ten_mh)
            self.subject_entries['sotc'].insert(0, sotc)
            self.subject_entries['mamh'].configure(state='disabled')
        except (IndexError, KeyError, tk.TclError) as e: 
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải thông tin môn học lên form. Lỗi: {e}")

    def handle_add_subject(self):
        if self.subject_entries['mamh'].cget('state') == 'disabled': 
            messagebox.showwarning("Trạng thái không hợp lệ", "Đang chọn môn học để sửa. Nhấn 'Làm Mới MH' trước khi thêm."); return
        
        data = self._get_and_validate_subject_data()
        if data is None: return
        
        try:
            self.db_manager.add_subject(**data)
            messagebox.showinfo("Thành công", f"Đã thêm môn học '{data['ten_mh']}' ({data['mamh']}).")
            self.handle_refresh_subjects()
        except pyodbc.IntegrityError as e:
            self._handle_subject_integrity_error(e, data.get('mamh', ''))
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Mới", f"Có lỗi xảy ra khi thêm môn học: {e}")

    def handle_delete_subject(self):
        selected_item = self.tree_mh.selection()
        if not selected_item: 
            messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một môn học trong danh sách để xóa."); return
        
        try:
            values = self.tree_mh.item(selected_item[0], 'values')
            mamh_to_delete = values[0]; ten_mh_to_delete = values[1]
        except IndexError: 
            messagebox.showerror("Lỗi", "Không thể lấy thông tin môn học để xóa."); return
        
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa môn học '{ten_mh_to_delete}' ({mamh_to_delete})?"):
            try:
                self.db_manager.delete_subject(mamh_to_delete)
                messagebox.showinfo("Thành công", f"Đã xóa môn học '{ten_mh_to_delete}'.")
                self.handle_refresh_subjects()
            except pyodbc.IntegrityError as e:
                self._handle_subject_integrity_error(e, mamh_to_delete) # Xử lý lỗi FK
            except Exception as e:
                messagebox.showerror("Lỗi Xóa", f"Có lỗi xảy ra khi xóa môn học: {e}")

    def handle_update_subject(self):
        if self.subject_entries['mamh'].cget('state') == 'normal': 
            messagebox.showwarning("Chưa Chọn", "Vui lòng chọn một môn học từ danh sách trước khi sửa."); return
        
        data_to_validate = self._get_and_validate_subject_data()
        if data_to_validate is None: return
        
        # Lấy mamh (đã bị disabled) riêng
        mamh = self.subject_entries['mamh'].get().strip().lower()
        if not mamh: 
            messagebox.showwarning("Lỗi", "Không xác định được Mã Môn Học cần sửa."); return
        
        # Gán mamh vào dict data
        data_to_validate['mamh'] = mamh
        
        try:
            self.db_manager.update_subject(**data_to_validate)
            messagebox.showinfo("Thành công", f"Đã cập nhật môn học '{data_to_validate['ten_mh']}' ({mamh}).")
            self.handle_refresh_subjects()
        except pyodbc.IntegrityError as e: # Bắt lỗi CHECK khi update
            self._handle_subject_integrity_error(e, mamh)
        except Exception as e:
            messagebox.showerror("Lỗi Cập Nhật", f"Có lỗi xảy ra khi cập nhật môn học: {e}")

    def handle_refresh_subjects(self):
        self._clear_subject_entries()
        self.subject_entries['search_mamh'].delete(0, 'end')
        self.load_subjects()

    def handle_search_subject(self):
        try:
            search_keyword = self.subject_entries['search_mamh'].get().strip()
            columns, subjects = self.db_manager.find_subject(search_keyword)
            self._populate_subject_treeview(subjects)
            if not subjects and search_keyword: 
                messagebox.showinfo("Tìm kiếm", f"Không tìm thấy môn học nào khớp với '{search_keyword}'.")
        except Exception as e: 
            messagebox.showerror("Lỗi Tìm Kiếm", f"Có lỗi xảy ra khi tìm kiếm môn học:\n{e}")
            self._populate_subject_treeview([])