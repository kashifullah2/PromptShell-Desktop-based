from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QFormLayout, QMessageBox, QHBoxLayout, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QSize, Signal
from src.core.config import settings
import qtawesome as qta

class SettingsPage(QWidget):
    settings_saved = Signal()
    theme_changed = Signal(str)  # Emits theme name when changed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(qta.icon('fa5s.cog', color='#007ACC').pixmap(32, 32))
        header_layout.addWidget(header_icon)
        
        header_label = QLabel("Settings")
        header_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Subtitle
        subtitle = QLabel("Configure your LLM provider and model")
        subtitle.setObjectName("secondary")
        subtitle.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Settings card
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Provider dropdown
        provider_layout = QHBoxLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Groq", "OpenAI", "OpenRouter", "Gemini"])
        self.provider_combo.setMinimumHeight(45)
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        
        provider_text = QLabel("Provider:")
        provider_text.setStyleSheet("font-weight: 500; font-size: 14px;")
        form_layout.addRow(provider_text, provider_layout)
        
        # Model Name dropdown (dynamic based on provider)
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(45)
        self.model_combo.setEditable(True)  # Allow custom models
        model_layout.addWidget(self.model_combo)
        
        model_text = QLabel("Model Name:")
        model_text.setStyleSheet("font-weight: 500; font-size: 14px;")
        form_layout.addRow(model_text, model_layout)
        
        # Define model options for each provider
        self.provider_models = {
            "Groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "OpenAI": [
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-4o"
            ],
            "OpenRouter": [
                "openai/gpt-4-turbo",
                "anthropic/claude-3-opus",
                "meta-llama/llama-3-70b-instruct",
                "google/gemini-pro"
            ],
            "Gemini": [
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-ultra"
            ]
        }
        
        # Initialize with first provider's models
        self.on_provider_changed(self.provider_combo.currentText())
        
        # API Key
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setMinimumHeight(45)
        key_layout.addWidget(self.api_key_input)
        
        # Toggle password visibility
        self.show_key_btn = QPushButton()
        self.show_key_btn.setIcon(qta.icon('fa5s.eye', color='#007ACC'))
        self.show_key_btn.setIconSize(QSize(18, 18))
        self.show_key_btn.setFixedSize(45, 45)
        self.show_key_btn.clicked.connect(self.toggle_password_visibility)
        key_layout.addWidget(self.show_key_btn)
        
        key_text = QLabel("API Key:")
        key_text.setStyleSheet("font-weight: 500; font-size: 14px;")
        form_layout.addRow(key_text, key_layout)
        
        # Theme toggle
        theme_layout = QHBoxLayout()
        
        # Dark mode button
        self.dark_btn = QPushButton(" Dark Mode")
        self.dark_btn.setIcon(qta.icon('fa5s.moon', color='white'))
        self.dark_btn.setIconSize(QSize(18, 18))
        self.dark_btn.setCheckable(True)
        self.dark_btn.setMinimumHeight(45)
        self.dark_btn.clicked.connect(lambda: self.set_theme_mode("dark"))
        theme_layout.addWidget(self.dark_btn)
        
        # Light mode button
        self.light_btn = QPushButton(" Light Mode")
        self.light_btn.setIcon(qta.icon('fa5s.sun', color='white'))
        self.light_btn.setIconSize(QSize(18, 18))
        self.light_btn.setCheckable(True)
        self.light_btn.setMinimumHeight(45)
        self.light_btn.clicked.connect(lambda: self.set_theme_mode("light"))
        theme_layout.addWidget(self.light_btn)
        
        theme_layout.addStretch()
        
        theme_text = QLabel("Theme:")
        theme_text.setStyleSheet("font-weight: 500; font-size: 14px;")
        form_layout.addRow(theme_text, theme_layout)
        
        card_layout.addLayout(form_layout)
        card.setLayout(card_layout)
        layout.addWidget(card)
        
        layout.addSpacing(20)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Reset button
        reset_btn = QPushButton(" Reset to Defaults")
        reset_btn.setIcon(qta.icon('fa5s.undo', color='#007ACC'))
        reset_btn.setIconSize(QSize(16, 16))
        reset_btn.setMinimumHeight(45)
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        # Save button
        save_btn = QPushButton(" Save Settings")
        save_btn.setIcon(qta.icon('fa5s.check', color='white'))
        save_btn.setIconSize(QSize(16, 16))
        save_btn.setMinimumHeight(45)
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def toggle_password_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setIcon(qta.icon('fa5s.eye-slash', color='#007ACC'))
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setIcon(qta.icon('fa5s.eye', color='#007ACC'))
    
    def on_provider_changed(self, provider):
        """Update model dropdown when provider changes"""
        self.model_combo.clear()
        models = self.provider_models.get(provider, [])
        self.model_combo.addItems(models)
        # Set first model as default
        if models:
            self.model_combo.setCurrentIndex(0)
    
    def set_theme_mode(self, mode):
        """Set theme mode and update button states"""
        if mode == "dark":
            self.dark_btn.setChecked(True)
            self.light_btn.setChecked(False)
            # Update icons: Dark active (white), Light inactive (blue)
            self.dark_btn.setIcon(qta.icon('fa5s.moon', color='white'))
            self.light_btn.setIcon(qta.icon('fa5s.sun', color='#007ACC'))
        else:
            self.dark_btn.setChecked(False)
            self.light_btn.setChecked(True)
            # Update icons: Dark inactive (blue), Light active (white)
            self.dark_btn.setIcon(qta.icon('fa5s.moon', color='#007ACC'))
            self.light_btn.setIcon(qta.icon('fa5s.sun', color='white'))
        
        # Emit signal for live preview
        self.theme_changed.emit(mode)

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
        
        # Set model - will be in dropdown or can be custom
        model_name = config.model_name
        index = self.model_combo.findText(model_name)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        else:
            # Custom model not in list
            self.model_combo.setEditText(model_name)
        
        self.api_key_input.setText(config.api_key)
        
        # Load theme
        theme = settings.config.theme
        self.set_theme_mode(theme)

    def reset_to_defaults(self):
        self.provider_combo.setCurrentText("OpenRouter")
        self.on_provider_changed("OpenRouter")  # Update models
        self.model_combo.setCurrentIndex(0)  # First model
        self.api_key_input.clear()
        self.set_theme_mode("dark")

    def save_settings(self):
        provider = self.provider_combo.currentText().lower()
        model = self.model_combo.currentText().strip()  # Get from dropdown
        api_key = self.api_key_input.text().strip()
        theme = "dark" if self.dark_btn.isChecked() else "light"
        
        if not model:
            QMessageBox.warning(self, "Validation Error", "Model name is required.")
            return
            
        settings.update_llm_config(provider, model, api_key)
        settings.set_theme(theme)
        
        # Show success message
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText("Settings saved successfully!")
        msg.exec()
        
        self.settings_saved.emit()
