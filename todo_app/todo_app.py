import reflex as rx
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


class State(rx.State):
    """This is state"""

    tasks: list[dict] = []

    show_new_form: bool = False
    new_label: str = ""
    hovered_task_id: int = -1
    is_loading: bool = False
    editing_task: dict | None = None

    def fetch_tasks(self):
        self.tasks = []
        try:
            self.is_loading = True
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT ID, Title, IsCompleted FROM Tasks ORDER BY CreatedAt DESC"
                )
                rows = cursor.fetchall()
                for row in rows:
                    self.tasks.append(
                        {
                            "id": row.ID,
                            "title": row.Title,
                            "is_completed": bool(row.IsCompleted),
                        }
                    )
        except Exception as e:
            print(f"Lỗi khi tải task {e}")
        finally:
            self.is_loading = False

    def toggle_complete(self, task: dict):
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                new_status = not task["is_completed"]
                cursor.execute(
                    "UPDATE Tasks SET IsCompleted = ? WHERE ID = ?",
                    new_status,
                    task["id"],
                )
                conn.commit()
            self.fetch_tasks()
        except Exception as e:
            print(f"Lỗi khi tải task {e}")

    def open_new_form(self):
        self.editing_task = None
        self.new_label = ""
        self.show_new_form = True

    def cancel_new_form(self):
        self.show_new_form = False
        self.new_label = ""
        self.editing_task = None

    def set_hovered_task(self, task_id: int):
        self.hovered_task_id = task_id

    def new_label_set(self, v: str):
        self.new_label = v

    def add_task(self):
        label = (self.new_label or "").strip()
        if not label:
            return

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Tasks (Title) VALUES (?)", label)
                conn.commit()
            self.cancel_new_form()
            self.fetch_tasks()
        except Exception as e:
            print(f"Lỗi khi tải task {e}")

    def delete_task(self, task_id: int):
        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Tasks WHERE ID = ?", task_id)
                conn.commit()
            self.fetch_tasks()
        except Exception as e:
            print(f"Lỗi khi tải task {e}")

    @rx.var
    def remaining_task(self) -> int:
        return sum(1 for task in self.tasks if not task["is_completed"])

    def start_editing(self, task: dict):
        self.editing_task = task

        self.new_label = task["title"]

        self.show_new_form = True

    def update_task(self):
        if self.editing_task is None:
            return

        new_title = (self.new_label or "").strip()
        if not new_title:
            return

        try:
            with pyodbc.connect(CONNECTION_STRING) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Tasks SET Title = ? WHERE ID = ?",
                    new_title,
                    self.editing_task["id"],
                )
                conn.commit()
            self.fetch_tasks()
        except Exception as e:
            print(f"Lỗi khi tải task {e}")
        finally:
            self.cancel_new_form()

    def save_task(self):
        if self.editing_task:
            self.update_task()
        else:
            self.add_task()


def task_row(task: dict) -> rx.Component:
    return rx.hstack(
        rx.checkbox(
            cursor="pointer",
            checked=task["is_completed"],
            on_change=lambda _: State.toggle_complete(task),
        ),
        rx.text(
            task["title"],
            text_decoration=rx.cond(task["is_completed"], "line-through", "none"),
            color=rx.cond(task["is_completed"], "gray", "black"),
        ),
        rx.spacer(),
        rx.cond(
            State.hovered_task_id == task["id"],
            rx.hstack(
                rx.icon(
                    "pencil",
                    cursor="pointer",
                    on_click=lambda: State.start_editing(task),
                ),
                rx.icon(
                    "trash",
                    cursor="pointer",
                    on_click=lambda: State.delete_task(task["id"]),
                ),
            ),
            rx.box(),
        ),
        width="100%",
        on_mouse_enter=lambda: State.set_hovered_task(task["id"]),
        on_mouse_leave=lambda: State.set_hovered_task(-1),
        key=task["id"],
    )


def add_new_task_form() -> rx.Component:
    return rx.fragment(
        rx.box(
            position="fixed",
            inset="0",
            background="rgba(0, 0, 0, 4)",
            z_index="1000",
            on_click=State.cancel_new_form,
        ),
        rx.box(
            rx.form(
                rx.vstack(
                    rx.heading(rx.cond(State.editing_task, "Edit task", "Add task")),
                    rx.input(
                        placeholder= rx.cond(State.editing_task, "Edit a task", "Add a task"),
                        value=State.new_label,
                        on_change=State.new_label_set,
                        auto_focus=True,
                    ),
                    rx.hstack(
                        rx.button(rx.cond(State.editing_task, "Update", "Add"), cursor="pointer", type="submit"),
                        rx.button(
                            "Cancel", on_click=State.cancel_new_form, cursor="pointer"
                        ),
                    ),
                ),
                on_submit=lambda _: State.save_task(),
            ),
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            padding="16px",
            z_index="1001",
            background_color="gray",
            box_shadow="0 10px 40px black",
        ),
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(rx.text(f"Remaining tasks: {State.remaining_task}")),
            rx.box(
                rx.heading("Website todo", size="6"),
                background="#AF7EEA",
                padding="8px 80px",
            ),
            rx.cond(
                State.is_loading,
                rx.center(rx.spinner(size="3")),
                rx.vstack(
                    rx.foreach(State.tasks, task_row),
                    width="100%",
                    background="white",
                    color="#9FA2AC",
                    padding="16px",
                    gap="12px",
                ),
            ),
            rx.box(
                rx.button(
                    "+ New task",
                    on_click=State.open_new_form,
                    background="#AF7EEA",
                    cursor="pointer",
                ),
                width="100%",
                text_align="center",
                cursor="pointer",
            ),
            rx.cond(State.show_new_form, add_new_task_form(), rx.fragment()),
        ),
        height="100vh",
        on_mount=State.fetch_tasks,
    )


app = rx.App()
app.add_page(index)
