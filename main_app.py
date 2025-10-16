# main_app.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class MainApp(tk.Toplevel):
    def __init__(self, master, db_manager):
        # Sử dụng Toplevel để tạo cửa sổ chính sau khi cửa sổ đăng nhập đã bị ẩn/hủy
        super().__init__(master) 
        self.db_manager = db_manager
        self.title("Ứng Dụng Quản Lý Sinh Viên (QLSV) - MSSQL")
        self.geometry("900x550")
        
        # Đảm bảo kết nối được đóng khi cửa sổ bị đóng
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._setup_layout()
        self._setup_student_treeview()
        self._setup_input_fields()
        self.load_students()

    def _on_closing(self):
        """Đóng kết nối database an toàn khi ứng dụng thoát."""
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát ứng dụng?"):
            self.db_manager.disconnect()
            self.master.destroy() # Hủy cửa sổ gốc (nếu có)
            self.destroy()


    def _setup_layout(self):
        """Thiết lập khung giao diện (Grid/Frame)."""
        # Frame cho các trường nhập liệu và nút chức năng
        # Gán Frame vào self.input_frame để sử dụng sau này
        self.input_frame = ttk.LabelFrame(self, text="Thông Tin Sinh Viên") 
        self.input_frame.pack(padx=10, pady=10, fill="x")

        # Frame cho bảng Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.tree_frame = tree_frame

   
    def _setup_input_fields(self):
        """Tạo các nhãn và ô nhập liệu."""
        labels = ""# Giả định labels đã được định nghĩa
        self.entries = {}
        # Dùng đối tượng Frame đã được lưu
        input_frame = self.input_frame 

        for i, text in enumerate(labels):
            #... (Phần tạo Label và Entry)
            ttk.Label(input_frame, text=text).grid(row=0, column=i*2, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(input_frame, width=15)
            entry.grid(row=0, column=i*2 + 1, padx=5, pady=5, sticky="ew")
            self.entries[text.replace(":", "")] = entry

        # Nút chức năng
        # Bây giờ input_frame là đối tượng LabelFrame hợp lệ
        ttk.Button(input_frame, text="Thêm SV", command=self.handle_add_student).grid(row=1, column=0, padx=5, pady=10)
        ttk.Button(input_frame, text="Xóa SV", command=self.handle_delete_student).grid(row=1, column=2, padx=5, pady=10)
        ttk.Button(input_frame, text="Làm Mới", command=self.load_students).grid(row=1, column=4, padx=5, pady=10)
        #...
        # Thêm nút Sửa và Tìm kiếm sau

    def _setup_student_treeview(self):
        """Thiết lập widget hiển thị bảng dữ liệu (Treeview)."""
        columns = ("MASV", "TEN", "NAM", "KHOA")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')
        
        # Thiết lập tiêu đề cột
        self.tree.heading("MASV", text="Mã SV")
        self.tree.heading("TEN", text="Họ Tên")
        self.tree.heading("NAM", text="Năm")
        self.tree.heading("KHOA", text="Khoa")

        # Thiết lập chiều rộng cột (tùy chọn)
        self.tree.column("MASV", width=80, anchor=tk.CENTER)
        self.tree.column("TEN", width=200, anchor=tk.W)
        self.tree.column("NAM", width=80, anchor=tk.CENTER)
        self.tree.column("KHOA", width=100, anchor=tk.CENTER)
        
        # Thêm Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    # --- HANDLERS (Xử lý sự kiện) ---
    def load_students(self):
        """Tải và hiển thị dữ liệu sinh viên."""
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Lấy dữ liệu từ DB_Manager
        columns, students = self.db_manager.fetch_all_students() 
        
        # Chèn dữ liệu mới
        for student in students:
            # student là một tuple (MASV, TEN, NAM, KHOA)
            self.tree.insert("", tk.END, values=student)
            
    def handle_add_student(self):
        """Thu thập dữ liệu và gọi hàm thêm sinh viên."""
        # Lấy dữ liệu từ các Entry field
        masv = self.entries.get().strip().upper()
        ten = self.entries.get().strip()
        nam_str = self.entries.get().strip()
        khoa = self.entries["Khoa"].get().strip()

        # Kiểm tra dữ liệu đầu vào cơ bản
        if not masv or not ten or not nam_str:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đủ Mã SV, Họ Tên và Năm Sinh.")
            return

        try:
            nam = int(nam_str)
        except ValueError:
            messagebox.showwarning("Lỗi dữ liệu", "Năm Sinh phải là số nguyên.")
            return

        # Gọi hàm thêm từ DB_Manager
        if self.db_manager.add_student(masv, ten, nam, khoa):
            messagebox.showinfo("Thành công", f"Đã thêm sinh viên {ten} ({masv}).")
            self.load_students() # Cập nhật Treeview
            self._clear_entries()

    def handle_delete_student(self):
        """Xử lý việc xóa sinh viên được chọn."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lựa chọn", "Vui lòng chọn một sinh viên trong danh sách để xóa.")
            return

        # Lấy giá trị của hàng được chọn (values là MASV)
        masv_to_delete = self.tree.item(selected_item, 'values')

        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa sinh viên {masv_to_delete}?"):
            if self.db_manager.delete_student(masv_to_delete):
                messagebox.showinfo("Thành công", f"Đã xóa sinh viên {masv_to_delete}.")
                self.load_students() # Cập nhật Treeview
                
    def _clear_entries(self):
        """Xóa nội dung trong các ô nhập liệu."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)