import customtkinter as ctk

# --- Màu sắc (Kết hợp từ login_view.py và main_app.py) ---
# Dùng cho LoginView
COLOR_DARK_BLUE = "#0f1e3f"
COLOR_LIGHT_GOLD = "#cdaa80"
COLOR_DARK_GOLD = "#997953"
COLOR_WHITE = "#FFFFFF"

# Dùng cho MainApp (Tên nhất quán)
APP_DARK_BLUE = "#142143"
APP_YELLOW = "#ffaf00"
APP_LIGHT_GREY = "#e4e4e4" # Dùng cho text trên nền tối
APP_MID_BLUE = "#1a5d94"
APP_HOVER_YELLOW = "#EAA000"
APP_RED_DELETE = "#D32F2F"
APP_RED_DELETE_HOVER = "#B71C1C"


# --- Fonts ---
FONT_BOLD_DEFAULT = ("Segoe UI", 13, "bold")
FONT_NORMAL_DEFAULT = ("Segoe UI", 13)
FONT_BOLD_TITLE_APP = ("Segoe UI", 27, "bold")

FONT_LOGIN_TITLE = ("Segoe UI", 25, "bold")
FONT_LOGIN_LABEL = ("Segoe UI", 15, "bold")
FONT_LOGIN_ENTRY = ("Segoe UI", 15, "bold")
FONT_LOGIN_BUTTON = ("Segoe UI", 15, "bold")

FONT_NORMAL_TREEVIEW = ("Segoe UI", 11)
FONT_BOLD_TREEVIEW_HEADING = ("Segoe UI", 11, "bold")


# --- Widget Styles (Dùng cho nguyên tắc DRY trong các Tab) ---

# Style cho các ô nhập liệu (Entry) trong MainApp
APP_ENTRY_STYLE = {
    "border_color": APP_YELLOW,
    "fg_color": COLOR_WHITE,
    "text_color": APP_DARK_BLUE
}

# Style cho các Label (chữ trắng/xám trên nền xanh đậm)
APP_LABEL_STYLE = {
    "font": FONT_BOLD_DEFAULT,
    "text_color": APP_LIGHT_GREY
}

# Style cho các Nút màu vàng
APP_BUTTON_STYLE_YELLOW = {
    "font": FONT_BOLD_DEFAULT,
    "fg_color": APP_YELLOW,
    "hover_color": APP_HOVER_YELLOW,
    "text_color": COLOR_WHITE # Đổi text sang màu trắng cho dễ đọc
}

# Style cho các Nút Xóa (màu đỏ)
APP_BUTTON_STYLE_RED = {
    "font": FONT_BOLD_DEFAULT,
    "fg_color": APP_RED_DELETE,
    "hover_color": APP_RED_DELETE_HOVER,
    "text_color": COLOR_WHITE
}

# Style cho ComboBox
APP_COMBOBOX_STYLE = {
    "border_color": APP_YELLOW,
    "fg_color": COLOR_WHITE,
    "text_color": APP_DARK_BLUE,
    "dropdown_fg_color": COLOR_WHITE,
    "button_color": APP_YELLOW,
    "dropdown_hover_color": APP_HOVER_YELLOW,
    "state": 'readonly'
}