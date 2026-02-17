import flet as ft
from src.core.llm_engine import LLMEngine
from src.core.executor import CommandExecutor
from src.core.history import HistoryManager


class AppLayout:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PromptShell - Smart Terminal"
        self.page.bgcolor = "#0D1117"
        print("AppLayout init started...")

        # Core Engines
        try:
            self.llm = LLMEngine()
        except ValueError as e:
            self.page.add(ft.Text(f"Configuration Error: {e}", color="red"))
            return

        self.executor = CommandExecutor()
        self.history = HistoryManager("promptshell_history.json")
        self.safe_mode = True

        self.setup_ui()
        print("setup_ui completed.")

    def setup_ui(self):
        # Simplified UI for testing
        self.chat_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        
        # Input Area
        self.input_field = ft.TextField(
            hint_text="Describe your command (e.g., 'Find all python files')",
            expand=True,
            on_submit=self.handle_submit,
            border_radius=10,
            bgcolor="#161b22",
            border_color="#30363d"
        )
        
        self.send_btn = ft.IconButton(
            icon=ft.Icon("play_arrow", color="#58a6ff"), 
            on_click=self.handle_submit
        )

        # Main Layout - simplified
        main_content = ft.Column([
            self.chat_list,
            ft.Container(
                content=ft.Row([self.input_field, self.send_btn]),
                padding=10,
                bgcolor="#0D1117"
            )
        ], expand=True)

        self.page.add(main_content)
        
        # Add welcome message
        print("Adding welcome message...")
        self.chat_list.controls.append(
            ft.Text("Welcome to PromptShell!", color="#888888", italic=True, size=12)
        )
        self.page.update()

    def handle_submit(self, e):
        user_text = self.input_field.value
        if not user_text:
            return
        
        self.input_field.value = ""
        self.page.update()
        
        # Add user message
        self.chat_list.controls.append(
            ft.Container(
                content=ft.Text(user_text, color="#FFFFFF", size=14),
                padding=10,
                border_radius=10,
                bgcolor="#1E1E1E",
                margin=ft.margin.only(bottom=5)
            )
        )
        self.page.update()

        try:
            command_obj = self.llm.generate_command(user_text)
            
            # Save to history
            self.history.add_entry(user_text, command_obj.command_shell)
            
            # Display command
            self.chat_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Command: {command_obj.command_shell}", 
                               color="#4EC9B0", size=14),
                        ft.Text(f"Explanation: {command_obj.explanation}", 
                               color="#AAAAAA", size=12, italic=True),
                        ft.ElevatedButton(
                            "Execute", 
                            on_click=lambda _: self.execute_command(command_obj.command_shell),
                            color="green"
                        )
                    ], spacing=5),
                    padding=15,
                    border_radius=10,
                    bgcolor="#2D2D2D",
                    margin=ft.margin.only(bottom=10)
                )
            )
            self.page.update()
            
        except Exception as ex:
            self.chat_list.controls.append(
                ft.Text(f"Error: {str(ex)}", color="#FF6347", size=14)
            )
            self.page.update()

    def execute_command(self, command_shell):
        self.chat_list.controls.append(
            ft.Text(f"Executing: {command_shell}", color="#888888", italic=True, size=12)
        )
        self.page.update()
        
        stdout, stderr = self.executor.execute(command_shell)
        if stdout:
            self.chat_list.controls.append(
                ft.Text(stdout, color="#CCCCCC", size=14)
            )
        if stderr:
            self.chat_list.controls.append(
                ft.Text(stderr, color="#FF6347", size=14)
            )
        self.page.update()
