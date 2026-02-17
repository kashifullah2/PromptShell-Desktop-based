import flet as ft


class MessageBubble(ft.Container):
    def __init__(self, text: str, is_user: bool = False, is_error: bool = False):
        color = "#FFFFFF" if is_user else ("#FF6347" if is_error else "#CCCCCC")
        align = ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        bg_color = "#1E1E1E" if is_user else "#2D2D2D"
        
        super().__init__(
            content=ft.Text(
                text,
                color=color,
                size=14,
                font_family="JetBrainsMono",
                selectable=True,
            ),
            padding=10,
            border_radius=10,
            bgcolor=bg_color,
            margin=ft.margin.only(bottom=5),
            alignment=ft.Alignment(-1, 0) if not is_user else ft.Alignment(1, 0),
        )

class CommandCard(ft.Card):
    def __init__(self, command_nlp: str, command_shell: str, explanation: str, on_execute, on_copy):
        super().__init__(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Target: {command_nlp}", size=12, color="#888888"),
                    ft.Container(
                        content=ft.Text(command_shell, font_family="JetBrainsMono", color="#4EC9B0", size=16, weight="bold"),
                        padding=10,
                        bgcolor="#1E1E1E",
                        border_radius=5,
                    ),
                    ft.Text(explanation, size=13, italic=True, color="#AAAAAA"),
                    ft.Row([
                        ft.ElevatedButton("Execute", on_click=lambda _: on_execute(command_shell), icon="play_arrow", color="green"),
                        ft.IconButton(icon=ft.Icon("copy"), on_click=lambda _: on_copy(command_shell), tooltip="Copy to Clipboard"),
                    ])
                ], spacing=10),
                padding=15
            ),
            margin=ft.margin.only(bottom=10)
        )

class SettingsSidebar(ft.NavigationRail):
    def __init__(self, on_change_safe_mode, on_clear_history):
        super().__init__(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon="terminal", selected_icon="terminal_outlined", label="Terminal"
                ),
                ft.NavigationRailDestination(
                    icon="settings",
                    selected_icon="settings_outlined",
                    label="Settings",
                ),
            ],
            on_change=lambda e: print("Selected destination:", e.control.selected_index),
        )
        self.safe_mode_switch = ft.Switch(label="Safe Mode", value=True, on_change=on_change_safe_mode)
        self.clear_history_btn = ft.ElevatedButton("Clear History", on_click=on_clear_history, color="red")
