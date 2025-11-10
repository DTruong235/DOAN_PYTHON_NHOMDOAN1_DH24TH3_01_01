
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Import hằng số và tiện ích
from constants import (
    APP_DARK_BLUE, APP_LIGHT_GREY,
    APP_LABEL_STYLE, APP_BUTTON_STYLE_YELLOW, 
    APP_BUTTON_STYLE_RED, APP_COMBOBOX_STYLE
)
from gui.ui_utils import setup_themed_treeview

class PrerequisiteTab(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master, fg_color="transparent")
        self.db_manager = db_manager
        
        # Dùng để lưu các ComboBox và Entry
        self.entries = {}
        # Dùng để map Tên Môn Học (hiển thị) về Mã Môn Học (ID)
        self.mamh_data_map = {} 
        
        self._setup_layout()

    def _setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1) # Treeview co giãn

        frame_fg_color = APP_DARK_BLUE

        # --- 1. Frame Nhập Liệu (row 0) ---
        input_frame = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self._setup_input_fields(input_frame)
        
        # --- 2. Frame Treeview (row 1) ---
        tree_frame = ctk.CTkFrame(self, fg_color=frame_fg_color, corner_radius=10)
        tree_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self._setup_dkien_treeview(tree_frame)

        # --- Tải dữ liệu ban đầu ---
        self.load_all_data()

    def _setup_input_fields(self, input_frame):
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        # ComboBox Môn chính (MAMH)
        ctk.CTkLabel(input_frame, text="Môn Học Chính:", **APP_LABEL_STYLE).grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        combo_mamh = ctk.CTkComboBox(input_frame, **APP_COMBOBOX_STYLE, values=[])
        combo_mamh.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.entries['mamh_combo'] = combo_mamh

        # ComboBox Môn tiên quyết (MAMH_TRUOC)
        ctk.CTkLabel(input_frame, text="Môn Tiên Quyết:", **APP_LABEL_STYLE).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")
        combo_mamh_truoc = ctk.CTkComboBox(input_frame, **APP_COMBOBOX_STYLE, values=[])
        combo_mamh_truoc.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.entries['mamh_truoc_combo'] = combo_mamh_truoc

        # Frame chứa các nút
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, rowspan=2, columnspan=2, padx=15, pady=10, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)
        
        ctk.CTkButton(button_frame, text="Thêm Điều Kiện", command=self.handle_add_prerequisite, **APP_BUTTON_STYLE_YELLOW).grid(row=0, column=0, padx=10, pady=(5, 5), sticky="ew")
        ctk.CTkButton(button_frame, text="Xóa Điều Kiện", command=self.handle_delete_prerequisite, **APP_BUTTON_STYLE_RED).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(button_frame, text="Làm Mới", command=self.load_all_data, **APP_BUTTON_STYLE_YELLOW).grid(row=2, column=0, padx=10, pady=5, sticky="ew")


    def _setup_dkien_treeview(self, parent_frame):
        columns_config = {
            "MAMH": "Mã Môn Chính",
            "TEN_MH": "Tên Môn Chính",
            "MAMH_TRUOC": "Mã Môn Tiên Quyết",
            "TEN_MH_TRUOC": "Tên Môn Tiên Quyết"
        }
        self.tree_dkien = setup_themed_treeview(parent_frame, columns_config, style_name="Dkien.Treeview")
        
        self.tree_dkien.column("MAMH", width=120, anchor=tk.W, stretch=False)
        self.tree_dkien.column("TEN_MH", width=250, anchor=tk.W)
        self.tree_dkien.column("MAMH_TRUOC", width=150, anchor=tk.W, stretch=False)
        self.tree_dkien.column("TEN_MH_TRUOC", width=250, anchor=tk.W)
        
        self.tree_dkien.bind("<<TreeviewSelect>>", self._on_dkien_select)
    
    def _populate_mamh_comboboxes(self):
        """Tải danh sách môn học vào cả 2 ComboBox."""
        self.mamh_data_map.clear()
        try:
            _, subjects = self.db_manager.fetch_all_subjects()
            # subjects = (MAMH, TEN_MH, SOTC, KHOA)
            
            display_list = []
            for subject in subjects:
                mamh, ten_mh = subject[0], subject[1]
                display_string = f"{mamh} - {ten_mh}"
                
                # Lưu vào map để tra cứu ngược
                self.mamh_data_map[display_string] = mamh
                display_list.append(display_string)

            display_list.sort()
            
            self.entries['mamh_combo'].configure(values=display_list)
            self.entries['mamh_truoc_combo'].configure(values=display_list)
            
        except Exception as e:
            messagebox.showerror("Lỗi Tải Môn Học", f"Không thể tải danh sách Môn Học cho ComboBox: {e}")

    def _populate_dkien_treeview(self, prerequisites_list):
        for item in self.tree_dkien.get_children(): 
            self.tree_dkien.delete(item)
        for row in prerequisites_list:
            # (MAMH, TEN_MH, MAMH_TRUOC, TEN_MH_TRUOC)
            self.tree_dkien.insert("", tk.END, values=row)

    def _clear_entries(self):
        self.entries['mamh_combo'].set("")
        self.entries['mamh_truoc_combo'].set("")
        # Bỏ chọn trên Treeview
        if self.tree_dkien.selection():
            self.tree_dkien.selection_remove(self.tree_dkien.selection())

    def load_all_data(self):
        """Hàm "Làm Mới" - Tải lại ComboBox và Treeview."""
        try:
            # Tải ComboBox
            self._populate_mamh_comboboxes()
            
            # Tải Treeview
            _, prerequisites = self.db_manager.fetch_all_prerequisites()
            self._populate_dkien_treeview(prerequisites)
            
            # Xóa các lựa chọn
            self._clear_entries()
            
        except Exception as e:
            messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải dữ liệu môn tiên quyết:\n{e}")

    def _on_dkien_select(self, event):
        """Khi click vào 1 dòng trong Treeview, điền thông tin lên 2 ComboBox."""
        selected_item = self.tree_dkien.selection()
        if not selected_item: 
            return
        
        values = self.tree_dkien.item(selected_item[0], 'values')
        
        try:
            mamh, ten_mh, mamh_truoc, ten_mh_truoc = values
            
            # Tạo lại chuỗi hiển thị chuẩn
            display_mamh = f"{mamh} - {ten_mh}"
            display_mamh_truoc = f"{mamh_truoc} - {ten_mh_truoc}"
            
            # Set giá trị cho ComboBox
            self.entries['mamh_combo'].set(display_mamh)
            self.entries['mamh_truoc_combo'].set(display_mamh_truoc)
            
        except (IndexError, KeyError, tk.TclError) as e:
             messagebox.showerror("Lỗi Tải Dữ Liệu", f"Không thể tải thông tin điều kiện lên form. Lỗi: {e}")

    def _get_and_validate_dkien_data(self):
        """Lấy MAMH và MAMH_TRUOC từ ComboBox."""
        try:
            display_mamh = self.entries['mamh_combo'].get()
            display_mamh_truoc = self.entries['mamh_truoc_combo'].get()

            if not display_mamh or not display_mamh_truoc:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Môn học chính và Môn tiên quyết.")
                return None, None

            # Tra cứu ID thật từ map
            mamh = self.mamh_data_map.get(display_mamh)
            mamh_truoc = self.mamh_data_map.get(display_mamh_truoc)

            if mamh is None or mamh_truoc is None:
                messagebox.showwarning("Lỗi Dữ Liệu", "Môn học được chọn không hợp lệ (không tìm thấy ID).")
                return None, None
            
            # Kiểm tra logic
            if mamh == mamh_truoc:
                messagebox.showwarning("Lỗi Logic", "Môn học không thể là tiên quyết của chính nó.")
                return None, None
                
            return mamh, mamh_truoc
            
        except KeyError as e:
            messagebox.showerror("Lỗi", f"Lỗi truy cập ComboBox '{e}'."); return None, None

    def handle_add_prerequisite(self):
        mamh, mamh_truoc = self._get_and_validate_dkien_data()
        
        if mamh is None: 
            return
            
        try:
            self.db_manager.add_prerequisite(mamh, mamh_truoc)
            messagebox.showinfo("Thành công", f"Đã thêm ràng buộc: {mamh_truoc} -> {mamh}")
            self.load_all_data()
            
        except pyodbc.IntegrityError as e:
            error_message = str(e)
            if "PRIMARY KEY" in error_message or "UNIQUE constraint" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", f"Ràng buộc này ( {mamh_truoc} -> {mamh} ) đã tồn tại.")
            elif "FOREIGN KEY" in error_message:
                messagebox.showwarning("Lỗi Dữ Liệu", "Mã môn học không tồn tại trong bảng MHOC.")
            else:
                messagebox.showwarning("Lỗi Toàn Vẹn", f"Lỗi: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi Thêm Mới", f"Lỗi không xác định khi thêm điều kiện: {e}")

    def handle_delete_prerequisite(self):
        # Lấy dữ liệu từ ComboBox (đã được điền bằng cách click vào Treeview)
        mamh, mamh_truoc = self._get_and_validate_dkien_data()
        
        if mamh is None:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một ràng buộc từ bảng bên dưới để xóa.")
            return

        if not messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa ràng buộc:\n\n{mamh_truoc} là tiên quyết của {mamh}?"):
            return
            
        try:
            self.db_manager.delete_prerequisite(mamh, mamh_truoc)
            messagebox.showinfo("Thành công", f"Đã xóa ràng buộc: {mamh_truoc} -> {mamh}")
            self.load_all_data()
            
        except ValueError as e: # Lỗi "Không tìm thấy" từ db_manager
            messagebox.showwarning("Lỗi Xóa", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi Xóa", f"Lỗi không xác định khi xóa điều kiện: {e}")