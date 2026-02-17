from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QSplitter, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
import qtawesome as qta

class TerminalWidget(QWidget):
    command_submitted = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFontPointSize(12)
        # Monospace font - removed hardcoded colors
        self.output_area.setStyleSheet("font-family: 'Fira Code', 'Courier New', monospace; border: none; padding: 10px;")
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or describe what you want to do...")
        self.input_field.setMinimumHeight(40)
        self.input_field.returnPressed.connect(self.submit_command)
        
        # Run button with icon
        self.run_btn = QPushButton(" Run")
        self.run_btn.setIcon(qta.icon('fa5s.play', color='white'))
        self.run_btn.setIconSize(QSize(16, 16))
        self.run_btn.setObjectName("primary")
        self.run_btn.clicked.connect(self.submit_command)
        self.run_btn.setMinimumHeight(40)
        
        # Clear button with icon
        self.clear_btn = QPushButton(" Clear")
        self.clear_btn.setIcon(qta.icon('fa5s.eraser', color='#007ACC'))
        self.clear_btn.setIconSize(QSize(16, 16))
        self.clear_btn.clicked.connect(self.clear_terminal)
        self.clear_btn.setMinimumHeight(40)
        
        layout = QVBoxLayout()
        layout.addWidget(self.output_area)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.run_btn)
        input_layout.addWidget(self.clear_btn)
        
        layout.addLayout(input_layout)
        self.setLayout(layout)
        
        # Show welcome message
        self.show_welcome_message()
        
    def show_welcome_message(self):
        """Display welcome message when terminal loads"""
        # Use colors that work in both light and dark modes
        welcome = """<span style="color:#0078D4; font-weight:bold;">Welcome to PromptShell Terminal!</span>
<span style="color:#14CE14;">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>

<span style="color:inherit;">Type your commands or describe what you want to do in natural language.</span>
<span style="color:inherit;">The AI will help you execute shell commands safely.</span>

<span style="color:#14CE14;">Ready to start!</span>
"""
        self.output_area.setHtml(welcome)
        
    def clear_terminal(self):
        """Clear terminal and show welcome message again"""
        self.output_area.clear()
        self.show_welcome_message()
        
    def submit_command(self):
        text = self.input_field.text().strip()
        if text:
            self.append_output(f"> {text}", color="#007ACC")  # VS Code blue for user input
            self.command_submitted.emit(text)
            self.input_field.clear()
            
    def append_output(self, text, color=None):
        if color:
            self.output_area.append(f'<span style="color:{color}">{text}</span>')
        else:
            self.output_area.append(text)
        
        # Auto scroll
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_area.setTextCursor(cursor)

