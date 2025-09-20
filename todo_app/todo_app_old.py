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

class State(rx.State):
    """Lớp State quản lý toàn bộ trạng thái và logic của ứng dụng."""
    
    # Biến lưu trữ danh sách công việc lấy từ database.
    # Mỗi công việc là một dictionary, ví dụ: {"id": 1, "title": "Học Reflex", "is_completed": False}
    tasks: list[dict] = []
    
    # Biến theo dõi ID của task đang được di chuột qua để hiển thị icon xóa.
    hovered_task_id: int = -1
    # Biến kiểm soát việc hiển thị modal (hộp thoại) thêm task mới.
    show_new_form: bool = False
    # Biến lưu trữ nội dung của ô input trong modal thêm task.
    new_label: str = ""
    
    # --- CÁC HÀM TƯƠNG TÁC VỚI DATABASE ---

    def fetch_tasks(self):
        """Tải tất cả công việc từ SQL Server và cập nhật State."""
        self.tasks = []  # Xóa danh sách cũ để làm mới
        try:
            # Dùng `with` để đảm bảo kết nối được đóng lại an toàn sau khi dùng
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Thực thi câu lệnh SQL để lấy dữ liệu
                cursor.execute("SELECT ID, Title, IsCompleted FROM Tasks ORDER BY CreatedAt DESC")
                rows = cursor.fetchall()
                # Duyệt qua từng dòng kết quả và thêm vào danh sách `tasks`
                for row in rows:
                    self.tasks.append(
                        {
                            "id": row.ID,
                            "title": row.Title,
                            "is_completed": row.IsCompleted,
                        }
                    )
        except Exception as e:
            # In ra lỗi nếu có sự cố kết nối hoặc truy vấn
            print(f"Lỗi khi tải tasks: {e}")
    
    def set_hovered_task(self, task_id: int | None):
        """Cập nhật ID của task đang được hover."""
        self.hovered_task_id = task_id
        
    def delete_task(self, task_id: int):
        """Xóa một công việc khỏi DB dựa trên ID."""
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Dùng `?` để tránh lỗi SQL Injection, an toàn hơn
                cursor.execute("DELETE FROM Tasks WHERE ID = ?", task_id)
                conn.commit()  # commit() để xác nhận và lưu thay đổi vào DB
            self.fetch_tasks() # Tải lại danh sách để cập nhật giao diện
        except Exception as e:
            print(f"Lỗi khi xóa task: {e}")

    def add_task(self):
        """Thêm một công việc mới vào DB."""
        label = (self.new_label or "").strip() # Lấy và làm sạch dữ liệu từ input
        if not label: # Nếu input rỗng thì không làm gì cả
            return
        
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Tasks (Title) VALUES (?)", label)
                conn.commit()
            self.cancel_new_form() # Đóng form sau khi thêm thành công
            self.fetch_tasks()     # Tải lại danh sách
        except Exception as e:
            print(f"Lỗi khi thêm task: {e}")
            
    def toggle_complete(self, task: dict):
        """Cập nhật trạng thái hoàn thành của một công việc."""
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                # Lật ngược trạng thái hiện tại (True -> False, False -> True)
                new_status = not task["is_completed"]
                cursor.execute("UPDATE Tasks SET IsCompleted = ? WHERE ID = ?", new_status, task["id"])
                conn.commit()
            self.fetch_tasks() # Tải lại danh sách
        except Exception as e:
            print(f"Lỗi khi cập nhật task: {e}")

    # --- CÁC HÀM QUẢN LÝ TRẠNG THÁI GIAO DIỆN ---

    def open_new_form(self):
        """Mở modal thêm task."""
        self.show_new_form = True
    
    def cancel_new_form(self):
        """Đóng và reset modal thêm task."""
        self.show_new_form = False
        self.new_label = ""
        
    def new_label_set (self, v: str):
        """Cập nhật giá trị cho ô input trong modal."""
        self.new_label = v


# --- 3. CÁC COMPONENT GIAO DIỆN (UI) ---

