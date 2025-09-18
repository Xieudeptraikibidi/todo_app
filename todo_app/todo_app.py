import reflex as rx

from rxconfig import config


class State(rx.State):
    task = ["Ex1", 'Ex2', 'Ex3']
    hovered: int | None = None
    
    show_new_form: bool = False
    new_label: str = ''
    
    def set_hovered(self, i: int | None):
        self.hovered = i
        
    def delete_task(self, i: int):
        t = self.task.copy()
        t.pop(i)
        self.task = t
        
    def open_new_form(self):
        self.show_new_form = True
    
    def cancel_new_form(self):
        self.show_new_form = False
        self.new_label = ""
        
    def new_label_set (self, v: str):
        self.new_label = v

    def add_task(self):
        label = (self.new_label or "").strip()
        if not label:
            return
        t = self.task.copy()
        t.append(label)
        self.task = t
        
        self.new_label = ""
        self.show_new_form = False
        
def new_task_modal() -> rx.Component:
    return rx.fragment(
        rx.box(
            position="fixed",
            inset="0",
            background="rgba(0,0,0,0.4)",
            z_index="1000",
            on_click=State.cancel_new_form,
        ),
        rx.box(
            rx.form(
                rx.vstack(
                    rx.heading("Create a new task", size="5", color = 'white'),
                    rx.input(
                        placeholder="Nhập tên task…",
                        value=State.new_label,
                        on_change=State.new_label_set,
                        auto_focus=True,
                        width="100%",
                        color = 'white'
                    ),
                    rx.hstack(
                        rx.button("Cancel", variant="soft", on_click=State.cancel_new_form, cursor = 'pointer'),
                        rx.button("Add", type="submit", cursor = 'pointer'),
                        justify="end",
                        gap="8px",
                    ),
                    gap="12px",
                ),
                on_submit=lambda _: State.add_task(),
                width="100%",
            ),
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            background_color="#AF7EEA",
            padding="16px",
            border_radius="12px",
            box_shadow="0 10px 40px rgba(0,0,0,0.2)",
            width="90vw",
            max_width="480px",
            z_index="1001",
        ),
    )
        
def task_row(label: str, i: int) -> rx.Component:
    return rx.hstack(
        rx.checkbox(name=f"checkbox_{i}"),
        rx.text(label),
        
        rx.icon(
            'trash',
            margin_left='auto',
            display = rx.cond(State.hovered == i, 'block', 'none'),
            cursor = 'pointer',
            on_click = lambda: State.delete_task(i),
        ),
        width="100%",
        align="center",
        margin="0 12px",
        
        on_mouse_enter= lambda: State.set_hovered(i),
        on_mouse_leave= lambda: State.set_hovered(None),
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.heading("Website todo", size="8"),
                padding="12px",
                background_color="#AF7EEA",
                border_radius="8px",
            ),
            rx.vstack(
                rx.foreach(State.task, task_row),
                width="100%",
                border="1px solid gray",
                border_radius="12px",
                padding="12px",
            ),
            
            
            rx.box(
                rx.button("+ New task", background_color="#AF7EEA", padding="12px"),
                width="100%",
                text_align="center",
                on_click=State.open_new_form
            ),
            
            rx.cond(State.show_new_form, new_task_modal(), rx.fragment()),
        ),
        height="100vh",
    )


app = rx.App()
app.add_page(index)
