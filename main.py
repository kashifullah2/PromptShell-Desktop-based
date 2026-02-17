import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                               QSplitter, QTabWidget, QLabel, QFrame, QScrollArea,
                               QToolButton, QSizePolicy, QStackedWidget)
from PySide6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer, 
                            QParallelAnimationGroup, QRect, Signal, QThread)
from PySide6.QtGui import (QFont, QColor, QPalette, QTextCharFormat, 
                           QSyntaxHighlighter, QIcon, QPainter, QLinearGradient)
from src.core.llm_engine import LLMEngine
from src.core.executor import CommandExecutor
from src.core.history import CommandHistory, AliasManager


class Theme:
    """Theme configuration for light and dark modes"""
    
    class Light:
        BG_PRIMARY = "#F9F9F9"
        BG_SECONDARY = "#FFFFFF"
        BG_TERTIARY = "#F3F4F6"
        TEXT_PRIMARY = "#1F2937"
        TEXT_SECONDARY = "#6B7280"
        TEXT_MUTED = "#9CA3AF"
        ACCENT = "#3B82F6"
        ACCENT_HOVER = "#2563EB"
        SUCCESS = "#10B981"
        ERROR = "#EF4444"
        WARNING = "#F59E0B"
        BORDER = "#E5E7EB"
        SHADOW = "rgba(0, 0, 0, 0.1)"
    
    class Dark:
        BG_PRIMARY = "#1E1E2F"
        BG_SECONDARY = "#2A2A3E"
        BG_TERTIARY = "#363650"
        TEXT_PRIMARY = "#E5E7EB"
        TEXT_SECONDARY = "#D1D5DB"
        TEXT_MUTED = "#9CA3AF"
        ACCENT = "#3B82F6"
        ACCENT_HOVER = "#60A5FA"
        SUCCESS = "#10B981"
        ERROR = "#EF4444"
        WARNING = "#F59E0B"
        BORDER = "#4B5563"
        SHADOW = "rgba(0, 0, 0, 0.3)"


class Fonts:
    """Professional font configuration"""
    PRIMARY = "Segoe UI"
    SECONDARY = "Inter"
    MONO = "Fira Code"
    
    SIZE_LARGE = 16
    SIZE_NORMAL = 14
    SIZE_SMALL = 12
    SIZE_TINY = 10


class CommandSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for command output"""
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or Theme.Dark
        self.setup_formats()
    
    def setup_formats(self):
        self.command_format = QTextCharFormat()
        self.command_format.setForeground(QColor(self.theme.ACCENT))
        self.command_format.setFontWeight(QFont.Weight.Bold)
        
        self.success_format = QTextCharFormat()
        self.success_format.setForeground(QColor(self.theme.SUCCESS))
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor(self.theme.ERROR))
        
        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor(self.theme.WARNING))
    
    def highlightBlock(self, text):
        # Highlight commands (first word)
        words = text.split()
        if words:
            self.setFormat(0, len(words[0]), self.command_format)
        
        # Highlight paths
        import re
        for match in re.finditer(r'/[\w/.-]+', text):
            self.setFormat(match.start(), match.end() - match.start(), self.path_format)


class AnimatedButton(QPushButton):
    """Button with smooth hover animations"""
    def __init__(self, text, parent=None, theme=None):
        super().__init__(text, parent)
        self.theme = theme or Theme.Dark
        self.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_NORMAL, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        
        self.default_style = f"""
            QPushButton {{
                background-color: {self.theme.ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {self.theme.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.ACCENT};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
        """
        self.setStyleSheet(self.default_style)


class AnimatedSidebar(QFrame):
    """Animated sliding sidebar"""
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or Theme.Dark
        self.is_expanded = True
        self.collapsed_width = 60
        self.expanded_width = 250
        
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Navigation")
        header.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_NORMAL, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Navigation buttons
        nav_items = [
            ("Terminal", "terminal"),
            ("History", "history"),
            ("Aliases", "aliases"),
            ("Settings", "settings")
        ]
        
        for text, icon in nav_items:
            btn = QPushButton(text)
            btn.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_SMALL))
            btn.setMinimumHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.theme.TEXT_PRIMARY};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.BG_TERTIARY};
                }}
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def apply_theme(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.BG_SECONDARY};
                border-right: 1px solid {self.theme.BORDER};
            }}
        """)
    
    def toggle(self):
        """Animate sidebar collapse/expand"""
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        if self.is_expanded:
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.setMaximumWidth(self.collapsed_width)
        else:
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.setMaximumWidth(self.expanded_width)
        
        self.animation.start()
        self.is_expanded = not self.is_expanded


class CommandInputPanel(QFrame):
    """Professional command input panel with animations"""
    command_submitted = Signal(str)
    
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or Theme.Dark
        self.command_history = []
        self.history_index = -1
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Label
        label = QLabel("Command Input")
        label.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_SMALL, QFont.Weight.Medium))
        label.setStyleSheet(f"color: {self.theme.TEXT_SECONDARY};")
        layout.addWidget(label)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your command or describe what you want to do...")
        self.input_field.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_NORMAL))
        self.input_field.setMinimumHeight(48)
        self.input_field.returnPressed.connect(self.submit_command)
        self.input_field.installEventFilter(self)
        
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.BG_SECONDARY};
                color: {self.theme.TEXT_PRIMARY};
                border: 2px solid {self.theme.BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.theme.ACCENT};
            }}
        """)
        layout.addWidget(self.input_field)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.run_btn = AnimatedButton("Run", theme=self.theme)
        self.run_btn.clicked.connect(self.submit_command)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_NORMAL))
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.input_field.clear)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme.TEXT_SECONDARY};
                border: 2px solid {self.theme.BORDER};
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.BG_TERTIARY};
            }}
        """)
        
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def apply_theme(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.BG_PRIMARY};
                border-top: 1px solid {self.theme.BORDER};
            }}
        """)
    
    def submit_command(self):
        text = self.input_field.text().strip()
        if text:
            self.command_history.append(text)
            self.history_index = len(self.command_history)
            self.command_submitted.emit(text)
            self.input_field.clear()
    
    def eventFilter(self, obj, event):
        """Handle arrow key navigation for command history"""
        if obj == self.input_field and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.input_field.setText(self.command_history[self.history_index])
                return True
            elif event.key() == Qt.Key.Key_Down:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.input_field.setText(self.command_history[self.history_index])
                elif self.history_index == len(self.command_history) - 1:
                    self.history_index = len(self.command_history)
                    self.input_field.clear()
                return True
        return super().eventFilter(obj, event)


class OutputPanel(QFrame):
    """Professional output panel with tabs and animations"""
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or Theme.Dark
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_SMALL))
        
        # Output tab
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont(Fonts.MONO, Fonts.SIZE_SMALL))
        self.output_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Apply syntax highlighting
        self.highlighter = CommandSyntaxHighlighter(self.output_text.document(), self.theme)
        
        # Logs tab
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont(Fonts.MONO, Fonts.SIZE_SMALL))
        
        # Errors tab
        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)
        self.errors_text.setFont(QFont(Fonts.MONO, Fonts.SIZE_SMALL))
        
        self.tabs.addTab(self.output_text, "Output")
        self.tabs.addTab(self.logs_text, "Logs")
        self.tabs.addTab(self.errors_text, "Errors")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def apply_theme(self):
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.theme.BORDER};
                background-color: {self.theme.BG_SECONDARY};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {self.theme.BG_TERTIARY};
                color: {self.theme.TEXT_SECONDARY};
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.theme.BG_SECONDARY};
                color: {self.theme.ACCENT};
                border-bottom: 2px solid {self.theme.ACCENT};
            }}
            QTabBar::tab:hover {{
                background-color: {self.theme.BG_SECONDARY};
            }}
        """)
        
        text_style = f"""
            QTextEdit {{
                background-color: {self.theme.BG_SECONDARY};
                color: {self.theme.TEXT_PRIMARY};
                border: none;
                padding: 12px;
                font-family: '{Fonts.MONO}';
                font-size: {Fonts.SIZE_SMALL}px;
            }}
        """
        self.output_text.setStyleSheet(text_style)
        self.logs_text.setStyleSheet(text_style)
        self.errors_text.setStyleSheet(text_style)
    
    def add_output(self, text, fade_in=True):
        """Add output with optional fade-in animation"""
        self.output_text.append(text)
        
        if fade_in:
            # Scroll to bottom
            cursor = self.output_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.output_text.setTextCursor(cursor)
    
    def add_log(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {text}")
    
    def add_error(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.errors_text.append(f"[{timestamp}] ERROR: {text}")
        self.tabs.setCurrentWidget(self.errors_text)


class CommandGeneratorThread(QThread):
    """Background thread for command generation"""
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, llm, user_text):
        super().__init__()
        self.llm = llm
        self.user_text = user_text
    
    def run(self):
        try:
            command_obj = self.llm.generate_command(self.user_text)
            self.finished.emit(command_obj)
        except Exception as e:
            self.error.emit(str(e))


class PromptShellPro(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptShell Professional")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 600)
        
        # Theme
        self.is_dark_mode = True
        self.current_theme = Theme.Dark
        
        # Core components
        try:
            self.llm = LLMEngine()
        except ValueError as e:
            print(f"LLM Error: {e}")
            self.llm = None
        
        self.executor = CommandExecutor()
        self.history_manager = CommandHistory()
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = AnimatedSidebar(theme=self.current_theme)
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Output panel
        self.output_panel = OutputPanel(theme=self.current_theme)
        splitter.addWidget(self.output_panel)
        
        # Input panel
        self.input_panel = CommandInputPanel(theme=self.current_theme)
        self.input_panel.command_submitted.connect(self.handle_command)
        splitter.addWidget(self.input_panel)
        
        # Set initial sizes (70% output, 30% input)
        splitter.setSizes([700, 300])
        splitter.setHandleWidth(2)
        
        content_layout.addWidget(splitter)
        content_widget.setLayout(content_layout)
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_widget)
        
        central.setLayout(main_layout)
        
        # Welcome message
        self.output_panel.add_log("PromptShell Professional initialized")
        self.output_panel.add_output("Welcome to PromptShell Professional\n" + "="*50 + "\n")
    
    def create_header(self):
        """Create application header"""
        header = QFrame()
        header.setFixedHeight(60)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Title
        title = QLabel("PromptShell Pro")
        title.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_LARGE, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Theme toggle
        theme_btn = QToolButton()
        theme_btn.setText("🌙" if self.is_dark_mode else "☀️")
        theme_btn.setFont(QFont(Fonts.PRIMARY, 16))
        theme_btn.setMinimumSize(40, 40)
        theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        theme_btn.clicked.connect(self.toggle_theme)
        theme_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {self.current_theme.BG_TERTIARY};
                border: none;
                border-radius: 20px;
            }}
            QToolButton:hover {{
                background-color: {self.current_theme.ACCENT};
            }}
        """)
        layout.addWidget(theme_btn)
        
        # Sidebar toggle
        sidebar_btn = QToolButton()
        sidebar_btn.setText("☰")
        sidebar_btn.setFont(QFont(Fonts.PRIMARY, 18))
        sidebar_btn.setMinimumSize(40, 40)
        sidebar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_btn.clicked.connect(self.sidebar.toggle)
        sidebar_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {self.current_theme.BG_TERTIARY};
                border: none;
                border-radius: 20px;
            }}
            QToolButton:hover {{
                background-color: {self.current_theme.ACCENT};
            }}
        """)
        layout.addWidget(sidebar_btn)
        
        header.setLayout(layout)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.current_theme.BG_SECONDARY};
                border-bottom: 1px solid {self.current_theme.BORDER};
            }}
        """)
        
        return header
    
    def apply_theme(self):
        """Apply current theme to application"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.current_theme.BG_PRIMARY))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.current_theme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Base, QColor(self.current_theme.BG_SECONDARY))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.current_theme.TEXT_PRIMARY))
        self.setPalette(palette)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.current_theme.BG_PRIMARY};
            }}
            QSplitter::handle {{
                background-color: {self.current_theme.BORDER};
            }}
            QSplitter::handle:hover {{
                background-color: {self.current_theme.ACCENT};
            }}
        """)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = Theme.Dark if self.is_dark_mode else Theme.Light
        
        # Recreate UI with new theme
        self.setup_ui()
        self.apply_theme()
        
        self.output_panel.add_log(f"Switched to {'dark' if self.is_dark_mode else 'light'} mode")
    
    def handle_command(self, text):
        """Handle command submission"""
        self.output_panel.add_output(f"\n> {text}\n", fade_in=True)
        self.output_panel.add_log(f"Command received: {text}")
        
        if not self.llm:
            self.output_panel.add_error("LLM not initialized. Check your API key.")
            return
        
        # Generate command in background
        self.worker = CommandGeneratorThread(self.llm, text)
        self.worker.finished.connect(self.on_command_generated)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
        self.output_panel.add_log("Generating command...")
    
    def on_command_generated(self, command_obj):
        """Handle generated command"""
        self.output_panel.add_output(f"Generated Command: {command_obj.command_shell}\n")
        self.output_panel.add_output(f"Explanation: {command_obj.explanation}\n")
        
        # Execute command
        stdout, stderr = self.executor.execute(command_obj.command_shell)
        
        if stdout:
            self.output_panel.add_output(f"\nOutput:\n{stdout}\n")
        if stderr:
            self.output_panel.add_error(stderr)
        
        # Save to history
        self.history_manager.add_entry(command_obj.command_nlp, command_obj.command_shell, not bool(stderr))
    
    def on_error(self, error_msg):
        """Handle error"""
        self.output_panel.add_error(error_msg)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    app.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_NORMAL))
    
    window = PromptShellPro()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()