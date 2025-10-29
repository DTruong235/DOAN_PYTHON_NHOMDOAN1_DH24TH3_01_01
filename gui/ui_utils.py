import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from constants import (
    COLOR_WHITE, APP_YELLOW, APP_DARK_BLUE, 
    FONT_NORMAL_TREEVIEW, FONT_BOLD_TREEVIEW_HEADING
)

def setup_themed_treeview(parent_frame, columns_config, style_name="Custom.Treeview"):
    """
    Tạo và cấu hình style cho một ttk.Treeview dùng chung.
    
    Args:
        parent_frame (ctk.CTkFrame): Frame cha chứa Treeview (đã có màu nền).
        columns_config (dict): Dict cấu hình cột, ví dụ: {"ID": "Tên Hiển Thị", ...}
        style_name (str): Tên style duy nhất cho Treeview này.

    Returns:
        ttk.Treeview: Đối tượng Treeview đã được tạo.
    """
    style = ttk.Style()
    style.theme_use("clam") # Rất quan trọng

    try:
        header_bg = ctk.ThemeManager.theme["CTkButton"]["fg_color"][0]
        header_active_bg = ctk.ThemeManager.theme["CTkButton"]["fg_color"][1]
    except (KeyError, IndexError):
        header_bg = APP_DARK_BLUE
        header_active_bg = APP_DARK_BLUE

    # Cấu hình style
    style.configure(f"{style_name}",
                    background=COLOR_WHITE,
                    fieldbackground=COLOR_WHITE,
                    foreground="black",
                    rowheight=28,
                    relief="flat",
                    font=FONT_NORMAL_TREEVIEW)

    style.configure(f"{style_name}.Heading",
                    background=header_bg,
                    foreground=COLOR_WHITE,
                    font=FONT_BOLD_TREEVIEW_HEADING,
                    relief="flat",
                    padding=(10, 5))

    style.map(f"{style_name}.Heading",
              background=[('active', header_active_bg)])
    
    style.map(f"{style_name}",
              background=[('selected', APP_YELLOW)],
              foreground=[('selected', APP_DARK_BLUE)])
    
    column_ids = tuple(columns_config.keys())
    
    tree = ttk.Treeview(
        parent_frame, 
        columns=column_ids, 
        show='headings', 
        style=f"{style_name}"
    )
    
    tree.column('#0', width=0, stretch=False)
    for col_id, heading_text in columns_config.items():
        tree.heading(col_id, text=heading_text, anchor='w') 

    # --- Setup Scrollbars (Dùng CTkScrollbar) ---
    scrollbar_y = ctk.CTkScrollbar(parent_frame, command=tree.yview)
    scrollbar_x = ctk.CTkScrollbar(parent_frame, command=tree.xview, orientation="horizontal")
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    tree.grid(row=0, column=0, sticky='nsew', padx=(5,0), pady=(5,0))
    scrollbar_y.grid(row=0, column=1, sticky='ns', padx=(0,5), pady=5)
    scrollbar_x.grid(row=1, column=0, sticky='ew', padx=5, pady=(0,5))
    
    # Cấu hình grid của frame cha (parent_frame)
    parent_frame.rowconfigure(0, weight=1)
    parent_frame.columnconfigure(0, weight=1)

    return tree