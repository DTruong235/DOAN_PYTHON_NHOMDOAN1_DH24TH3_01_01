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
        style.configure('Custom.TFrame',background="#D1D3D4")

        self.input_frame = ttk.LabelFrame(parent, text="Thông Tin Sinh Viên",style='Custom.TFrame') 
        self.input_frame.pack(padx=10, pady=10, fill="x")

        #Frame cho thanh tìm kiếm
        self.search_bar_frame = ttk.Frame(parent)
        self.search_bar_frame.pack(padx=100, pady=5, fill="x")

        #Frame cho bảng Treeview
        tree_frame = ttk.Frame(parent)
        
        tree_frame.pack(padx=5, pady=10, fill="both", expand=True)
        self.tree_frame = tree_frame

        
        self._setup_input_fields()
        self._setup_student_treeview()
        self.load_students()
        
        
    def _setup_input_fields(self):
        """Tạo các nhãn và ô nhập liệu."""
        input_frame = self.input_frame 

        # 1. Khởi tạo dictionary để lưu trữ Entry widgets
        self.entries = {}
        
        # ---MSSV ---
        ttk.Label(input_frame, text="MSSV", font=("Arial", 12, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_masv = ttk.Entry(input_frame, width=15)
        entry_masv.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entries['masv'] = entry_masv # 🔑 LƯU TRỮ

        # --- HỌ VÀ TÊN ---
        ttk.Label(input_frame, text="Họ và tên", font=("Arial", 12, 'bold')).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_ten = ttk.Entry(input_frame, width=30)
        entry_ten.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.entries['ten'] = entry_ten # 🔑 LƯU TRỮ

        # --- GIỚI TÍNH ---
        style = ttk.Style()
        style.configure('Custom.TRadiobutton',font=("Arial", 10, 'bold'))
        rad_gt = tk.StringVar(value="Nam")
        ttk.Label(input_frame, text="Giới tính", font=("Arial", 12, 'bold')).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        rad_gtnam = ttk.Radiobutton(input_frame, text="Nam", value="Nam",variable=rad_gt,style='Custom.TRadiobutton')
        rad_gtnam.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        rad_gtnu = ttk.Radiobutton(input_frame, text="Nữ", value="Nu",variable=rad_gt,style='Custom.TRadiobutton')
        rad_gtnu.grid(row=3, column=1, padx=100, pady=5, sticky="w")

        self.entries['gioitinh'] = rad_gt # 🔑 LƯU TRỮ

         # --- NGÀY SINH ---
        ttk.Label(input_frame, text="Ngày sinh", font=("Arial", 12, 'bold')).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        entry_ngaysinh = ttk.Entry(input_frame, width=30)
        entry_ngaysinh.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.entries['ngaysinh'] = entry_ngaysinh # 🔑 LƯU TRỮ

        # --- ĐỊA CHỈ ---
        ttk.Label(input_frame, text="Địa chỉ", font=("Arial", 12, 'bold')).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        entry_diachi = ttk.Entry(input_frame, width=30)
        entry_diachi.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entries['diachi'] = entry_diachi # 🔑 LƯU TRỮ

        # --- KHÓA HỌC ---
        ttk.Label(input_frame, text="Khóa học", font=("Arial", 12, 'bold')).grid(row=2, column=2, padx=5, pady=5, sticky="w")
        entry_khoahoc = ttk.Entry(input_frame, width=8)
        entry_khoahoc.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.entries['khoahoc'] = entry_khoahoc # 🔑 LƯU TRỮ

        # --- KHOA ---
        # Đã chuyển nhãn Khoa sang cột 2 để tránh bị đè lên ô nhập Năm.
        ttk.Label(input_frame, text="Khoa", font=("Arial", 12, 'bold')).grid(row=3, column=2, padx=5, pady=5, sticky="w") 
        entry_khoa = ttk.Entry(input_frame, width=15)
        entry_khoa.grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.entries['khoa'] = entry_khoa # 🔑 LƯU TRỮ

         # --- EMAIL ---
        ttk.Label(input_frame, text="Email", font=("Arial", 12, 'bold')).grid(row=4, column=2, padx=5, pady=5, sticky="w")
        entry_email = ttk.Entry(input_frame, width=30)
        entry_email.grid(row=4, column=3, padx=5, pady=5, sticky="w")
        self.entries['email'] = entry_email # 🔑 LƯU TRỮ

        ttk.Button(input_frame, text="Thêm SV", command=self.handle_add_student).grid(row=1, column=5, padx=10, pady=5, sticky="w") 
        ttk.Button(input_frame, text="Xóa SV", command=self.handle_delete_student).grid(row=2, column=5, padx=10, pady=5, sticky="w")
        ttk.Button(input_frame, text="Làm Mới", command=self.load_students).grid(row=3, column=5, padx=10, pady=5, sticky="w")

        # Đảm bảo các cột trống phía sau mở rộng (chú ý cột cuối cùng là cột 4)
        input_frame.grid_columnconfigure(4, weight=1)

        search_frame = self.search_bar_frame # Container là Frame tìm kiếm mới
        ttk.Label(search_frame, text="Tìm kiếm Mã SV:", font=("Arial", 12, "bold","italic")).pack(side="left", padx=5)
        entry_search_masv = ttk.Entry(search_frame, width=30)
        entry_search_masv.pack(side="left", padx=5, fill="x", expand=True)
        self.entries['search_masv'] = entry_search_masv

        ttk.Button(search_frame, text="Tìm", command=self.handle_search_and_load).pack(side="left", padx=10)
        

    def _setup_student_treeview(self):
        """Thiết lập widget hiển thị bảng dữ liệu (Treeview)."""
        columns = ("MASV", "TEN", "GIOITINH","NGAYSINH","DIACHI","KHOAHOC", "KHOA","EMAIL")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')

        # Thêm đoạn này để ẩn cột #0 nếu bạn chưa làm
        self.tree.column('#0', width=0, stretch=False)
        
        # Thiết lập tiêu đề cột
        self.tree.heading("MASV", text="Mã SV")
        self.tree.heading("TEN", text="Họ Tên")
        self.tree.heading("GIOITINH", text="Giới tính")
        self.tree.heading("NGAYSINH", text="Ngày sinh")
        self.tree.heading("DIACHI", text="Địa chỉ")
        self.tree.heading("KHOAHOC", text="Khóa học")
        self.tree.heading("KHOA", text="Khoa")
        self.tree.heading("EMAIL", text="Email")

        # Thiết lập chiều rộng cột (tùy chọn)
        self.tree.column("MASV", width=40, anchor=tk.CENTER)
        self.tree.column("TEN", width=150, anchor=tk.W)
        self.tree.column("GIOITINH", width=50, anchor=tk.CENTER)
        self.tree.column("NGAYSINH", width=100, anchor=tk.W)
        self.tree.column("DIACHI", width=150, anchor=tk.W)
        self.tree.column("KHOAHOC", width=50, anchor=tk.CENTER)
        self.tree.column("KHOA", width=100, anchor=tk.CENTER)
        self.tree.column("EMAIL", width=150, anchor=tk.W)
        
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
            
            masv = self.entries['masv'].get().strip().upper()
            ten = self.entries['ten'].get().strip()
            gioitinh = self.entries['gioitinh'].get().strip()
            ngaysinh = self.entries['ngaysinh'].get().strip()
            diachi = self.entries['diachi'].get().strip()
            khoahoc_str = self.entries['khoahoc'].get().strip()
            khoa = self.entries['khoa'].get().strip()
            email = self.entries['email'].get().strip()
        except KeyError as e:
            # Bắt lỗi nếu các Entry fields chưa được tạo hoặc được truy cập sai
            messagebox.showerror("Lỗi Cấu hình", f"Lỗi truy cập Entry field {e}. Vui lòng kiểm tra lại tên khóa.")
            return
            
        # Kiểm tra dữ liệu đầu vào cơ bản
        if not masv or not ten or not khoahoc_str:
             messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đủ Mã SV, Họ Tên và Năm Sinh.")
             return

        try:
            khoahoc = int(khoahoc_str)
        except ValueError:
            messagebox.showwarning("Lỗi dữ liệu", "Khóa học phải là số nguyên.")
            return

        # Gọi hàm thêm từ DB_Manager
        if self.db_manager.add_student(masv,ten,gioitinh,ngaysinh,diachi,khoahoc,khoa,email):
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

    def handle_search_and_load(self):
        try:
            # 1. Thu thập đầu vào
            # Sử dụng khóa 'search_masv' như đã thiết lập trong _setup_input_fields
            search_keyword = self.entries['search_masv'].get().strip()

            # 2. Gọi Model để tìm kiếm
            # Hàm find_student() sẽ trả về tất cả sinh viên nếu search_keyword trống.
            # (Hàm find_student() phải được sửa lỗi cú pháp SQL và trả về: columns, students)
            
            # Khởi tạo students là rỗng để tránh lỗi nếu Model gặp sự cố
            columns, students = None,[] 
            
            # Gọi Model (DB_Manager)
            results = self.db_manager.find_student(search_keyword)

            if results and len(results) == 2:
                columns, students = results
            
            # 3. Cập nhật View (Treeview)
            
            # Xóa dữ liệu cũ khỏi Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not students:
                # Nếu không tìm thấy và ô tìm kiếm không trống
                if search_keyword:
                    messagebox.showinfo("Tìm kiếm", f"Không tìm thấy sinh viên nào khớp với '{search_keyword}'.")
                
                # Sau khi thông báo, nếu không tìm thấy gì, Treeview sẽ trống
                return

            # Chèn dữ liệu mới vào Treeview
            for student in students:
                # Mỗi 'student' là một tuple dữ liệu hàng (MASV, TEN, GIOITINH,...)
                self.tree.insert("", tk.END, values=student)
                
        except Exception as e:
            # Xử lý lỗi hệ thống hoặc lỗi khác (không phải lỗi DB đã được xử lý)
            messagebox.showerror("Lỗi Truy vấn Hệ thống", f"Đã xảy ra lỗi khi thực hiện tìm kiếm:\n{e}")