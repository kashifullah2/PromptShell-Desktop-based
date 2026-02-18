from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (ScrollArea, ComboBox, EditableComboBox, LineEdit, PrimaryPushButton, PushButton, 
                            StrongBodyLabel, CaptionLabel,  TitleLabel, TransparentToolButton, 
                            FluentIcon as FIF, InfoBar, InfoBarPosition, Theme, setTheme, SwitchButton)
from src.core.config import settings

class SettingsPage(ScrollArea):
    settings_saved = Signal()
    theme_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = QWidget(self)
        self.view.setObjectName("settings_view")
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("settings_page")
        
        # Transparent background to let FluentWindow theme show through
        self.setStyleSheet("""
            SettingsPage, #settings_view { 
                background-color: transparent; 
                border: none; 
            }
        """)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self.view)
        self.main_layout.setContentsMargins(36, 36, 36, 36)
        self.main_layout.setSpacing(24)
        
        # Header
        title = TitleLabel("Settings", self)
        subtitle = CaptionLabel("Configure your AI execution environment", self)
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(subtitle)
        
        self.main_layout.addSpacing(16)
        
        # Provider Config
        provider_group = self.create_group("AI Provider")
        
        # Provider Combo
        provider_label = StrongBodyLabel("Service Provider", self)
        self.provider_combo = ComboBox(self)
        self.provider_combo.addItems(["Groq", "OpenAI", "OpenRouter", "Gemini"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        provider_row = QHBoxLayout()
        provider_row.addWidget(provider_label)
        provider_row.addWidget(self.provider_combo, 1)
        provider_group.addLayout(provider_row)
        
        self.main_layout.addLayout(provider_group)
        
        # Model Config
        model_group = self.create_group("Model Configuration")
        
        # Model Name (Editable)
        model_label = StrongBodyLabel("Model Name", self)
        self.model_combo = EditableComboBox(self) 
 
        
        model_row = QHBoxLayout()
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_combo, 1)
        model_group.addLayout(model_row)
        
        self.main_layout.addLayout(model_group)
        
        # API Key Config
        key_group = self.create_group("Authentication")
        
        key_label = StrongBodyLabel("API Key", self)
        self.api_key_input = LineEdit(self)
        self.api_key_input.setPlaceholderText("Enter your API key here")
        self.api_key_input.setEchoMode(LineEdit.EchoMode.Password)
        self.api_key_input.setClearButtonEnabled(True)
        
        key_row = QHBoxLayout()
        key_row.addWidget(key_label)
        key_row.addWidget(self.api_key_input, 1)
        key_group.addLayout(key_row)
        
        self.main_layout.addLayout(key_group)
        
        # Theme Config
        theme_group = self.create_group("Appearance")
        
        theme_label = StrongBodyLabel("Dark Mode", self)
        self.theme_switch = SwitchButton(self)
        self.theme_switch.setOnText("On")
        self.theme_switch.setOffText("Off")
        self.theme_switch.checkedChanged.connect(self.toggle_theme)
        
        theme_row = QHBoxLayout()
        theme_row.addWidget(theme_label)
        theme_row.addStretch()
        theme_row.addWidget(self.theme_switch)
        theme_group.addLayout(theme_row)
        
        self.main_layout.addLayout(theme_group)
        
        self.main_layout.addStretch()
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.reset_btn = PushButton("Reset Defaults", self, FIF.SYNC)
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.save_btn = PrimaryPushButton("Save Settings", self, FIF.SAVE)
        self.save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.save_btn)
        
        self.main_layout.addLayout(button_layout)
        
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

    def create_group(self, title_text):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        # StrongBodyLabel is good
        header = StrongBodyLabel(title_text, self)
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        return layout

    def on_provider_changed(self, provider):
        """Update model dropdown when provider changes"""
        self.model_combo.clear()
        models = self.provider_models.get(provider, [])
        self.model_combo.addItems(models)
        # Set first model as default
        if models:
            self.model_combo.setCurrentIndex(0)
    
    def toggle_theme(self, checked):
        # We only support Dark really, but let's toggle between Dark and Light if user insists
        theme = Theme.DARK if checked else Theme.LIGHT
        setTheme(theme)
        self.theme_changed.emit("dark" if checked else "light")

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
        
        # Set model
        model_name = config.model_name
        self.model_combo.setText(model_name)
        
        self.api_key_input.setText(config.api_key)
        
        # Load theme
        theme = settings.config.theme
        self.theme_switch.setChecked(theme == "dark")

    def reset_to_defaults(self):
        self.provider_combo.setCurrentText("OpenRouter")
        self.on_provider_changed("OpenRouter")  # Update models
        self.model_combo.setCurrentIndex(0)  # First model
        self.api_key_input.clear()
        self.theme_switch.setChecked(True)

    def save_settings(self):
        provider = self.provider_combo.currentText().lower()
        model = self.model_combo.currentText().strip()
        api_key = self.api_key_input.text().strip()
        theme = "dark" if self.theme_switch.isChecked() else "light"
        
        if not model:
            InfoBar.warning(
                title='Validation Error',
                content="Model name is required.",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
            return
            
        settings.update_llm_config(provider, model, api_key)
        settings.set_theme(theme)
        
        InfoBar.success(
            title='Success',
            content="Settings saved successfully!",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self
        )
        
        self.settings_saved.emit()
