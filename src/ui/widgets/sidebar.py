from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QIcon
import qtawesome as qta

class ModernSidebar(QFrame):
    page_changed = Signal(int) # Index of page
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)  # Optimized width
        self.is_expanded = True
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # Header/Brand with icon
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(qta.icon('fa5s.terminal', color='#007ACC').pixmap(24, 24))
        header_layout.addWidget(header_icon)
        
        self.header_label = QLabel("PromptShell")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Navigation Buttons with icons
        self.nav_buttons = []
        self.add_nav_button("Terminal", "fa5s.terminal", 0, layout)
        self.add_nav_button("History", "fa5s.history", 1, layout)
        self.add_nav_button("Settings", "fa5s.cog", 2, layout)
        
        layout.addStretch()
        
        # Toggle Button (Bottom) with icon
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(qta.icon('fa5s.chevron-left', color='#007ACC'))
        self.toggle_btn.setIconSize(QSize(16, 16))
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        layout.addWidget(self.toggle_btn)
        
        self.setLayout(layout)

    def add_nav_button(self, text, icon_name, index, layout):
        btn = QPushButton(f"  {text}")
        
        # Store icon name for updates
        btn.setProperty("icon_name", icon_name)
        
        # Initial icon - VS Code blue
        btn.setIcon(qta.icon(icon_name, color='#007ACC'))
        btn.setIconSize(QSize(20, 20))
        
        btn.setProperty("page_index", index)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        
        # Handle click to update all icons
        btn.clicked.connect(lambda: self.page_changed.emit(index))
        btn.clicked.connect(self.update_icons)
        
        layout.addWidget(btn)
        self.nav_buttons.append(btn)
        
        # Set initial state
        if index == 0:
            btn.setChecked(True)
            # Update icon immediately for initial selection
            btn.setIcon(qta.icon(icon_name, color='white'))
            
    def update_icons(self):
        """Update icon colors based on checked state"""
        for btn in self.nav_buttons:
            icon_name = btn.property("icon_name")
            if btn.isChecked():
                # Active: White icon on blue background
                btn.setIcon(qta.icon(icon_name, color='white'))
            else:
                # Inactive: Blue icon on transparent/hover background
                btn.setIcon(qta.icon(icon_name, color='#007ACC'))
        
    def toggle_sidebar(self):
        width = 70 if self.is_expanded else 200  # Optimized width
        self.is_expanded = not self.is_expanded
        
        # Update toggle icon
        icon_name = 'fa5s.chevron-right' if not self.is_expanded else 'fa5s.chevron-left'
        self.toggle_btn.setIcon(qta.icon(icon_name, color='#007ACC'))
        
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Also animate max width
        self.setMaximumWidth(width)
        
        self.anim.start()
        
        # Update text visibility - hide text but keep icons
        for i, btn in enumerate(self.nav_buttons):
            if self.is_expanded:
                texts = ["  Terminal", "  History", "  Settings"]
                btn.setText(texts[i])
            else:
                btn.setText("")  # Hide text, icon remains visible
        
        # Update header visibility
        if self.is_expanded:
            self.header_label.show()
        else:
            self.header_label.hide()
