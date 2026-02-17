from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QSplitter, QLabel, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QThread
import qtawesome as qta
import os
from src.core.media_processor import MediaProcessorWorker

class TerminalWidget(QWidget):
    command_submitted = Signal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_context = None
        self.active_file_type = None
        self.active_file_path = None
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)

        self.output_area.setFontPointSize(12)
        # Monospace font - removed hardcoded colors
        self.output_area.setStyleSheet("font-family: 'Fira Code', 'Courier New', monospace; border: none; padding: 10px;")
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or describe what you want to do...")
        self.input_field.setMinimumHeight(40)
        self.input_field.returnPressed.connect(self.submit_command)
        
        # Upload button
        self.upload_btn = QPushButton()
        self.upload_btn.setIcon(qta.icon('fa5s.paperclip', color='#CCCCCC'))
        self.upload_btn.setIconSize(QSize(16, 16))
        self.upload_btn.setToolTip("Upload PDF, Image, or Video")
        self.upload_btn.clicked.connect(self.handle_upload)
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.setFixedWidth(40)

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
        
        # File preview label
        self.file_preview = QLabel()
        self.file_preview.setVisible(False)
        self.file_preview.setStyleSheet("background-color: #2D2D2D; color: #CCCCCC; padding: 5px; border-radius: 4px; margin-bottom: 5px;")
        layout.addWidget(self.file_preview)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.upload_btn)
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
        self.clear_file_context()
        
    def handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Media File", "", 
            "Media Files (*.pdf *.png *.jpg *.jpeg *.bmp *.mp4 *.avi *.mov)"
        )
        if file_path:
            self.start_processing(file_path)

    def start_processing(self, file_path):
        self.active_file_path = file_path
        self.run_btn.setText(" Analyzing...")
        self.run_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        self.upload_btn.setEnabled(False)
        
        self.thread = QThread()
        self.worker = MediaProcessorWorker(file_path)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def on_processing_finished(self, content, file_type):
        self.active_context = content
        self.active_file_type = file_type
        
        self.run_btn.setText(" Run")
        self.run_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.upload_btn.setEnabled(True)
        
        filename = os.path.basename(self.active_file_path)
        self.file_preview.setText(f"📄 {filename} ({file_type.upper()}) - Ready")
        self.file_preview.setVisible(True)
        self.input_field.setFocus()
        
        self.append_output(f"Analyzed {filename}. Extracted content length: {len(content)} chars.", color="#14CE14")

    def on_processing_error(self, error_msg):
        self.run_btn.setText(" Run")
        self.run_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.upload_btn.setEnabled(True)
        self.append_output(f"Error analyzing file: {error_msg}", color="red")

    def clear_file_context(self):
        self.active_context = None
        self.active_file_type = None
        self.active_file_path = None
        self.file_preview.setVisible(False)

    def submit_command(self):
        text = self.input_field.text().strip()
        if text:
            display_text = text
            task_type = "command"
            
            if self.active_context:
                display_text = f"[With File Context] {text}"
                
                # Construct payload with context
                system_prompt_add = ""
                if self.active_file_type in ['pdf', 'image']:
                    system_prompt_add = (
                        "You are an expert Data Analyst. "
                        "Your task is to extract information from the provided context based on the user's request. "
                        "Return the result ONLY as a valid JSON object. "
                        "If the requested information is not found, return null values in the JSON. "
                        "Do not include any conversational text, markdown formatting, or explanations outside the JSON."
                    )
                    task_type = "analyst"
                elif self.active_file_type == 'video':
                    system_prompt_add = "You are an expert Senior Developer."
                    task_type = "developer"
                
                full_query = f"{system_prompt_add}\n\nContext Content:\n{self.active_context}\n\nUser Question: {text}"
                
                self.append_output(f"> {display_text}", color="#007ACC")
                self.command_submitted.emit(full_query, task_type)
            else:
                self.append_output(f"> {text}", color="#007ACC")
                self.command_submitted.emit(text, task_type)
                
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

