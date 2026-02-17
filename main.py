import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QScrollArea, QLabel, QFrame, QMessageBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QTextCursor, QIcon, QPainter, QLinearGradient
from src.core.llm_engine import LLMEngine
from src.core.executor import CommandExecutor
from src.core.history import HistoryManager


# Modern Theme with vibrant colors
DARK_THEME = {
    'bg': '#0A0E27',
    'bg_secondary': '#151932',
    'card_bg': '#1A1F3A',
    'accent_primary': '#667EEA',
    'accent_secondary': '#764BA2',
    'success': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'text': '#F9FAFB',
    'text_secondary': '#D1D5DB',
    'text_muted': '#9CA3AF',
    'border': '#374151',
    'shadow': 'rgba(102, 126, 234, 0.3)',
}

LIGHT_THEME = {
    'bg': '#F8FAFC',
    'bg_secondary': '#FFFFFF',
    'card_bg': '#FFFFFF',
    'accent_primary': '#667EEA',
    'accent_secondary': '#764BA2',
    'success': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'text': '#1F2937',
    'text_secondary': '#4B5563',
    'text_muted': '#6B7280',
    'border': '#E5E7EB',
    'shadow': 'rgba(102, 126, 234, 0.2)',
}


class CommandGeneratorThread(QThread):
    """Background thread for LLM command generation"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
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


class ModernButton(QPushButton):
    """Custom modern button with hover effects"""
    def __init__(self, text, color_type='primary', parent=None):
        super().__init__(text, parent)
        self.color_type = color_type
        self.theme = DARK_THEME
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(45)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.apply_style()
    
    def apply_style(self):
        if self.color_type == 'primary':
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.theme['accent_primary']}, stop:1 {self.theme['accent_secondary']});
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #7C8FFF, stop:1 #8B5FBF);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5568D3, stop:1 #653A8B);
                }}
            """)
        elif self.color_type == 'success':
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['success']};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #14D99E;
                }}
                QPushButton:pressed {{
                    background-color: #0D9668;
                }}
            """)
        elif self.color_type == 'danger':
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme['danger']};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #F87171;
                }}
                QPushButton:pressed {{
                    background-color: #DC2626;
                }}
            """)


class MessageBubble(QFrame):
    """Modern message bubble with animations"""
    def __init__(self, text, is_user=False, theme=None, parent=None):
        super().__init__(parent)
        self.theme = theme or DARK_THEME
        self.is_user = is_user
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon
        icon_label = QLabel("👤" if is_user else "🤖")
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {self.theme['accent_primary'] if is_user else self.theme['accent_secondary']};
            border-radius: 20px;
        """)
        
        # Message text
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setFont(QFont("Segoe UI", 11))
        self.label.setStyleSheet(f"color: {self.theme['text']}; padding: 5px;")
        
        if is_user:
            layout.addStretch()
            layout.addWidget(self.label)
            layout.addWidget(icon_label)
        else:
            layout.addWidget(icon_label)
            layout.addWidget(self.label)
            layout.addStretch()
        
        self.setLayout(layout)
        self.apply_style()
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def apply_style(self):
        if self.is_user:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.theme['accent_primary']}, stop:1 {self.theme['accent_secondary']});
                    border-radius: 16px;
                    margin: 5px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme['card_bg']};
                    border-radius: 16px;
                    border: 1px solid {self.theme['border']};
                    margin: 5px;
                }}
            """)


