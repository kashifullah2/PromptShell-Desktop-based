from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, 
                               QPushButton, QFormLayout, QDialogButtonBox, QMessageBox, QHBoxLayout)
from PySide6.QtCore import Qt, QSize
from src.core.config import settings
import qtawesome as qta

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(qta.icon('fa5s.cog', color='#3B82F6').pixmap(24, 24))
        header_layout.addWidget(header_icon)
        
        header_label = QLabel("LLM Configuration")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E5E7EB;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        form_layout = QFormLayout()
        
        # Provider with icon
        provider_layout = QHBoxLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Groq", "OpenAI", "OpenRouter", "Gemini"])
        self.provider_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #4B5563;
                border-radius: 5px;
                background-color: #2A2A3E;
                color: #E5E7EB;
            }
            QComboBox:hover {
                border-color: #3B82F6;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A3E;
                color: #E5E7EB;
                selection-background-color: #3B82F6;
            }
        """)
        provider_layout.addWidget(self.provider_combo)
        
        provider_label = QLabel()
        provider_label.setPixmap(qta.icon('fa5s.server', color='#9CA3AF').pixmap(16, 16))
        provider_layout.addWidget(provider_label)
        
        provider_text = QLabel("Provider:")
        provider_text.setStyleSheet("color: #D1D5DB; font-weight: 500;")
        form_layout.addRow(provider_text, provider_layout)
        
        # Model Name with icon
        model_layout = QHBoxLayout()
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g. gpt-4, openai/gpt-oss-120b")
        self.model_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #4B5563;
                border-radius: 5px;
                background-color: #2A2A3E;
                color: #E5E7EB;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QLineEdit::placeholder {
                color: #6B7280;
            }
        """)
        model_layout.addWidget(self.model_input)
        
        model_label = QLabel()
        model_label.setPixmap(qta.icon('fa5s.brain', color='#9CA3AF').pixmap(16, 16))
        model_layout.addWidget(model_label)
        
        model_text = QLabel("Model Name:")
        model_text.setStyleSheet("color: #D1D5DB; font-weight: 500;")
        form_layout.addRow(model_text, model_layout)
        
        # API Key with icon
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #4B5563;
                border-radius: 5px;
                background-color: #2A2A3E;
                color: #E5E7EB;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QLineEdit::placeholder {
                color: #6B7280;
            }
        """)
        key_layout.addWidget(self.api_key_input)
        
        key_label = QLabel()
        key_label.setPixmap(qta.icon('fa5s.key', color='#9CA3AF').pixmap(16, 16))
        key_layout.addWidget(key_label)
        
        key_text = QLabel("API Key:")
        key_text.setStyleSheet("color: #D1D5DB; font-weight: 500;")
        form_layout.addRow(key_text, key_layout)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Custom buttons with icons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(" Cancel")
        cancel_btn.setIcon(qta.icon('fa5s.times', color='#9CA3AF'))
        cancel_btn.setIconSize(QSize(16, 16))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A2A3E;
                color: #9CA3AF;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #363650;
                color: #E5E7EB;
            }
        """)
        
        save_btn = QPushButton(" Save")
        save_btn.setIcon(qta.icon('fa5s.check', color='white'))
        save_btn.setIconSize(QSize(16, 16))
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Dialog styling - Dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E2F;
            }
            QLabel {
                color: #E5E7EB;
            }
        """)

    def load_settings(self):
        config = settings.config.llm
        
        # Map lowercase provider names to display names
        provider_map = {
            "groq": "Groq",
            "openai": "OpenAI",
            "openrouter": "OpenRouter",
            "gemini": "Gemini"
        }
        text = provider_map.get(config.provider.lower(), "OpenRouter")
        self.provider_combo.setCurrentText(text)
        
        self.model_input.setText(config.model_name)
        self.api_key_input.setText(config.api_key)

    def save_settings(self):
        provider = self.provider_combo.currentText().lower()
        model = self.model_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not model:
            QMessageBox.warning(self, "Validation Error", "Model name is required.")
            return
            
        settings.update_llm_config(provider, model, api_key)
        self.accept()
