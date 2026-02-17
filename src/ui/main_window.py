import sys
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt, QThread, Signal

from src.ui.widgets.sidebar import ModernSidebar
from src.ui.widgets.terminal import TerminalWidget
from src.ui.widgets.history_view import HistoryWidget
from src.ui.widgets.settings_page import SettingsPage
from src.core.worker import CommandWorker
from src.ui.theme import ThemeManager
from src.core.config import settings

from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget

class PromptShellWindow(QMainWindow):
    theme_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptShell Professional")
        self.resize(1200, 800)
        
        # Initialize Core
        from src.core.llm_engine import LLMEngine
        from src.core.executor import CommandExecutor
        from src.core.history import CommandHistory
        
        self.llm_engine = LLMEngine()
        self.executor = CommandExecutor()
        self.history = CommandHistory()
        
        # UI Components
        self.sidebar = ModernSidebar()
        self.sidebar.setObjectName("sidebar")
        self.terminal = TerminalWidget()
        self.history_view = HistoryWidget(self.history)
        self.settings_page = SettingsPage()
        
        # Stack for main content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.terminal)      # Index 0
        self.stack.addWidget(self.history_view)  # Index 1
        self.stack.addWidget(self.settings_page) # Index 2
        
        self.setup_layout()
        self.connect_signals()
        
        # Apply theme
        self.apply_current_theme()

    def setup_layout(self):
        main_widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
    def connect_signals(self):
        self.sidebar.page_changed.connect(self.change_page)
        self.terminal.command_submitted.connect(self.process_command)
        self.history_view.command_selected.connect(self.terminal.input_field.setText)
        self.history_view.command_selected.connect(lambda: self.stack.setCurrentIndex(0))
        self.settings_page.settings_saved.connect(self.on_settings_saved)
        self.settings_page.theme_changed.connect(self.on_theme_changed)
        
    def apply_current_theme(self):
        """Apply the current theme from settings"""
        theme = settings.config.theme
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, theme)
    
    def on_theme_changed(self, theme: str):
        """Handle theme change from settings"""
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, theme)
        
    def change_page(self, index):
        self.stack.setCurrentIndex(index)
    
    def on_settings_saved(self):
        self.llm_engine.initialize()
        self.stack.setCurrentIndex(0)
            
    def process_command(self, text, task_type="command"):
        # 1. Generate Command via LLM (Threaded)
        self.terminal.append_output("Processing...", "#888")
        
        # Create worker
        self.worker = CommandWorker(text, self.llm_engine, task_type)
        self.worker.finished.connect(self.on_command_generated)
        self.worker.error.connect(self.on_error)
        
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
        
    def on_command_generated(self, result):
        import json
        
        if isinstance(result, (dict, list)):
            # Analyst Mode: Render Table
            self.terminal.append_output("Analysis Result:", "#10B981")
            html = self.format_html_table(result)
            self.terminal.output_area.append(html)
            
            # Add to history (store as text representation)
            self.history.add_entry("Analysis Task", "Data Table generated", success=True)
            
        elif isinstance(result, str):
            # Developer Mode: Render Code
            self.terminal.append_output("Generated Code:", "#10B981")
            # Escape HTML to prevent rendering
            import html as html_lib
            escaped_code = html_lib.escape(result)
            self.terminal.output_area.append(f"<pre style='background-color:#1E1E1E; color:#D4D4D4; padding:10px; border-radius:4px;'>{escaped_code}</pre>")
            
            self.history.add_entry("Code Generation", "Code Block generated", success=True)
            
        else:
            # Command Mode (CommandResponse object)
            cmd = result.command_shell
            explanation = result.explanation
            
            self.terminal.append_output(f"Generated: {cmd}", "#10B981")
            self.terminal.append_output(f"Explanation: {explanation}", "#aaa")
            
            if result.is_safe:
                stdout, stderr = self.executor.execute(cmd)
                if stdout:
                    self.terminal.append_output(stdout)
                if stderr:
                    self.terminal.append_output(stderr, "#EF4444")
                
                self.history.add_entry(result.command_nlp, cmd, success=not bool(stderr))
                self.history_view.refresh_history()
            else:
                self.terminal.append_output("Command deemed unsafe. Please review and execute manually if sure.", "#F59E0B")

    def format_html_table(self, data):
        import json
        
        # Normalize data to columns/rows structure if possible
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                columns = list(data[0].keys())
                rows = [[str(item.get(col, "")) for col in columns] for item in data]
                data = {"columns": columns, "rows": rows}
        elif isinstance(data, dict) and ("columns" not in data or "rows" not in data):
            # Key-Value table for simple dicts
            if all(not isinstance(v, (dict, list)) for v in data.values()):
                data = {
                    "columns": ["Field", "Value"],
                    "rows": [[str(k), str(v)] for k, v in data.items()]
                }

        # Render table or fallback to JSON
        if "columns" not in data or "rows" not in data:
            return f"<pre style='color: #CCCCCC;'>{json.dumps(data, indent=2)}</pre>"
        
        html = "<table border='1' cellspacing='0' cellpadding='5' style='border-collapse: collapse; border-color: #444; width: 100%;'>"
        html += "<thead><tr style='background-color: #333;'>"
        for col in data["columns"]:
            html += f"<th style='color: white; padding: 8px; text-align: left;'>{col}</th>"
        html += "</tr></thead><tbody>"
        
        for i, row in enumerate(data["rows"]):
            bg_color = "#2D2D2D" if i % 2 == 0 else "#252526"
            html += f"<tr style='background-color: {bg_color};'>"
            for cell in row:
                html += f"<td style='padding: 8px; color: #CCCCCC;'>{cell}</td>"
            html += "</tr>"
        html += "</tbody></table>"
        return html

    def on_error(self, err):
        self.terminal.append_output(f"Error: {err}", "#EF4444")

def from_qthread_import_QThread():
    from PySide6.QtCore import QThread
    return QThread()

def main():
    app = QApplication(sys.argv)
    window = PromptShellWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()