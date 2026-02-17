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
            
    def process_command(self, text):
        # 1. Generate Command via LLM (Threaded)
        self.terminal.append_output("Processing...", "#888")
        
        # Create worker
        # Note: In production, store worker in self to prevent garbage collection
        self.worker = CommandWorker(text, self.llm_engine)
        self.worker.finished.connect(self.on_command_generated)
        self.worker.error.connect(self.on_error)
        
        # Logic to wait? No, async.
        import threading
        # QThread logic is in CommandWorker. But CommandWorker inherits QObject, not QThread.
        # Wait, I checked src/core/worker.py in my previous step.
        # "class CommandWorker(QObject): ... def run(self)..."
        # It needs to be moved to a QThread.
        
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
        
    def on_command_generated(self, result):
        # result is CommandResponse object
        cmd = result.command_shell
        explanation = result.explanation
        
        self.terminal.append_output(f"Generated: {cmd}", "#10B981")
        self.terminal.append_output(f"Explanation: {explanation}", "#aaa")
        
        # Execute? Or ask for confirmation?
        # User requested "stable command execution flow". 
        # I'll add execute logic here or button.
        # For professional feel, let's auto-execute if safe, or show button.
        
        # For now, auto-execute for flow demonstration, or check safe flag.
        if result.is_safe:
            stdout, stderr = self.executor.execute(cmd)
            if stdout:
                self.terminal.append_output(stdout)
            if stderr:
                self.terminal.append_output(stderr, "#EF4444")
            
            # Save to history
            self.history.add_entry(result.command_nlp, cmd, success=not bool(stderr))
            self.history_view.refresh_history()
        else:
            self.terminal.append_output("Command deemed unsafe. Please review and execute manually if sure.", "#F59E0B")

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