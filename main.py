import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QScrollArea, 
                             QLabel, QFrame, QMessageBox, QGraphicsDropShadowEffect, 
                             QSizePolicy, QListWidget, QListWidgetItem, QSplitter,
                             QCompleter, QDialog, QDialogButtonBox, QTextEdit,
                             QTreeWidget, QTreeWidgetItem, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QStringListModel, QDir
from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat
from src.core.llm_engine import LLMEngine
from src.core.executor import CommandExecutor
from src.core.history import CommandHistory, AliasManager


# Professional Color Palette
class Theme:
    PRIMARY = "#2563EB"
    PRIMARY_DARK = "#1E40AF"
    PRIMARY_LIGHT = "#3B82F6"
    ACCENT = "#8B5CF6"
    SUCCESS = "#10B981"
    SUCCESS_DARK = "#059669"
    ERROR = "#EF4444"
    ERROR_DARK = "#DC2626"
    WARNING = "#F59E0B"
    BG_PRIMARY = "#0F172A"
    BG_SECONDARY = "#1E293B"
    BG_TERTIARY = "#334155"
    CARD_BG = "#1E293B"
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#CBD5E1"
    TEXT_MUTED = "#94A3B8"
    BORDER = "#334155"
    BORDER_LIGHT = "#475569"


class Typography:
    FONT_FAMILY = "Inter"
    FONT_FAMILY_MONO = "JetBrains Mono"
    SIZE_H1 = 24
    SIZE_H2 = 18
    SIZE_BODY = 14
    SIZE_SMALL = 12
    SIZE_TINY = 10
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


class CommandSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for shell commands"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Command format (first word)
        self.command_format = QTextCharFormat()
        self.command_format.setForeground(QColor(Theme.PRIMARY_LIGHT))
        self.command_format.setFontWeight(Typography.WEIGHT_BOLD)
        
        # Option format (--, -)
        self.option_format = QTextCharFormat()
        self.option_format.setForeground(QColor(Theme.ACCENT))
        
        # String format (' ', " ")
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(Theme.SUCCESS))
        
        # Path format (/)
        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor(Theme.WARNING))
    
    def highlightBlock(self, text):
        # Highlight first word as command
        words = text.split()
        if words:
            self.setFormat(0, len(words[0]), self.command_format)
        
        # Highlight options
        import re
        for match in re.finditer(r'--?\w+', text):
            self.setFormat(match.start(), match.end() - match.start(), self.option_format)
        
        # Highlight strings
        for match in re.finditer(r'["\'].*?["\']', text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        
        # Highlight paths
        for match in re.finditer(r'/[\w/.-]+', text):
            self.setFormat(match.start(), match.end() - match.start(), self.path_format)


class CommandGeneratorThread(QThread):
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


class AliasDialog(QDialog):
    """Dialog for managing command aliases"""
    def __init__(self, alias_manager, parent=None):
        super().__init__(parent)
        self.alias_manager = alias_manager
        self.setWindowTitle("Manage Command Aliases")
        self.setMinimumSize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Command Aliases & Macros")
        title.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_H2, Typography.WEIGHT_BOLD))
        layout.addWidget(title)
        
        # Alias list
        self.alias_list = QListWidget()
        self.alias_list.setFont(QFont(Typography.FONT_FAMILY_MONO, Typography.SIZE_SMALL))
        self.refresh_list()
        layout.addWidget(self.alias_list)
        
        # Add new alias
        add_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Alias name (e.g., 'update system')")
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Command (e.g., 'sudo apt update && sudo apt upgrade')")
        
        add_btn = QPushButton("Add Alias")
        add_btn.clicked.connect(self.add_alias)
        
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(self.command_input)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def refresh_list(self):
        self.alias_list.clear()
        for name, command in self.alias_manager.get_all_aliases().items():
            item = QListWidgetItem(f"{name} → {command}")
            self.alias_list.addItem(item)
    
    def add_alias(self):
        name = self.name_input.text().strip()
        command = self.command_input.text().strip()
        
        if name and command:
            self.alias_manager.add_alias(name, command)
            self.name_input.clear()
            self.command_input.clear()
            self.refresh_list()


