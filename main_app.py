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
        self.geometry("900x600")
        
        # Đảm bảo kết nối được đóng khi cửa sổ bị đóng
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.config(background="#FFFFFF")

        style = ttk.Style()
        style.theme_use('clam')

        #ĐẶT MÀU NỀN CỦA TAB (khi chưa được chọn)
        style.configure('TNotebook.Tab', background='#D0D0D0', foreground='black') 

        #ĐẶT MÀU NỀN CHO KHU VỰC NOTEBOOK (Màu nền chung)
        style.configure('TNotebook', background="#2F7AEA")

        # Tab sẽ có màu trắng khi nó ở trạng thái 'selected'
        style.map('TNotebook.Tab', 
                       background=[('selected', '#FFFFFF'),  # Khi trạng thái là 'selected', dùng màu trắng
                                   ('active', 'lightgray')], # Khi chuột di chuyển qua (active), dùng màu xám nhạt
                       foreground=[('selected', 'black')])

        self.label_Title = ttk.Label(self, text="PHẦN MỀM QUẢN LÝ SINH VIÊN")
        self.label_Title.pack(side='top',padx=5,pady=20, anchor="center")
        self.label_Title.config(font=("Segoe UI", 20, 'bold'), foreground="#032E5B", background="#FFFFFF")

        self._setup_tabs()
        

    def _on_closing(self):
        """Đóng kết nối database an toàn khi ứng dụng thoát."""
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát ứng dụng?"):
            self.db_manager.disconnect()
            self.master.destroy() # Hủy cửa sổ gốc (nếu có)
            self.destroy()

    def _configure_tab_colors(self):
    #Cấu hình màu nền cho các Tab trong Notebook
    
    # Màu nền chung của khu vực Notebook (nằm ngoài các tab mục)
        self.style.configure('TNotebook', background='#EFEFEF') 
    
    #  Cấu hình màu nền mặc định cho Tab (khi chưa được chọn)
        self.style.configure('TNotebook.Tab', 
                         background='#D0D0D0', # Màu xám nhạt cho tab không hoạt động
                         foreground='black') 

    #  Sử dụng map() để thay đổi màu khi Tab được chọn (Selected)
        self.style.map('TNotebook.Tab', 
                   # Quy tắc 1: Khi trạng thái là 'selected', màu nền là Trắng (#FFFFFF)
                   background=[('selected', '#FFFFFF')], 
                   
                   # Quy tắc 2: Đảm bảo văn bản trên tab được chọn có màu đen
                   foreground=[('selected', 'black')])

    
    def _setup_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        # --- Tạo từng tab ---
        self.tab_sinhvien = ttk.Frame(notebook)
        self.tab_mohoc = ttk.Frame(notebook)
        self.tab_bangdiem = ttk.Frame(notebook)

        # --- Thêm tab vào notebook ---
        notebook.add(self.tab_sinhvien, text="Sinh viên")
        notebook.add(self.tab_mohoc, text="Môn học")
        notebook.add(self.tab_bangdiem, text="Bàng điểm")

         # --- Gọi setup cho từng tab ---
        self._setup_layout_sinhvien(self.tab_sinhvien)
        #self._setup_tab_khoa(self.tab_mohoc)
        #self._setup_tab_thongke(self.tab_bangdiem)

    def _setup_layout_sinhvien(self,parent):
        style = ttk.Style()
        style.configure('Custom.TFrame',background="#9CE6FB")

        self.input_frame = ttk.LabelFrame(parent, text="Thông Tin Sinh Viên",style='Custom.TFrame') 
        self.input_frame.pack(padx=10, pady=10, fill="x")

        #Frame cho bảng Treeview
        tree_frame = ttk.Frame(parent)
        # Đây là lệnh pack đúng để Treeview chiếm toàn bộ không gian còn lại
        tree_frame.pack(padx=5, pady=10, fill="both", expand=True)
        self.tree_frame = tree_frame

        
        # Lệnh gọi hàm phải được đặt ở đây để các Frame self.input_frame và self.tree_frame tồn tại
        self._setup_input_fields()
        self._setup_student_treeview()
        self.load_students()
        
    def _setup_input_fields(self):
        """Tạo các nhãn và ô nhập liệu."""
        input_frame = self.input_frame 

        # 1. Khởi tạo dictionary để lưu trữ Entry widgets
        self.entries = {}
        
        # --- HÀNG 0: MSSV ---
        ttk.Label(input_frame, text="MSSV", font=("Arial", 12, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_masv = ttk.Entry(input_frame, width=15)
        entry_masv.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.entries['masv'] = entry_masv # 🔑 LƯU TRỮ

        # --- HÀNG 1: HỌ VÀ TÊN ---
        ttk.Label(input_frame, text="Họ và tên", font=("Arial", 12, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_ten = ttk.Entry(input_frame, width=30)
        entry_ten.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entries['ten'] = entry_ten # 🔑 LƯU TRỮ

        # --- HÀNG 2 (Cột 0, 1): NĂM ---
        ttk.Label(input_frame, text="Năm", font=("Arial", 12, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_nam = ttk.Entry(input_frame, width=8)
        entry_nam.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.entries['nam'] = entry_nam # 🔑 LƯU TRỮ

        # --- HÀNG 2 (Cột 2, 3): KHOA ---
        # Đã chuyển nhãn Khoa sang cột 2 để tránh bị đè lên ô nhập Năm.
        ttk.Label(input_frame, text="Khoa", font=("Arial", 12, 'bold')).grid(row=2, column=2, padx=10, pady=5, sticky="w") 
        entry_khoa = ttk.Entry(input_frame, width=15)
        entry_khoa.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.entries['khoa'] = entry_khoa # 🔑 LƯU TRỮ

        ttk.Button(input_frame, text="Thêm SV", command=self.handle_add_student).grid(row=3, column=0, padx=10, pady=5, sticky="w") 
        ttk.Button(input_frame, text="Xóa SV", command=self.handle_delete_student).grid(row=3, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(input_frame, text="Làm Mới", command=self.load_students).grid(row=3, column=2, padx=10, pady=5, sticky="w")

        # Đảm bảo các cột trống phía sau mở rộng (chú ý cột cuối cùng là cột 4)
        input_frame.grid_columnconfigure(4, weight=1)

        

    def _setup_student_treeview(self):
        """Thiết lập widget hiển thị bảng dữ liệu (Treeview)."""
        columns = ("MASV", "TEN", "NAM", "KHOA")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')

        # Thêm đoạn này để ẩn cột #0 nếu bạn chưa làm
        self.tree.column('#0', width=0, stretch=False)
        
        # Thiết lập tiêu đề cột
        self.tree.heading("MASV", text="Mã SV")
        self.tree.heading("TEN", text="Họ Tên")
        self.tree.heading("NAM", text="Năm")
        self.tree.heading("KHOA", text="Khoa")

        # Thiết lập chiều rộng cột (tùy chọn)
        self.tree.column("MASV", width=40, anchor=tk.CENTER)
        self.tree.column("TEN", width=150, anchor=tk.W)
        self.tree.column("NAM", width=50, anchor=tk.CENTER)
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
        try:
            # ✅ SỬA LỖI CÚ PHÁP: Truy cập bằng khóa dictionary (ví dụ: self.entries['masv'])
            masv = self.entries['masv'].get().strip().upper()
            ten = self.entries['ten'].get().strip()
            nam_str = self.entries['nam'].get().strip()
            khoa = self.entries['khoa'].get().strip()
        except KeyError as e:
            # Bắt lỗi nếu các Entry fields chưa được tạo hoặc được truy cập sai
            messagebox.showerror("Lỗi Cấu hình", f"Lỗi truy cập Entry field {e}. Vui lòng kiểm tra lại tên khóa.")
            return
            
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