class CommandCard(QFrame):
    """Ultra-modern command card with glassmorphism"""
    def __init__(self, command_obj, executor, safe_mode, theme=None, parent=None):
        super().__init__(parent)
        self.command_obj = command_obj
        self.executor = executor
        self.safe_mode = safe_mode
        self.parent_window = parent
        self.theme = theme or DARK_THEME
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(self.theme['shadow']))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header with icon
        header_layout = QHBoxLayout()
        
        icon = QLabel("⚡")
        icon.setFont(QFont("Segoe UI Emoji", 20))
        icon.setFixedSize(35, 35)
        
        task_label = QLabel(f"<b>Task:</b> {self.command_obj.command_nlp}")
        task_label.setFont(QFont("Segoe UI", 10))
        task_label.setStyleSheet(f"color: {self.theme['text_secondary']};")
        task_label.setWordWrap(True)
        
        header_layout.addWidget(icon)
        header_layout.addWidget(task_label, 1)
        layout.addLayout(header_layout)
        
        # Command display with gradient background
        cmd_container = QFrame()
        cmd_container.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.theme['accent_primary']}, stop:1 {self.theme['accent_secondary']});
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        cmd_layout = QVBoxLayout()
        cmd_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cmd_label = QLabel(self.command_obj.command_shell)
        self.cmd_label.setFont(QFont("Fira Code", 12, QFont.Bold))
        self.cmd_label.setStyleSheet("color: white;")
        self.cmd_label.setWordWrap(True)
        self.cmd_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        cmd_layout.addWidget(self.cmd_label)
        cmd_container.setLayout(cmd_layout)
        layout.addWidget(cmd_container)
        
        # Explanation with icon
        exp_layout = QHBoxLayout()
        exp_icon = QLabel("💡")
        exp_icon.setFont(QFont("Segoe UI Emoji", 14))
        
        exp_text = QLabel(self.command_obj.explanation)
        exp_text.setFont(QFont("Segoe UI", 10, QFont.StyleItalic))
        exp_text.setStyleSheet(f"color: {self.theme['text_muted']};")
        exp_text.setWordWrap(True)
        
        exp_layout.addWidget(exp_icon)
        exp_layout.addWidget(exp_text, 1)
        layout.addLayout(exp_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.execute_btn = ModernButton("▶ Execute", 'success')
        self.execute_btn.clicked.connect(self.execute_command)
        
        self.copy_btn = ModernButton("📋 Copy", 'primary')
        self.copy_btn.clicked.connect(self.copy_command)
        
        btn_layout.addWidget(self.execute_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme['card_bg']};
                border-radius: 20px;
                border: 1px solid {self.theme['border']};
            }}
        """)
    
    def execute_command(self):
        if self.safe_mode and not self.executor.is_safe(self.command_obj.command_shell):
            reply = QMessageBox.warning(
                self, "⚠️ Unsafe Command",
                f"This command may be dangerous:\n\n{self.command_obj.command_shell}\n\nProceed?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        if self.parent_window:
            self.parent_window.add_system_message(f"⚡ Executing: {self.command_obj.command_shell}")
        
        stdout, stderr = self.executor.execute(self.command_obj.command_shell)
        
        if stdout and self.parent_window:
            self.parent_window.add_output_message(stdout)
        if stderr and self.parent_window:
            self.parent_window.add_error_message(stderr)
    
    def copy_command(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.command_obj.command_shell)
        if self.parent_window:
            self.parent_window.add_system_message("✅ Copied to clipboard!")


class PromptShellUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptShell - AI Terminal Assistant")
        self.setGeometry(100, 100, 1400, 900)
        
        # Theme
        self.is_dark_mode = True
        self.current_theme = DARK_THEME
        
        # Core components
        try:
            self.llm = LLMEngine()
        except ValueError as e:
            QMessageBox.critical(self, "Configuration Error", str(e))
            sys.exit(1)
        
        self.executor = CommandExecutor()
        self.history = HistoryManager("promptshell_history.json")
        self.safe_mode = True
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ultra-modern header with gradient
        self.header = QFrame()
        self.header.setFixedHeight(100)
        self.header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.current_theme['accent_primary']}, 
                    stop:0.5 {self.current_theme['accent_secondary']},
                    stop:1 {self.current_theme['accent_primary']});
                border-bottom: 3px solid {self.current_theme['accent_secondary']};
            }}
        """)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # Logo and title
        title_container = QVBoxLayout()
        
        title = QLabel("⚡ PromptShell")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("AI-Powered Terminal Assistant")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Control buttons
        self.safe_mode_btn = ModernButton("🛡️ Safe Mode: ON", 'success')
        self.safe_mode_btn.setCheckable(True)
        self.safe_mode_btn.setChecked(True)
        self.safe_mode_btn.clicked.connect(self.toggle_safe_mode)
        
        self.theme_btn = ModernButton("🌙 Dark", 'primary')
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(self.safe_mode_btn)
        header_layout.addWidget(self.theme_btn)
        
        self.header.setLayout(header_layout)
        main_layout.addWidget(self.header)
        
        # Chat area with modern scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.current_theme['bg']};
            }}
            QScrollBar:vertical {{
                background: {self.current_theme['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.current_theme['accent_primary']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.current_theme['accent_secondary']};
            }}
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(15)
        self.chat_layout.setContentsMargins(30, 30, 30, 30)
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        
        self.scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll)
        
        # Modern input area
        self.input_frame = QFrame()
        self.input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.current_theme['bg_secondary']};
                border-top: 2px solid {self.current_theme['border']};
                padding: 25px;
            }}
        """)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("💬 Describe what you want to do...")
        self.input_field.setFont(QFont("Segoe UI", 12))
        self.input_field.setMinimumHeight(55)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.current_theme['bg']};
                color: {self.current_theme['text']};
                border: 2px solid {self.current_theme['border']};
                border-radius: 16px;
                padding: 15px 20px;
                font-size: 12pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.current_theme['accent_primary']};
                background-color: {self.current_theme['card_bg']};
            }}
        """)
        self.input_field.returnPressed.connect(self.handle_submit)
        
        self.send_btn = ModernButton("✨ Generate Command", 'primary')
        self.send_btn.setMinimumWidth(200)
        self.send_btn.clicked.connect(self.handle_submit)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        self.input_frame.setLayout(input_layout)
        main_layout.addWidget(self.input_frame)
        
        central_widget.setLayout(main_layout)
        
        # Welcome message
        self.add_system_message("👋 Welcome to PromptShell! Describe any task and I'll generate the perfect command.")
    
    def apply_theme(self):
        t = self.current_theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {t['bg']};
            }}
            QWidget {{
                background-color: {t['bg']};
                color: {t['text']};
            }}
        """)
    
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        
        if self.is_dark_mode:
            self.theme_btn.setText("🌙 Dark")
            self.add_system_message("🌙 Switched to Dark Mode")
        else:
            self.theme_btn.setText("☀️ Light")
            self.add_system_message("☀️ Switched to Light Mode")
        
        self.apply_theme()
        self.setup_ui()  # Rebuild UI with new theme
    
    def toggle_safe_mode(self):
        self.safe_mode = self.safe_mode_btn.isChecked()
        if self.safe_mode:
            self.safe_mode_btn.setText("🛡️ Safe Mode: ON")
            self.add_system_message("✅ Safe Mode enabled")
        else:
            self.safe_mode_btn.setText("⚠️ Safe Mode: OFF")
            self.add_system_message("⚠️ Safe Mode disabled")
    
    def add_message(self, text, is_user=False):
        msg = MessageBubble(text, is_user, self.current_theme)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def add_system_message(self, text):
        label = QLabel(f"ℹ️ {text}")
        label.setFont(QFont("Segoe UI", 10, QFont.StyleItalic))
        label.setStyleSheet(f"color: {self.current_theme['text_muted']}; padding: 10px;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, label)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def add_output_message(self, text):
        self.add_message(f"📤 Output:\n{text}", False)
    
    def add_error_message(self, text):
        label = QLabel(f"❌ Error: {text}")
        label.setFont(QFont("Segoe UI", 10))
        label.setStyleSheet(f"color: {self.current_theme['danger']}; padding: 10px;")
        label.setWordWrap(True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, label)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def add_command_card(self, command_obj):
        card = CommandCard(command_obj, self.executor, self.safe_mode, self.current_theme, self)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, card)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
    
    def handle_submit(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.send_btn.setText("⏳ Generating...")
        
        self.add_message(user_text, is_user=True)
        self.add_system_message("🤖 AI is thinking...")
        
        self.worker = CommandGeneratorThread(self.llm, user_text)
        self.worker.finished.connect(self.on_command_generated)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()
    
    def on_command_generated(self, command_obj):
        self.history.add_entry(self.input_field.text(), command_obj.command_shell)
        self.add_command_card(command_obj)
        
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("✨ Generate Command")
        self.input_field.setFocus()
    
    def on_generation_error(self, error_msg):
        self.add_error_message(f"Failed to generate command: {error_msg}")
        
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("✨ Generate Command")
        self.input_field.setFocus()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set app-wide font
    app.setFont(QFont("Segoe UI", 10))
    
    window = PromptShellUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()