class FileExplorerPanel(QFrame):
    """File explorer sidebar"""
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("File Explorer")
        header.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_BODY, Typography.WEIGHT_SEMIBOLD))
        header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; padding: 12px;")
        layout.addWidget(header)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_SMALL))
        self.tree.itemClicked.connect(self.on_item_clicked)
        
        # Populate with home directory
        self.populate_tree(os.path.expanduser("~"))
        
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_SECONDARY};
                border-right: 1px solid {Theme.BORDER};
            }}
            QTreeWidget {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT_SECONDARY};
                border: none;
            }}
            QTreeWidget::item:hover {{
                background-color: {Theme.BG_TERTIARY};
            }}
        """)
    
    def populate_tree(self, path):
        self.tree.clear()
        root = QTreeWidgetItem(self.tree, [os.path.basename(path) or path])
        root.setData(0, Qt.ItemDataRole.UserRole, path)
        self.add_children(root, path, max_depth=2)
        root.setExpanded(True)
    
    def add_children(self, parent_item, path, current_depth=0, max_depth=2):
        if current_depth >= max_depth:
            return
        
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                item_path = os.path.join(path, item)
                child = QTreeWidgetItem(parent_item, [item])
                child.setData(0, Qt.ItemDataRole.UserRole, item_path)
                
                if os.path.isdir(item_path):
                    self.add_children(child, item_path, current_depth + 1, max_depth)
        except PermissionError:
            pass
    
    def on_item_clicked(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.file_selected.emit(path)


class HistoryPanel(QFrame):
    """Command history sidebar"""
    command_selected = pyqtSignal(str)
    
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header
        header = QLabel("Command History")
        header.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_BODY, Typography.WEIGHT_SEMIBOLD))
        header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(header)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history...")
        self.search_input.textChanged.connect(self.filter_history)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        layout.addWidget(self.search_input)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setFont(QFont(Typography.FONT_FAMILY_MONO, Typography.SIZE_SMALL))
        self.history_list.itemClicked.connect(self.on_item_clicked)
        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT_SECONDARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.BORDER};
            }}
            QListWidget::item:hover {{
                background-color: {Theme.BG_TERTIARY};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.PRIMARY};
            }}
        """)
        
        self.refresh_history()
        layout.addWidget(self.history_list)
        
        # Clear button
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ERROR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ERROR_DARK};
            }}
        """)
        layout.addWidget(clear_btn)
        
        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {Theme.BG_SECONDARY};")
    
    def refresh_history(self):
        self.history_list.clear()
        for entry in self.history_manager.get_recent(20):
            item = QListWidgetItem(entry['command'])
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
    
    def filter_history(self, query):
        if not query:
            self.refresh_history()
            return
        
        self.history_list.clear()
        for entry in self.history_manager.search(query):
            item = QListWidgetItem(entry['command'])
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
    
    def on_item_clicked(self, item):
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            self.command_selected.emit(entry['command'])
    
    def clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all command history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history_manager.clear()
            self.refresh_history()


class CommandPreviewCard(QFrame):
    """Command preview with safety check"""
    execute_confirmed = pyqtSignal()
    
    def __init__(self, command_obj, executor, parent=None):
        super().__init__(parent)
        self.command_obj = command_obj
        self.executor = executor
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Risk assessment
        risk_level = self.executor.get_risk_level(self.command_obj.command_shell)
        
        if risk_level == "dangerous":
            risk_color = Theme.ERROR
            risk_text = "DANGEROUS"
        elif risk_level == "risky":
            risk_color = Theme.WARNING
            risk_text = "RISKY"
        else:
            risk_color = Theme.SUCCESS
            risk_text = "SAFE"
        
        risk_label = QLabel(f"Risk Level: {risk_text}")
        risk_label.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_SMALL, Typography.WEIGHT_BOLD))
        risk_label.setStyleSheet(f"color: {risk_color}; padding: 4px 8px; background-color: {Theme.BG_PRIMARY}; border-radius: 4px;")
        layout.addWidget(risk_label)
        
        # Command display with syntax highlighting
        cmd_label = QLabel("Command to Execute:")
        cmd_label.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_TINY, Typography.WEIGHT_SEMIBOLD))
        cmd_label.setStyleSheet(f"color: {Theme.TEXT_MUTED};")
        layout.addWidget(cmd_label)
        
        cmd_text = QTextEdit()
        cmd_text.setPlainText(self.command_obj.command_shell)
        cmd_text.setReadOnly(True)
        cmd_text.setMaximumHeight(80)
        cmd_text.setFont(QFont(Typography.FONT_FAMILY_MONO, Typography.SIZE_BODY))
        
        # Apply syntax highlighting
        highlighter = CommandSyntaxHighlighter(cmd_text.document())
        
        cmd_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {risk_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout.addWidget(cmd_text)
        
        # Risk explanation
        if risk_level != "safe":
            warning_text = self.executor.get_risk_explanation(self.command_obj.command_shell)
            warning_label = QLabel(warning_text)
            warning_label.setWordWrap(True)
            warning_label.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_SMALL))
            warning_label.setStyleSheet(f"color: {risk_color}; padding: 8px; background-color: {Theme.BG_PRIMARY}; border-radius: 6px;")
            layout.addWidget(warning_label)
        
        # Explanation
        exp_label = QLabel(self.command_obj.explanation)
        exp_label.setWordWrap(True)
        exp_label.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_SMALL))
        exp_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        layout.addWidget(exp_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        execute_btn = QPushButton("Execute")
        execute_btn.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_BODY, Typography.WEIGHT_SEMIBOLD))
        execute_btn.clicked.connect(self.execute_confirmed.emit)
        execute_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {Theme.SUCCESS_DARK};
            }}
        """)
        
        copy_btn = QPushButton("Copy")
        copy_btn.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_BODY))
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.command_obj.command_shell))
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BG_TERTIARY};
            }}
        """)
        
        btn_layout.addWidget(execute_btn)
        btn_layout.addWidget(copy_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.CARD_BG};
                border: 1px solid {Theme.BORDER};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class PromptShellUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptShell - Professional AI Terminal Assistant")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1200, 700)
        
        # Core components
        try:
            self.llm = LLMEngine()
        except ValueError as e:
            QMessageBox.critical(self, "Configuration Error", str(e))
            sys.exit(1)
        
        self.executor = CommandExecutor()
        self.history_manager = CommandHistory()
        self.alias_manager = AliasManager()
        self.safe_mode = True
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left sidebar - File Explorer
        self.file_explorer = FileExplorerPanel()
        self.file_explorer.setMaximumWidth(250)
        self.file_explorer.file_selected.connect(self.on_file_selected)
        
        # Center - Main content
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setSpacing(0)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        center_layout.addWidget(header)
        
        # Chat area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {Theme.BG_PRIMARY};
            }}
            QScrollBar:vertical {{
                background: {Theme.BG_SECONDARY};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.PRIMARY};
                border-radius: 5px;
                min-height: 30px;
            }}
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(16)
        self.chat_layout.setContentsMargins(24, 24, 24, 24)
        self.chat_layout.addStretch()
        self.chat_container.setLayout(self.chat_layout)
        
        scroll.setWidget(self.chat_container)
        center_layout.addWidget(scroll)
        
        # Input area
        input_frame = self.create_input_area()
        center_layout.addWidget(input_frame)
        
        center_widget.setLayout(center_layout)
        
        # Right sidebar - History
        self.history_panel = HistoryPanel(self.history_manager)
        self.history_panel.setMaximumWidth(300)
        self.history_panel.command_selected.connect(self.on_history_selected)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.file_explorer)
        splitter.addWidget(center_widget)
        splitter.addWidget(self.history_panel)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Welcome message
        self.add_system_message("Welcome to PromptShell Professional. All 5 advanced features are now active.")
    
    def create_header(self):
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_SECONDARY};
                border-bottom: 1px solid {Theme.BORDER};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(24, 12, 24, 12)
        
        # Title
        title = QLabel("PromptShell Pro")
        title.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_H1, Typography.WEIGHT_BOLD))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        
        layout.addWidget(title)
        layout.addStretch()
        
        # Buttons
        alias_btn = QPushButton("Aliases")
        alias_btn.clicked.connect(self.show_alias_dialog)
        alias_btn.setStyleSheet(self.get_button_style())
        
        safe_btn = QPushButton("Safe Mode: ON")
        safe_btn.setCheckable(True)
        safe_btn.setChecked(True)
        safe_btn.clicked.connect(self.toggle_safe_mode)
        safe_btn.setStyleSheet(self.get_button_style(Theme.SUCCESS))
        self.safe_mode_btn = safe_btn
        
        layout.addWidget(alias_btn)
        layout.addWidget(safe_btn)
        
        header.setLayout(layout)
        return header
    
    def create_input_area(self):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_SECONDARY};
                border-top: 1px solid {Theme.BORDER};
                padding: 20px 24px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Input with autocomplete
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Describe what you want to do or use an alias...")
        self.input_field.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_BODY))
        self.input_field.setMinimumHeight(48)
        self.input_field.returnPressed.connect(self.handle_submit)
        
        # Setup autocomplete
        self.setup_autocomplete()
        
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT_PRIMARY};
                border: 2px solid {Theme.BORDER};
                border-radius: 10px;
                padding: 12px 16px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.PRIMARY};
            }}
        """)
        
        send_btn = QPushButton("Generate")
        send_btn.setMinimumWidth(140)
        send_btn.clicked.connect(self.handle_submit)
        send_btn.setStyleSheet(self.get_button_style(Theme.PRIMARY))
        self.send_btn = send_btn
        
        layout.addWidget(self.input_field)
        layout.addWidget(send_btn)
        
        frame.setLayout(layout)
        return frame
    
    def setup_autocomplete(self):
        """Setup autocomplete for input field"""
        suggestions = self.history_manager.get_autocomplete_suggestions("")
        suggestions.extend(self.alias_manager.get_all_aliases().keys())
        
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.input_field.setCompleter(completer)
        
        # Update suggestions as user types
        self.input_field.textChanged.connect(self.update_autocomplete)
    
    def update_autocomplete(self, text):
        """Update autocomplete suggestions"""
        suggestions = self.history_manager.get_autocomplete_suggestions(text)
        suggestions.extend([k for k in self.alias_manager.get_all_aliases().keys() if k.startswith(text.lower())])
        
        completer = QCompleter(list(set(suggestions)))
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.input_field.setCompleter(completer)
    
    def get_button_style(self, color=None):
        bg = color or Theme.PRIMARY
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_LIGHT if not color else bg};
                opacity: 0.9;
            }}
        """
    
    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Theme.BG_PRIMARY};
            }}
            QWidget {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
    
    def show_alias_dialog(self):
        dialog = AliasDialog(self.alias_manager, self)
        dialog.exec()
        self.setup_autocomplete()  # Refresh autocomplete
    
    def toggle_safe_mode(self):
        self.safe_mode = self.safe_mode_btn.isChecked()
        self.safe_mode_btn.setText("Safe Mode: ON" if self.safe_mode else "Safe Mode: OFF")
        self.add_system_message(f"Safe mode {'enabled' if self.safe_mode else 'disabled'}")
    
    def on_file_selected(self, path):
        if os.path.isfile(path):
            self.input_field.setText(f"show me the contents of {path}")
        else:
            self.input_field.setText(f"list files in {path}")
    
    def on_history_selected(self, command):
        self.input_field.setText(command)
    
    def add_system_message(self, text):
        label = QLabel(text)
        label.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_SMALL))
        label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; padding: 6px 0;")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, label)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def add_command_preview(self, command_obj):
        card = CommandPreviewCard(command_obj, self.executor, self)
        card.execute_confirmed.connect(lambda: self.execute_command(command_obj))
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, card)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def execute_command(self, command_obj):
        self.add_system_message(f"Executing: {command_obj.command_shell}")
        stdout, stderr = self.executor.execute(command_obj.command_shell)
        
        if stdout:
            self.add_output(stdout)
        if stderr:
            self.add_error(stderr)
        
        # Add to history
        self.history_manager.add_entry(
            command_obj.command_nlp,
            command_obj.command_shell,
            success=not bool(stderr)
        )
        self.history_panel.refresh_history()
    
    def add_output(self, text):
        label = QLabel(text)
        label.setFont(QFont(Typography.FONT_FAMILY_MONO, Typography.SIZE_SMALL))
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            background-color: {Theme.BG_SECONDARY};
            border-left: 3px solid {Theme.SUCCESS};
            padding: 12px;
            border-radius: 6px;
        """)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, label)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def add_error(self, text):
        label = QLabel(text)
        label.setFont(QFont(Typography.FONT_FAMILY_MONO, Typography.SIZE_SMALL))
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            color: {Theme.ERROR};
            background-color: {Theme.BG_SECONDARY};
            border-left: 3px solid {Theme.ERROR};
            padding: 12px;
            border-radius: 6px;
        """)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, label)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        scroll = self.centralWidget().findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    
    def handle_submit(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        
        # Check for alias expansion
        expanded = self.alias_manager.expand_alias(user_text)
        if expanded != user_text:
            self.add_system_message(f"Alias expanded: '{user_text}' → '{expanded}'")
            user_text = expanded
        
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Processing...")
        
        self.add_system_message(f"Request: {user_text}")
        
        self.worker = CommandGeneratorThread(self.llm, user_text)
        self.worker.finished.connect(self.on_command_generated)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_command_generated(self, command_obj):
        self.add_command_preview(command_obj)
        
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Generate")
        self.input_field.setFocus()
    
    def on_error(self, error_msg):
        self.add_error(f"Error: {error_msg}")
        
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Generate")
        self.input_field.setFocus()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont(Typography.FONT_FAMILY, Typography.SIZE_BODY))
    
    window = PromptShellUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()