from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, 
                               QStackedWidget, QMenu, QFrame)
from PySide6.QtGui import QTextCursor, QAction, QColor, QPalette
from PySide6.QtCore import Qt, Signal, QSize, QThread, QPoint
from qfluentwidgets import (TextEdit, LineEdit, PrimaryPushButton, PushButton, 
                            FluentIcon as FIF, ToolButton, InfoBar, InfoBarPosition,
                            TitleLabel, StrongBodyLabel, ImageLabel, CaptionLabel,
                            isDarkTheme, Theme)
import os
import json
import csv
from src.core.media_processor import MediaProcessorWorker

class WelcomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Icon
        icon_label = ToolButton(FIF.COMMAND_PROMPT)
        icon_label.setIconSize(QSize(96, 96))
        icon_label.setStyleSheet("border: none; background: transparent;")
        
        title = TitleLabel("PromptShell Professional", self)
        subtitle = StrongBodyLabel("AI-Powered Terminal & Data Analysis", self)
        
        instruction = StrongBodyLabel("Type your command, upload files, or ask questions to get started.", self)
        # Use simple conditional for initial color or just standard styling
        # Theme awareness is tricky if we don't listen to change, but standard labels usually adapt.
        # StrongBodyLabel adapts automatically to theme (black/white text), 
        # so forcing color #909090 is actually okay for "secondary" text in both modes usually, 
        # but let's make it slightly darker for light mode if possible or just remove hardcode if we want auto.
        # Let's keep it gray but ensure it handles light mode visibility.
        if isDarkTheme():
             instruction.setStyleSheet("color: #909090;")
        else:
             instruction.setStyleSheet("color: #606060;")
        
        layout.addWidget(icon_label, 0, Qt.AlignCenter)
        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(subtitle, 0, Qt.AlignCenter)
        layout.addWidget(instruction, 0, Qt.AlignCenter)
        
class FileContextBar(QFrame):
    """Widget to show active file context with a close button"""
    cleared = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setVisible(False)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 5, 12, 5)
        
        self.icon_label = QLabel()
        # We'll set icon via strict stylesheet or pixmap? 
        # Let's use simple text/emoji for now as per original
        
        self.text_label = StrongBodyLabel("Files ready", self)
        
        self.close_btn = ToolButton(FIF.CLOSE, self)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.cleared.emit)
        
        self.layout.addWidget(self.text_label, 1)
        self.layout.addWidget(self.close_btn)
        
        self.update_style()
        
    def update_style(self):
        dark = isDarkTheme()
        bg = "#2D2D2D" if dark else "#F5F5F5"
        border = "#3E3E42" if dark else "#E0E0E0"
        text = "#E0E0E0" if dark else "#333333"
        
        self.setStyleSheet(f"""
            FileContextBar {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            StrongBodyLabel {{
                color: {text};
                border: none;
                background: transparent;
            }}
        """)
        
    def set_text(self, text):
        self.text_label.setText(text)
        self.update_style() # Refresh style in case theme changed (simple approach)

