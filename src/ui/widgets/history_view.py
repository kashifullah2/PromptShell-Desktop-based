from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton, QHBoxLayout, QListWidgetItem
)
from PySide6.QtCore import Signal, QSize, Qt
from src.core.history import CommandHistory
import qtawesome as qta
from datetime import datetime

class HistoryWidget(QWidget):
    command_selected = Signal(str)
    
    def __init__(self, history_manager: CommandHistory, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        
        # Header with icon and refresh button
        header_layout = QHBoxLayout()
        
        # Left side - icon and title
        left_header = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(qta.icon('fa5s.history', color='#007ACC').pixmap(20, 20))
        left_header.addWidget(header_icon)
        
        header_label = QLabel("Command History")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_header.addWidget(header_label)
        
        header_layout.addLayout(left_header)
        header_layout.addStretch()
        
        # Right side - compact refresh button
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#007ACC'))
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.setToolTip("Refresh History")
        self.refresh_btn.setFixedSize(36, 36)
        self.refresh_btn.clicked.connect(self.refresh_history)
        header_layout.addWidget(self.refresh_btn)
        
        # List widget with better styling
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setAlternatingRowColors(True)
        
        layout = QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        
        self.refresh_history()
        
    def refresh_history(self):
        self.list_widget.clear()
        recent = self.history_manager.get_recent(50)
        for entry in recent:
            cmd = entry.get('command') or entry.get('command_shell', '')
            if cmd:
                # Add timestamp if available
                timestamp = entry.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = dt.strftime("%H:%M:%S")
                        display_text = f"{time_str}  │  {cmd}"
                    except:
                        display_text = cmd
                else:
                    display_text = cmd
                
                item = QListWidgetItem(display_text)
                self.list_widget.addItem(item)
                
    def on_item_clicked(self, item):
        # Extract command (remove timestamp if present)
        text = item.text()
        if '│' in text:
            cmd = text.split('│', 1)[1].strip()
        else:
            cmd = text
        self.command_selected.emit(cmd)

