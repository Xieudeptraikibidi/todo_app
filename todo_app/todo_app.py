# --- 1. KHAI BÁO CÁC THƯ VIỆN VÀ CÀI ĐẶT BAN ĐẦU ---

import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv
from rxconfig import config

# Tải các biến môi trường từ file .env (chứa chuỗi kết nối)
load_dotenv()
# Lấy chuỗi kết nối từ biến môi trường đã được tải
CONNECTION_STRING = os.getenv("DATABASE_URL")


# --- 2. LỚP STATE: QUẢN LÝ TOÀN BỘ TRẠNG THÁI VÀ LOGIC ---




# --- 4. TRANG CHÍNH CỦA ỨNG DỤNG ---

def index() -> rx.Component:
    """Trang chính của ứng dụng, nơi lắp ráp tất cả các component lại."""
    

# Tạo một đối tượng ứng dụng
app = rx.App()
# Thêm trang index vào ứng dụng
app.add_page(index)