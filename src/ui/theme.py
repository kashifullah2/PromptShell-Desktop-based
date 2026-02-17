"""
Theme Manager for PromptShell
Provides light and dark color palettes and theme switching
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class Theme:
    """Theme color palettes - VS Code inspired"""
    
    # Dark Theme - VS Code Dark+ theme
    DARK = {
        'bg_primary': '#1E1E1E',      # VS Code dark background
        'bg_secondary': '#252526',    # Sidebar background
        'bg_tertiary': '#2D2D30',     # Hover background
        'bg_card': '#252526',         # Card background
        'border': '#3E3E42',          # Border color
        'text_primary': '#CCCCCC',    # Primary text (light gray)
        'text_secondary': '#9D9D9D',  # Secondary text
        'text_tertiary': '#6A6A6A',   # Tertiary text (comments)
        'accent': '#007ACC',          # VS Code blue
        'accent_hover': '#005A9E',    # Darker blue
        'accent_alt': '#C586C0',      # Purple accent
        'button': '#0E639C',          # Button blue
        'button_hover': '#1177BB',    # Button hover
        'success': '#4EC9B0',         # Teal/cyan
        'warning': '#CE9178',         # Orange
        'error': '#F48771',           # Red/orange
        'input_bg': '#3C3C3C',        # Input background
        'input_border': '#3E3E42',    # Input border
    }
    
    # Light Theme - VS Code Light+ theme
    LIGHT = {
        'bg_primary': '#FFFFFF',      # Pure white
        'bg_secondary': '#F3F3F3',    # Sidebar background
        'bg_tertiary': '#E8E8E8',     # Hover background
        'bg_card': '#FFFFFF',         # White cards
        'border': '#E5E5E5',          # Light border
        'text_primary': '#000000',    # Black text
        'text_secondary': '#6A6A6A',  # Gray text
        'text_tertiary': '#999999',   # Light gray text
        'accent': '#0078D4',          # VS Code light blue
        'accent_hover': '#005A9E',    # Darker blue
        'accent_alt': '#AF00DB',      # Purple accent
        'button': '#0078D4',          # Button blue
        'button_hover': '#005A9E',    # Button hover
        'success': '#14CE14',         # Green
        'warning': '#F9A825',         # Amber
        'error': '#E51400',           # Red
        'input_bg': '#FFFFFF',        # White input
        'input_border': '#CECECE',    # Gray border
    }

class ThemeManager:
    """Manages application theme switching"""
    
    @staticmethod
    def get_stylesheet(theme_name: str) -> str:
        """Get complete stylesheet for theme"""
        colors = Theme.DARK if theme_name == "dark" else Theme.LIGHT
        
        return f"""
            /* Main Application */
            QMainWindow, QWidget {{
                background-color: {colors['bg_primary']};
                color: {colors['text_primary']};
            }}
            
            /* Sidebar */
            QFrame#sidebar {{
                background-color: {colors['bg_secondary']};
                border-right: 1px solid {colors['border']};
            }}
            
            QFrame#sidebar QPushButton {{
                text-align: left;
                padding: 12px 15px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                color: {colors['text_primary']};
            }}
            
            QFrame#sidebar QPushButton:hover {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_primary']};
            }}
            
            QFrame#sidebar QPushButton:checked {{
                background-color: {colors['accent']};
                color: #FFFFFF;
                font-weight: 600;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {colors['bg_card']};
                border-color: {colors['accent']};
            }}
            
            QPushButton:pressed {{
                background-color: {colors['bg_secondary']};
            }}
            
            QPushButton:checked {{
                background-color: {colors['accent']};
                color: white;
                border-color: {colors['accent']};
            }}
            
            /* Primary Button */
            QPushButton#primary {{
                background-color: {colors['button']};
                color: white;
                border: none;
                font-weight: 600;
                padding: 12px 24px;
            }}
            
            QPushButton#primary:hover {{
                background-color: {colors['button_hover']};
            }}
            
            /* Accent Button */
            QPushButton#accent {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                font-weight: 600;
            }}
            
            QPushButton#accent:hover {{
                background-color: {colors['accent_hover']};
            }}
            
            /* Input Fields */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {colors['input_bg']};
                color: {colors['text_primary']};
                border: 2px solid {colors['input_border']};
                border-radius: 8px;
                padding: 10px 12px;
                selection-background-color: {colors['accent']};
                font-size: 14px;
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors['accent']};
                background-color: {colors['bg_primary']};
            }}
            
            QLineEdit:hover, QTextEdit:hover {{
                border-color: {colors['accent_hover']};
            }}
            
            QLineEdit::placeholder {{
                color: {colors['text_tertiary']};
            }}
            
            /* ComboBox */
            QComboBox {{
                background-color: {colors['input_bg']};
                color: {colors['text_primary']};
                border: 2px solid {colors['input_border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
            }}
            
            QComboBox:hover {{
                border-color: {colors['accent']};
            }}
            
            QComboBox:focus {{
                border-color: {colors['accent']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {colors['text_secondary']};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors['bg_card']};
                color: {colors['text_primary']};
                selection-background-color: {colors['accent']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 4px;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {colors['bg_tertiary']};
            }}
            
            /* List Widget */
            QListWidget {{
                background-color: {colors['bg_primary']};
                color: {colors['text_primary']};
                border: none;
                border-radius: 8px;
            }}
            
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {colors['border']};
                border-radius: 0px;
            }}
            
            QListWidget::item:alternate {{
                background-color: {colors['bg_secondary']};
            }}
            
            QListWidget::item:hover {{
                background-color: {colors['bg_tertiary']};
            }}
            
            QListWidget::item:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
            
            QListWidget::item:selected:hover {{
                background-color: {colors['accent_hover']};
            }}
            
            /* Scroll Area */
            QScrollArea {{
                background-color: {colors['bg_primary']};
                border: none;
            }}
            
            /* Scroll Bar */
            QScrollBar:vertical {{
                background-color: {colors['bg_secondary']};
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['bg_tertiary']};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['accent']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {colors['bg_secondary']};
                height: 10px;
                border-radius: 5px;
                margin: 2px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {colors['bg_tertiary']};
                border-radius: 5px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {colors['accent']};
            }}
            
            /* Labels */
            QLabel {{
                color: {colors['text_primary']};
            }}
            
            QLabel#secondary {{
                color: {colors['text_secondary']};
            }}
            
            QLabel#tertiary {{
                color: {colors['text_tertiary']};
            }}
            
            /* Cards/Frames */
            QFrame#card {{
                background-color: {colors['bg_card']};
                border-radius: 12px;
                border: 1px solid {colors['border']};
                padding: 20px;
            }}
            
            /* Message Box */
            QMessageBox {{
                background-color: {colors['bg_card']};
            }}
            
            QMessageBox QLabel {{
                color: {colors['text_primary']};
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
                padding: 8px 16px;
            }}
            
            /* Stacked Widget */
            QStackedWidget {{
                background-color: {colors['bg_primary']};
            }}
            
            /* Form Labels */
            QFormLayout QLabel {{
                color: {colors['text_primary']};
                font-weight: 500;
            }}
        """
    
    @staticmethod
    def apply_theme(app: QApplication, theme_name: str):
        """Apply theme to application"""
        stylesheet = ThemeManager.get_stylesheet(theme_name)
        app.setStyleSheet(stylesheet)
        
        # Also set QPalette for native widgets
        palette = QPalette()
        colors = Theme.DARK if theme_name == "dark" else Theme.LIGHT
        
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['input_bg']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['text_primary']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#FFFFFF'))
        
        app.setPalette(palette)
