from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from src.core.history import CommandHistory
from qfluentwidgets import (ListWidget, ToolButton, FluentIcon as FIF, TitleLabel, 
                            StrongBodyLabel, CaptionLabel, CardWidget, TransparentToolButton)
from datetime import datetime

class HistoryWidget(QWidget):
    command_selected = Signal(str)
    
    def __init__(self, history_manager: CommandHistory, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setObjectName("history_view")
        
        self.init_ui()
        self.refresh_history()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = TitleLabel("Request History", self)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = TransparentToolButton(FIF.SYNC, self)
        refresh_btn.setToolTip("Refresh History")
        refresh_btn.clicked.connect(self.refresh_history)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # List Widget
        self.list_widget = ListWidget(self)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setAlternatingRowColors(True)
        # Using fluent style for list widget automatically due to theme
        
        layout.addWidget(self.list_widget)
        
        self.empty_label = StrongBodyLabel("No history available yet.", self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

    def refresh_history(self):
        self.list_widget.clear()
        recent = self.history_manager.get_recent(50)
        
        if not recent:
            self.empty_label.setVisible(True)
            self.list_widget.setVisible(False)
        else:
            self.empty_label.setVisible(False)
            self.list_widget.setVisible(True)
            
            for entry in recent:
                cmd = entry.get('command') or entry.get('command_shell', '')
                if cmd:
                    # Add timestamp if available
                    timestamp = entry.get('timestamp', '')
                    display_text = cmd
                    
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%H:%M")
                            display_text = f"[{time_str}] {cmd}"
                        except:
                            pass
                    
                    item = QListWidgetItem(display_text)
                    # We could store metadata in item if needed
                    # item.setData(Qt.UserRole, entry)
                    self.list_widget.addItem(item)
                
    def on_item_clicked(self, item):
        # Extract command (remove timestamp if present)
        text = item.text()
        extracted_cmd = text
        if ']' in text and text.startswith('['):
            # rudimentary extraction
            try:
                extracted_cmd = text.split(']', 1)[1].strip()
            except:
                pass
                
        self.command_selected.emit(extracted_cmd)