class TerminalWidget(QWidget):
    command_submitted = Signal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminal_widget")
        self.active_context = ""
        self.active_file_type = None
        self.active_file_paths = []
        self.last_analysis_data = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Output Area Stack
        self.output_stack = QStackedWidget(self)
        
        # 1. Welcome Page
        self.welcome_page = WelcomeWidget(self)
        self.output_stack.addWidget(self.welcome_page)
        
        # 2. Output Text Area
        self.output_area = TextEdit()
        self.output_area.setReadOnly(True)
        # Use theme-neutral font style or adapt? 
        # TextEdit background adapts automatically. 
        self.output_area.setStyleSheet("font-family: 'Consolas', 'Fira Code', 'Menlo', 'Monospace'; font-size: 14px;")
        self.output_stack.addWidget(self.output_area)
        
        layout.addWidget(self.output_stack)
        
        # File Preview Bar (New)
        self.file_context_bar = FileContextBar(self)
        self.file_context_bar.cleared.connect(self.clear_file_context)
        layout.addWidget(self.file_context_bar)
        
        # Input Layout
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        # Upload Button
        self.upload_btn = ToolButton(FIF.FOLDER)
        self.upload_btn.setToolTip("Upload Files")
        self.upload_btn.clicked.connect(self.handle_upload)
        self.upload_btn.setFixedSize(36, 36)
        
        # Export Button (Hidden/Disabled by default)
        self.export_btn = ToolButton(FIF.SAVE)
        self.export_btn.setToolTip("Export Analysis Result")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.show_export_menu)
        self.export_btn.setFixedSize(36, 36)
        
        # Input Field
        self.input_field = LineEdit()
        self.input_field.setPlaceholderText("Enter command...")
        self.input_field.setMinimumHeight(36)
        self.input_field.returnPressed.connect(self.submit_command)
        
        # Run Button
        self.run_btn = PrimaryPushButton("Run", self)
        self.run_btn.setIcon(FIF.PLAY)
        self.run_btn.clicked.connect(self.submit_command)
        self.run_btn.setMinimumHeight(36)
        
        # Clear Button
        self.clear_btn = PushButton("Clear", self)
        self.clear_btn.setIcon(FIF.DELETE)
        self.clear_btn.clicked.connect(self.clear_terminal)
        self.clear_btn.setMinimumHeight(36)
        
        input_layout.addWidget(self.upload_btn)
        input_layout.addWidget(self.export_btn) # Added export button
        input_layout.addWidget(self.input_field, 1) 
        input_layout.addWidget(self.run_btn)
        input_layout.addWidget(self.clear_btn)
        
        layout.addLayout(input_layout)
        
        # Set default view
        self.output_stack.setCurrentIndex(0)
        
    def show_export_menu(self):
        if not self.last_analysis_data:
            return
            
        menu = QMenu(self)
        
        copy_action = QAction("Copy to Clipboard", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        menu.addAction(copy_action)
        
        csv_action = QAction("Save as CSV", self)
        csv_action.triggered.connect(self.save_as_csv)
        menu.addAction(csv_action)
        
        json_action = QAction("Save as JSON", self)
        json_action.triggered.connect(self.save_as_json)
        menu.addAction(json_action)
        
        menu.exec(self.export_btn.mapToGlobal(QPoint(0, -menu.sizeHint().height())))

    def copy_to_clipboard(self):
        import pyperclip
        if self.last_analysis_data:
             pyperclip.copy(json.dumps(self.last_analysis_data, indent=2))
             InfoBar.success(title='Copied', content="Data copied to clipboard", parent=self)

    def save_as_csv(self):
        if not self.last_analysis_data: 
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                data = self.last_analysis_data
                # Convert to efficient list of dicts
                rows = []
                headers = []
                
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    rows = data
                elif isinstance(data, dict):
                    headers = ["Field", "Value"]
                    rows = [{"Field": k, "Value": v} for k, v in data.items()]
                
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(rows)
                    
                InfoBar.success(title='Saved', content=f"Saved to {path}", parent=self)
            except Exception as e:
                InfoBar.error(title='Error', content=str(e), parent=self)

    def save_as_json(self):
        if not self.last_analysis_data:
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.last_analysis_data, f, indent=2)
                InfoBar.success(title='Saved', content=f"Saved to {path}", parent=self)
            except Exception as e:
                InfoBar.error(title='Error', content=str(e), parent=self)
        
    def clear_terminal(self):
        self.output_area.clear()
        self.output_stack.setCurrentIndex(0) # Show welcome
        self.clear_file_context()
        self.last_analysis_data = None
        self.export_btn.setEnabled(False)
        
    def handle_upload(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Media Files", "", 
            "Media Files (*.pdf *.png *.jpg *.jpeg *.bmp *.mp4 *.avi *.mov)"
        )
        if file_paths:
            self.start_processing(file_paths)

    def start_processing(self, file_paths):
        self.active_file_paths = file_paths
        self.run_btn.setText("Analyzing...")
        self.run_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        self.upload_btn.setEnabled(False)
        
        self.processing_queue = list(file_paths)
        self.active_context = "" # Reset context
        self.process_next_file()

    def process_next_file(self):
        if not self.processing_queue:
            self.on_all_files_processed()
            return
            
        file_path = self.processing_queue.pop(0)
        
        # Ensure previous thread is cleaned up
        if hasattr(self, 'processing_thread') and self.processing_thread is not None:
             try:
                 if self.processing_thread.isRunning():
                     self.processing_thread.quit()
                     self.processing_thread.wait()
             except RuntimeError:
                 # Thread already deleted
                 pass
        
        self.processing_thread = QThread()
        self.worker = MediaProcessorWorker(file_path)
        self.worker.moveToThread(self.processing_thread)
        
        self.processing_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_single_file_processed)
        self.worker.error.connect(self.on_processing_error)
        self.worker.progress.connect(self.on_processing_progress)
        self.worker.finished.connect(self.processing_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.processing_thread.finished.connect(self.processing_thread.deleteLater)
        
        self.processing_thread.start()

    def on_single_file_processed(self, content, file_type):
        if self.active_context:
             self.active_context += "\n\n--- Next File ---\n\n"
        self.active_context += content
        self.active_file_type = file_type 
        self.process_next_file()

    def on_all_files_processed(self):
        self.run_btn.setText("Run")
        self.run_btn.setEnabled(True)
        self.input_field.setEnabled(True)
        self.upload_btn.setEnabled(True)
        
        count = len(self.active_file_paths)
        filenames = [os.path.basename(f) for f in self.active_file_paths]
        display_name = ", ".join(filenames)
        if len(display_name) > 50:
            display_name = f"{count} files selected"
            
        self.file_context_bar.set_text(f"📄 {display_name} - Ready")
        self.file_context_bar.setVisible(True)
        self.input_field.setFocus()
        
        self.append_output(f"✅ Analyzed {count} files. Total context length: {len(self.active_context)} chars.")
        
        InfoBar.success(
            title='Analysis Complete',
            content=f"Successfully processed {count} files",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )

    def on_processing_progress(self, message):
        total = len(self.active_file_paths)
        remaining = len(self.processing_queue)
        current = total - remaining
        self.run_btn.setText(f"Analyzing {current}/{total}...")
        self.append_output(f"ℹ️ {message}")

    def on_processing_error(self, error_msg):
        self.append_output(f"❌ Error analyzing file: {error_msg}")
        # Continue processing next file
        self.process_next_file()

    def clear_file_context(self):
        self.active_context = ""
        self.active_file_type = None
        self.active_file_paths = []
        self.file_context_bar.setVisible(False)

    def submit_command(self):
        text = self.input_field.text().strip()
        if text:
            # Ensure output view is shown
            self.output_stack.setCurrentIndex(1)
            
            display_text = text
            task_type = "command"
            
            if self.active_context:
                display_text = f"[With File Context] {text}"
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
                
                self.append_output(f"> {display_text}")
                self.command_submitted.emit(full_query, task_type)
            else:
                self.append_output(f"> {text}")
                self.command_submitted.emit(text, task_type)
                
            self.input_field.clear()
            
    def append_output(self, text, color=None):
        # Ensure output view is shown
        if self.output_stack.currentIndex() != 1:
             self.output_stack.setCurrentIndex(1)
             
        if "<table" in text and "</table>" in text:
            self.output_area.append(text)
        else:
            import html
            self.output_area.append(html.escape(text))
        
        self.output_area.moveCursor(QTextCursor.MoveOperation.End)

    def display_analysis_result(self, raw_data, html_content=None):
        self.last_analysis_data = raw_data
        self.export_btn.setEnabled(True)
        
        self.output_stack.setCurrentIndex(1)
        self.append_output("📊 Analysis Result:")
        
        if html_content:
            self.output_area.append(html_content)
            self.output_area.moveCursor(QTextCursor.MoveOperation.End)
