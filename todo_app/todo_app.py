import reflex as rx

from rxconfig import config


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.heading('Website todo', size = '8'),
                padding = '12px',
                background_color = '#AF7EEA',
                border_radius = '8px',
            ),
            
            rx.vstack(
                rx.hstack(
                    rx.checkbox(
                        name = 'checkbox',
                        label = 'Ex 1'
                    ),
                    rx.text('Ex 1'),
                    width = '100%',
                    align = 'center',
                    text_align = 'center',
                    margin = '0 12px'
                ),
                
                rx.hstack(
                    rx.hstack(
                        rx.checkbox(
                        name = 'checkbox',
                        label = 'Ex 2'
                    ),
                    rx.text('Ex 2'),
                    ),
                    rx.icon('trash', margin_right = '12px'),
                    width = '100%',
                    justify='between',
                    align = 'center',
                    margin = '0 12px'
                ),
                
                rx.hstack(
                    rx.checkbox(
                        name = 'checkbox',
                        label = 'Ex 3'
                    ),
                    rx.text('Ex 3'),
                    width = '100%',
                    align = 'center',
                    text_align = 'center',
                    margin = '0 12px'
                ),
                
                width = '100%',
                border = '1px solid gray',
                border_radius = '12px',
                padding = '12px'
            ),
            
            rx.box(
                rx.button('+ New task', background_color ='#AF7EEA', padding = '12px'),
                width = '100%',
                text_align = 'center',
            ),
        ),
        height = '100vh'
    )


app = rx.App()
app.add_page(index)