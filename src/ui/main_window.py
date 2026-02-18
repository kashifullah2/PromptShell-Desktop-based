import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from qfluentwidgets import (FluentWindow, NavigationItemPosition, FluentIcon as FIF, 
                            Theme, setTheme, SplashScreen, isDarkTheme)

from src.ui.widgets.terminal import TerminalWidget
from src.ui.widgets.history_view import HistoryWidget
from src.ui.widgets.settings_page import SettingsPage
from src.core.worker import CommandWorker
from src.ui.theme import ThemeManager
from src.core.config import settings

class PromptShellWindow(FluentWindow):
    
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
        self.terminal_interface = TerminalWidget(self)
        self.terminal_interface.setObjectName("terminal_interface")
        
        self.history_interface = HistoryWidget(self.history, self)
        self.history_interface.setObjectName("history_interface")
        
        self.settings_interface = SettingsPage(self)
        self.settings_interface.setObjectName("settings_interface")
        
        self.init_navigation()
        self.init_window()
        self.connect_signals()
        
    def init_navigation(self):
        self.addSubInterface(self.terminal_interface, FIF.COMMAND_PROMPT, "Terminal")
        self.addSubInterface(self.history_interface, FIF.HISTORY, "History")
        self.addSubInterface(self.settings_interface, FIF.SETTING, "Settings", NavigationItemPosition.BOTTOM)
        
    def init_window(self):
        self.setMicaEffectEnabled(True)
        theme = Theme.DARK if settings.config.theme == "dark" else Theme.LIGHT
        setTheme(theme)
        
        # Set a custom icon if available, otherwise just window title
        # self.setWindowIcon(QIcon("path/to/icon.png"))
        
        # Center window
        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(int(w/2 - self.width()/2), int(h/2 - self.height()/2))

    def connect_signals(self):
        self.terminal_interface.command_submitted.connect(self.process_command)
        self.history_interface.command_selected.connect(self.on_history_command_selected)
        self.settings_interface.settings_saved.connect(self.on_settings_saved)
        # self.settings_interface.theme_changed.connect(self.on_theme_changed) # FluentWindow handles theme mostly

    def on_history_command_selected(self, cmd):
        self.terminal_interface.input_field.setText(cmd)
        self.switchTo(self.terminal_interface)

    def on_settings_saved(self):
        self.llm_engine.initialize()
        self.switchTo(self.terminal_interface)
            
    def process_command(self, text, task_type="command"):
        # 1. Generate Command via LLM (Threaded)
        self.terminal_interface.append_output(f"Processing... ({task_type})")
        
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
            self.terminal_interface.append_output("📊 Analysis Result:")
            html = self.format_html_table(result)
            self.terminal_interface.display_analysis_result(result, html)
            
            # Add to history
            self.history.add_entry("Analysis Task", "Data Table generated", success=True)
            self.history_interface.refresh_history()
            
        elif isinstance(result, str):
            # Developer Mode: Render Code
            self.terminal_interface.append_output("💻 Generated Code:")
            self.terminal_interface.append_output(result)
            
            self.history.add_entry("Code Generation", "Code Block generated", success=True)
            self.history_interface.refresh_history()
            
        else:
            # Command Mode (CommandResponse object)
            cmd = result.command_shell
            explanation = result.explanation
            
            self.terminal_interface.append_output(f"Generated: {cmd}")
            self.terminal_interface.append_output(f"Explanation: {explanation}")
            
            if result.is_safe:
                stdout, stderr = self.executor.execute(cmd)
                if stdout:
                    self.terminal_interface.append_output(stdout)
                if stderr:
                    self.terminal_interface.append_output(f"Error: {stderr}")
                
                self.history.add_entry(result.command_nlp, cmd, success=not bool(stderr))
                self.history_interface.refresh_history()
            else:
                self.terminal_interface.append_output("⚠️ Command deemed unsafe. Please review and execute manually if sure.")
                # We could add an interactive approval here later

    def format_html_table(self, data):
        # Determine colors based on theme
        dark = isDarkTheme()
        border_color = "#444" if dark else "#E0E0E0"
        header_bg = "#333" if dark else "#F0F0F0"
        header_text = "white" if dark else "#333"
        cell_text = "#CCCCCC" if dark else "#333"
        
        if isinstance(data, dict):
            # Single object or Key-Value pairs
            html = f"<table border='1' cellspacing='0' cellpadding='5' style='border-collapse: collapse; border-color: {border_color}; width: 100%;'>"
            html += f"<thead><tr style='background-color: {header_bg};'><th style='color: {header_text}; padding: 8px; text-align: left;'>Field</th><th style='color: {header_text}; padding: 8px; text-align: left;'>Value</th></tr></thead><tbody>"
            for k, v in data.items():
                html += f"<tr><td style='padding: 8px; color: {cell_text};'>{k}</td><td style='padding: 8px; color: {cell_text};'>{v}</td></tr>"
            html += "</tbody></table>"
            return html
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            # List of objects
            columns = list(data[0].keys())
            html = f"<table border='1' cellspacing='0' cellpadding='5' style='border-collapse: collapse; border-color: {border_color}; width: 100%;'>"
            html += f"<thead><tr style='background-color: {header_bg};'>"
            for col in columns:
                html += f"<th style='color: {header_text}; padding: 8px; text-align: left;'>{col}</th>"
            html += "</tr></thead><tbody>"
            for row in data:
                html += "<tr>"
                for col in columns:
                    val = row.get(col, "")
                    html += f"<td style='padding: 8px; color: {cell_text};'>{val}</td>"
                html += "</tr>"
            html += "</tbody></table>"
            return html
            
        import json
        return json.dumps(data, indent=2)

    def on_error(self, err):
        self.terminal_interface.on_processing_error(str(err))

    def closeEvent(self, event):
        # Clean up threads
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        super().closeEvent(event)

def main():
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    window = PromptShellWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()