def new_task_modal() -> rx.Component:
    """Component cho modal (hộp thoại) thêm task mới."""
    # rx.fragment dùng để nhóm các component lại mà không tạo thêm thẻ HTML thừa
    return rx.fragment(
        # Lớp phủ màu đen mờ phía sau
        rx.box(
            position="fixed", inset="0", background="rgba(0,0,0,0.4)",
            z_index="1000", on_click=State.cancel_new_form,
        ),
        # Hộp thoại nội dung chính
        rx.box(
            rx.form(
                rx.vstack(
                    rx.heading("Create a new task", size="5"),
                    rx.input(
                        placeholder="Nhập tên task…", value=State.new_label,
                        on_change=State.new_label_set, auto_focus=True, width="100%",
                    ),
                    rx.hstack(
                        rx.button("Cancel", variant="soft", on_click=State.cancel_new_form, cursor='pointer'),
                        rx.button("Add", type="submit", cursor='pointer'),
                        justify="end", gap="8px",
                    ),
                    gap="12px",
                ),
                on_submit=lambda _: State.add_task(), width="100%",
            ),
            # Các thuộc tính CSS để căn giữa và tạo kiểu cho modal
            position="fixed", top="50%", left="50%", transform="translate(-50%, -50%)",
            background="#AF7EEA", padding="16px", border_radius="12px",
            box_shadow="0 10px 40px rgba(0,0,0,0.2)", width="90vw",
            max_width="480px", z_index="1001",
        ),
    )
    
def task_row(task: dict) -> rx.Component:
    """Component render một dòng công việc trong danh sách."""
    return rx.hstack(
        rx.checkbox(
            is_checked=task["is_completed"],
            on_change=lambda _: State.toggle_complete(task),
        ),
        rx.text(task["title"]),
        rx.spacer(), # Dùng để đẩy icon xóa về cuối dòng
        # Hiển thị icon xóa một cách có điều kiện
        rx.cond(
            State.hovered_task_id == task["id"], # Chỉ hiện khi ID task này đang được hover
            rx.icon(
                'trash', cursor='pointer',
                on_click=lambda: State.delete_task(task["id"]), # Sự kiện xóa
            ),
            rx.box(), # Nếu không hover thì không hiện gì
        ),
        width="100%", align="center", padding="0 12px",
        # Gắn sự kiện hover cho cả dòng
        on_mouse_enter=lambda: State.set_hovered_task(task["id"]),
        on_mouse_leave=lambda: State.set_hovered_task(-1),
        # key: Cung cấp một định danh duy nhất cho mỗi dòng, giúp Reflex cập nhật giao diện chính xác
        key=task["id"],
    )


# --- 4. TRANG CHÍNH CỦA ỨNG DỤNG ---

def index() -> rx.Component:
    """Trang chính của ứng dụng, nơi lắp ráp tất cả các component lại."""
    return rx.center(
        rx.vstack(
            # Tiêu đề chính
            rx.box(
                rx.heading("Website todo", size="8"), padding="12px",
                background_color="#AF7EEA", border_radius="8px",
                width = '100%', text_align = 'center'
            ),
            # Danh sách các công việc
            rx.vstack(
                rx.foreach(State.tasks, task_row), # Dùng rx.foreach để render từng task_row
                width="100%", border="1px solid gray", border_radius="12px",
                padding="12px 0", spacing="3",
            ),
            # Nút "Add new task"
            rx.box(
                rx.button("+ New task", background_color="#AF7EEA", padding="12px", on_click=State.open_new_form),
                width="100%", text_align="center",
            ),
            # Hiển thị modal một cách có điều kiện
            rx.cond(State.show_new_form, new_task_modal(), rx.fragment()),
            spacing="5", width="400px",
        ),
        height="100vh",
        # Khi trang được tải lần đầu, gọi hàm fetch_tasks để lấy dữ liệu từ DB
        on_mount=State.fetch_tasks,
    )


# --- 5. KHỞI TẠO VÀ CHẠY ỨNG DỤNG ---

# Tạo một đối tượng ứng dụng
app = rx.App()
# Thêm trang index vào ứng dụng
app.add_page(index)