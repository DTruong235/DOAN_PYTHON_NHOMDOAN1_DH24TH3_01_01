import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Import hằng số và tiện ích
from constants import (
    APP_DARK_BLUE, APP_LIGHT_GREY,
    APP_ENTRY_STYLE, APP_LABEL_STYLE, APP_BUTTON_STYLE_YELLOW, 
    APP_BUTTON_STYLE_RED, APP_COMBOBOX_STYLE
)
from gui.ui_utils import setup_themed_treeview

class CourseTab(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color="transparent")
        self.db_manager = db_manager
        self.hocphan_entries = {}
        
        self._setup_layout_hocphan()

    def _setup_layout_hocphan(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        frame_fg_color = APP_DARK_BLUE

        input_frame_hp = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        input_frame_hp.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self._setup_hp_input_fields(input_frame_hp) 
        
        search_frame_hp = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        search_frame_hp.grid(row=1, column=0, padx=10, pady=5, sticky="new")
        self._setup_hp_search_bar(search_frame_hp) 
        
        tree_frame_hp = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        tree_frame_hp.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self._setup_hp_treeview(tree_frame_hp)
        
        self.load_hocphan()

    def _setup_hp_input_fields(self, input_frame_hp):
        input_frame_hp.columnconfigure((0, 2), weight=0); input_frame_hp.columnconfigure((1, 3), weight=1)
        
        # MaHP
        ctk.CTkLabel(input_frame_hp, text="Mã Học Phần", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_mahp = ctk.CTkEntry(input_frame_hp, width=120, **APP_ENTRY_STYLE)
        entry_mahp.grid(row=0, column=1, padx=5, pady=10, sticky="w"); self.hocphan_entries['mahp'] = entry_mahp
        
        # MaMH ComboBox
        ctk.CTkLabel(input_frame_hp, text="Mã Môn Học", **APP_LABEL_STYLE).grid(row=0, column=2, padx=(15, 5), pady=10, sticky="w")
        entry_mamh_hp = ctk.CTkComboBox(input_frame_hp, width=150, **APP_COMBOBOX_STYLE)
        entry_mamh_hp.grid(row=0, column=3, padx=5, pady=10, sticky="w"); self.hocphan_entries['mamh_hp'] = entry_mamh_hp
        self._populate_mamh_combobox() # Tải dữ liệu
        
        # HocKy
        ctk.CTkLabel(input_frame_hp, text="Học Kỳ", **APP_LABEL_STYLE).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_hocky = ctk.CTkEntry(input_frame_hp, width=80, **APP_ENTRY_STYLE)
        entry_hocky.grid(row=1, column=1, padx=5, pady=10, sticky="w"); self.hocphan_entries['hocky'] = entry_hocky
        
        # NamHoc
        ctk.CTkLabel(input_frame_hp, text="Năm Học", **APP_LABEL_STYLE).grid(row=1, column=2, padx=(15, 5), pady=10, sticky="w")
        entry_namhoc = ctk.CTkEntry(input_frame_hp, width=150, placeholder_text="vd: 2024-2025", **APP_ENTRY_STYLE)
        entry_namhoc.grid(row=1, column=3, padx=5, pady=10, sticky="w"); self.hocphan_entries['namhoc'] = entry_namhoc
        
        # GiangVien
        ctk.CTkLabel(input_frame_hp, text="Giảng Viên", **APP_LABEL_STYLE).grid(row=2, column=0, padx=(15, 5), pady=10, sticky="w")
        entry_gv = ctk.CTkEntry(input_frame_hp, **APP_ENTRY_STYLE)
        entry_gv.grid(row=2, column=1, columnspan=3, padx=5, pady=10, sticky="ew"); self.hocphan_entries['gv'] = entry_gv
        
        # Button Frame
        button_frame_hp = ctk.CTkFrame(input_frame_hp, fg_color="transparent")
        button_frame_hp.grid(row=3, column=0, columnspan=4, pady=(15, 10)); button_frame_hp.columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkButton(button_frame_hp, text="Thêm HP", command=self.handle_add_hp, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(button_frame_hp, text="Xóa HP", command=self.handle_delete_hp, **APP_BUTTON_STYLE_RED).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(button_frame_hp, text="Sửa HP", command=self.handle_update_hp, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=2, padx=10, pady=5)
        ctk.CTkButton(button_frame_hp, text="Làm Mới HP", command=self.handle_refresh_hp, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=3, padx=10, pady=5)

    def _setup_hp_search_bar(self, search_frame_hp):
        search_frame_hp.columnconfigure(1, weight=1)
        ctk.CTkLabel(search_frame_hp, text="Tìm HP:", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=10)
        entry_search_hp = ctk.CTkEntry(search_frame_hp, placeholder_text="Nhập từ khóa...", **APP_ENTRY_STYLE)
        entry_search_hp.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.hocphan_entries['search_hp'] = entry_search_hp

        ctk.CTkButton(search_frame_hp, text="Tìm HP", command=self.handle_search_hp, width=80, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=2, padx=15, pady=10)

    def _setup_hp_treeview(self, parent_frame):
        columns_config = {
            "MAHP": "Mã HP", "MAMH": "Mã MH", "TENMH": "Tên Môn Học",
            "HOCKY": "Học Kỳ", "NAMHOC": "Năm Học", "GV": "Giảng Viên"
        }
        self.tree_hp = setup_themed_treeview(parent_frame, columns_config, style_name="HocPhan.Treeview")
        
        self.tree_hp.column("MAHP", width=80, anchor=tk.CENTER, stretch=False)
        self.tree_hp.column("MAMH", width=100, anchor=tk.W, stretch=False)
        self.tree_hp.column("TENMH", width=250, anchor=tk.W)
        self.tree_hp.column("HOCKY", width=80, anchor=tk.CENTER, stretch=False)
        self.tree_hp.column("NAMHOC", width=120, anchor=tk.W, stretch=False)
        self.tree_hp.column("GV", width=200, anchor=tk.W)
        
        self.tree_hp.bind("<<TreeviewSelect>>", self._on_hp_select)

    def _populate_mamh_combobox(self):
        try:
            _, subjects = self.db_manager.fetch_all_subjects()
            mamh_list = sorted([subject[0] for subject in subjects]) # subject[0] là MAMH
            self.hocphan_entries['mamh_hp'].configure(values=mamh_list)
            self.hocphan_entries['mamh_hp'].set("")
        except Exception as e:
            messagebox.showerror("Lỗi Tải Môn Học", f"Không thể tải danh sách Mã Môn Học: {e}")
            self.hocphan_entries['mamh_hp'].configure(values=[])
            self.hocphan_entries['mamh_hp'].set("")

    def _populate_hp_treeview(self, hocphan_list):
        for item in self.tree_hp.get_children(): self.tree_hp.delete(item)
        for hp_row in hocphan_list:
            # (MAHP, MAMH, TEN_MH, HOCKY, NAMHOC, GV)
            self.tree_hp.insert("", tk.END, values=hp_row)

    def load_hocphan(self):
        try:
            columns, hocphans = self.db_manager.fetch_all_hocphan()
            self._populate_hp_treeview(hocphans)
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải danh sách học phần:\n{e}")

    def _clear_hp_entries(self):
        for key, entry_widget in self.hocphan_entries.items():
            if isinstance(entry_widget, ctk.CTkEntry):
                if key == 'mahp':
                    if entry_widget.cget('state') == 'disabled': 
                        entry_widget.configure(state='normal')
                if key != 'search_hp': 
                    entry_widget.delete(0, 'end')
            elif isinstance(entry_widget, ctk.CTkComboBox): 
                entry_widget.set("")
        if 'mahp' in self.hocphan_entries: 
            self.hocphan_entries['mahp'].focus()

    def _get_and_validate_hp_data(self):
        try: 
            mahp_str = self.hocphan_entries['mahp'].get().strip()
            mamh = self.hocphan_entries['mamh_hp'].get().strip()
            hocky_str = self.hocphan_entries['hocky'].get().strip()
            namhoc = self.hocphan_entries['namhoc'].get().strip()
            gv = self.hocphan_entries['gv'].get().strip()
        except KeyError as e: 
            messagebox.showerror("Lỗi", f"Lỗi truy cập ô nhập '{e}'."); return None
        
        if not mahp_str: messagebox.showwarning("Thiếu", "Mã Học Phần không được trống."); return None
        try: 
            mahp = int(mahp_str)
        except (ValueError): 
            messagebox.showwarning("Lỗi", "Mã Học Phần phải là số nguyên."); return None
        
        if not mamh: messagebox.showwarning("Thiếu", "Vui lòng chọn Mã Môn Học."); return None
        if not hocky_str: messagebox.showwarning("Thiếu", "Học Kỳ không được trống."); return None
        try: 
            hocky = int(hocky_str)
        except ValueError: 
            messagebox.showwarning("Lỗi", "Học Kỳ phải là số."); return None
        if not namhoc: messagebox.showwarning("Thiếu", "Năm Học không được trống."); return None
        
        # TỐI ƯU: Trả về dict
        return {
            "mahp": mahp, 
            "mamh": mamh, 
            "hocky": hocky, 
            "namhoc": namhoc, 
            "gv": gv
        }

    def _handle_hocphan_integrity_error(self, e, mahp, mamh=None):
        """(MỚI) Xử lý lỗi Integrity cho Học Phần."""
        error_message = str(e)
        if "PRIMARY KEY" in error_message:
            messagebox.showwarning("Lỗi Dữ Liệu", f"Mã học phần '{mahp}' đã tồn tại.")
        elif "FOREIGN KEY constraint 'FK_HOCPHAN'" in error_message:
             messagebox.showwarning("Lỗi Dữ Liệu", f"Mã môn học '{mamh}' không tồn tại trong bảng Môn Học.")
        elif "CHECK constraint" in error_message: 
             messagebox.showwarning("Lỗi Dữ Liệu", "Mã học phần phải là số nguyên dương.")
        elif "FOREIGN KEY" in error_message:
             messagebox.showwarning("Lỗi Ràng Buộc", f"Không thể xóa học phần '{mahp}' vì có dữ liệu điểm liên quan.")
        else:
             messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi toàn vẹn không xác định: {e}")

    def _on_hp_select(self, event):
        selected = self.tree_hp.selection()
        if not selected: return
        values = self.tree_hp.item(selected[0], 'values')
        try:
            self._clear_hp_entries()
            mahp, mamh, tenmh, hocky, namhoc, gv = values
            self.hocphan_entries['mahp'].insert(0, mahp)
            self.hocphan_entries['mamh_hp'].set(mamh)
            self.hocphan_entries['hocky'].insert(0, hocky)
            self.hocphan_entries['namhoc'].insert(0, namhoc)
            self.hocphan_entries['gv'].insert(0, gv)
            self.hocphan_entries['mahp'].configure(state='disabled')
        except (IndexError, ValueError, KeyError, tk.TclError) as e: 
            messagebox.showerror("Lỗi", f"Không tải được dữ liệu HP: {e}")

    def handle_add_hp(self):
        if self.hocphan_entries['mahp'].cget('state') == 'disabled': 
            messagebox.showwarning("Lỗi", "Đang chọn sửa, nhấn 'Làm Mới HP' trước."); return
        
        data = self._get_and_validate_hp_data()
        if data is None: return
        
        try:
            self.db_manager.add_hocphan(**data)
            messagebox.showinfo("OK", f"Thêm HP {data['mahp']} thành công.")
            self.handle_refresh_hp()
        except pyodbc.IntegrityError as e:
            self._handle_hocphan_integrity_error(e, data['mahp'], data['mamh'])
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Mới", f"Lỗi không xác định khi thêm học phần: {e}")

    def handle_delete_hp(self):
        selected = self.tree_hp.selection()
        if not selected: 
            messagebox.showwarning("Lỗi", "Chọn HP cần xóa."); return
        
        try:
            values = self.tree_hp.item(selected[0], 'values')
            mahp = values[0]; tenmh = values[2]
        except IndexError: 
            messagebox.showerror("Lỗi", "Không lấy được thông tin HP."); return
        
        if messagebox.askyesno("Xóa?", f"Xóa học phần '{tenmh}' (Mã HP: {mahp})?"):
            try:
                self.db_manager.delete_hocphan(mahp)
                messagebox.showinfo("OK", f"Xóa HP {mahp} thành công.")
                self.handle_refresh_hp()
            except pyodbc.IntegrityError as e:
                self._handle_hocphan_integrity_error(e, mahp)
            except Exception as e:
                messagebox.showerror("Lỗi Xóa", f"Lỗi không xác định khi xóa học phần: {e}")

    def handle_update_hp(self):
        if self.hocphan_entries['mahp'].cget('state') == 'normal': 
            messagebox.showwarning("Lỗi", "Chọn HP cần sửa từ danh sách."); return
        
        data_to_validate = self._get_and_validate_hp_data()
        if data_to_validate is None: return
        
        try: 
            # Lấy MAHP gốc (đang bị disabled)
            mahp_goc = int(self.hocphan_entries['mahp'].get())
            data_to_validate['mahp'] = mahp_goc # Gán lại mahp gốc vào dict
        except ValueError: 
            messagebox.showerror("Lỗi", "Mã Học Phần trên form không hợp lệ."); return
        
        try:
            self.db_manager.update_hocphan(**data_to_validate)
            messagebox.showinfo("OK", f"Cập nhật HP {mahp_goc} thành công.")
            self.handle_refresh_hp()
        except pyodbc.IntegrityError as e:
            self._handle_hocphan_integrity_error(e, mahp_goc, data_to_validate['mamh'])
        except Exception as e:
             messagebox.showerror("Lỗi Cập Nhật", f"Lỗi không xác định khi cập nhật học phần: {e}")

    def handle_refresh_hp(self):
        self._clear_hp_entries()
        self.hocphan_entries['search_hp'].delete(0, 'end')
        self.load_hocphan()
        self._populate_mamh_combobox() # Tải lại danh sách môn học

    def handle_search_hp(self):
        try:
            search_keyword = self.hocphan_entries['search_hp'].get().strip()
            columns, hocphans = self.db_manager.find_hocphan(search_keyword)
            self._populate_hp_treeview(hocphans)
            if not hocphans and search_keyword: 
                messagebox.showinfo("Tìm kiếm", f"Không tìm thấy học phần nào khớp với '{search_keyword}'.")
        except Exception as e: 
            messagebox.showerror("Lỗi Tìm Kiếm", f"Lỗi khi tìm học phần: {e}")
            self._populate_hp_treeview([])