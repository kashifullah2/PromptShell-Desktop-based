from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea)
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (ScrollArea, ComboBox, EditableComboBox, LineEdit, PrimaryPushButton, PushButton, 
                            StrongBodyLabel, CaptionLabel, TitleLabel, TransparentToolButton, 
                            FluentIcon as FIF, InfoBar, InfoBarPosition, Theme, setTheme, SwitchButton,
                            SettingCardGroup, SettingCard, SwitchSettingCard, ComboBoxSettingCard, 
                            OptionsSettingCard, ExpandLayout, TextEdit)
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
        
        # Transparent background for ScrollArea to blend with FluentWindow
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
        
        # --- AI Provider ---
        self.provider_group = SettingCardGroup("AI Provider", self)
        
        # Provider Card (Using base SettingCard with custom ComboBox)
        self.provider_card = SettingCard(
            FIF.ROBOT,
            "Service Provider",
            "Select the AI service provider you want to use",
            parent=self.provider_group
        )
        
        self.provider_combo = ComboBox(self.provider_card)
        self.provider_combo.addItems(["Groq", "OpenAI", "OpenRouter", "Gemini"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        # Add to card layout
        # SettingCard typically has a hBoxLayout for content
        self.provider_card.hBoxLayout.addWidget(self.provider_combo, 0, Qt.AlignRight)
        self.provider_card.hBoxLayout.addSpacing(16)
        
        self.provider_group.addSettingCard(self.provider_card)
        
        # Model Card
        self.model_card = SettingCard(
            FIF.SEARCH,
            "Model Selection",
            "Choose the specific model to run commands",
            parent=self.provider_group
        )
        
        self.model_combo = EditableComboBox(self.model_card) # Use EditableComboBox for flexibility
        
        self.model_card.hBoxLayout.addWidget(self.model_combo, 0, Qt.AlignRight)
        self.model_card.hBoxLayout.addSpacing(16)
        
        self.provider_group.addSettingCard(self.model_card)
        
        self.main_layout.addWidget(self.provider_group)
        
        # --- Authentication ---
        self.auth_group = SettingCardGroup("Authentication", self)
        
        # API Key Card
        self.api_key_card = SettingCard(FIF.VPN, "API Key", "Enter your secret API key for the selected provider", self.auth_group)
        self.api_key_input = LineEdit(self.api_key_card)
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setEchoMode(LineEdit.EchoMode.Password)
        self.api_key_input.setClearButtonEnabled(True)
        self.api_key_input.setFixedWidth(300)
        
        self.api_key_card.hBoxLayout.addWidget(self.api_key_input, 0, Qt.AlignRight)
        self.api_key_card.hBoxLayout.addSpacing(16)
        
        self.auth_group.addSettingCard(self.api_key_card)
        self.main_layout.addWidget(self.auth_group)
        
        # --- Appearance ---
        self.appearance_group = SettingCardGroup("Appearance", self)
        
        self.theme_card = SwitchSettingCard(
            FIF.BRUSH,
            "Dark Mode",
            "Toggle between Light and Dark themes",
            parent=self.appearance_group
        )
        self.theme_card.checkedChanged.connect(self.toggle_theme)
        self.appearance_group.addSettingCard(self.theme_card)
        
        self.main_layout.addWidget(self.appearance_group)
        
        self.main_layout.addStretch()
        
        # --- Footer Actions ---
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 24, 0, 0)
        button_layout.addStretch()
        
        self.reset_btn = PushButton("Reset Defaults", self, FIF.SYNC)
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.save_btn = PrimaryPushButton("Save Settings", self, FIF.SAVE)
        self.save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.save_btn)
        
        self.main_layout.addLayout(button_layout)
        
        # Data
        self.provider_models = {
            "Groq": ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
            "OpenAI": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-4o"],
            "OpenRouter": ["openai/gpt-4-turbo", "anthropic/claude-3-opus", "meta-llama/llama-3-70b-instruct", "google/gemini-pro"],
            "Gemini": ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
        }
        
        # Init with defaults if not loaded yet (will be overridden by load_settings immediately usually)
        # self.on_provider_changed(self.provider_combo.currentText())

    def on_provider_changed(self, provider):
        """Update model dropdown when provider changes"""
        self.model_combo.clear()
        models = self.provider_models.get(provider, [])
        self.model_combo.addItems(models)
        if models:
            self.model_combo.setCurrentIndex(0)

    def toggle_theme(self, checked):
        theme = Theme.DARK if checked else Theme.LIGHT
        setTheme(theme)
        self.theme_changed.emit("dark" if checked else "light")

    def load_settings(self):
        config = settings.config.llm
        
        # Provider
        provider_map = {"groq": "Groq", "openai": "OpenAI", "openrouter": "OpenRouter", "gemini": "Gemini"}
        text = provider_map.get(config.provider.lower(), "OpenRouter")
        self.provider_combo.setCurrentText(text)
        
        # Update models for the selected provider first
        self.on_provider_changed(text)
        
        # Model
        # Since we use EditableComboBox, we can just set text or find item
        model_name = config.model_name
        index = self.model_combo.findText(model_name)
        if index != -1:
            self.model_combo.setCurrentIndex(index)
        else:
            self.model_combo.addItem(model_name)
            self.model_combo.setCurrentText(model_name)
        
        # API Key
        self.api_key_input.setText(config.api_key)
        
        # Theme
        theme = settings.config.theme
        self.theme_card.setChecked(theme == "dark")

    def reset_to_defaults(self):
        self.provider_combo.setCurrentText("OpenRouter")
        self.on_provider_changed("OpenRouter")
        self.model_combo.setCurrentIndex(0)
        self.api_key_input.clear()
        self.theme_card.setChecked(True)

    def save_settings(self):
        provider = self.provider_combo.currentText().lower()
        model = self.model_combo.currentText().strip()
        api_key = self.api_key_input.text().strip()
        theme = "dark" if self.theme_card.isChecked() else "light"
        
        if not model:
            InfoBar.warning(title='Validation Error', content="Model name is required.", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.BOTTOM_RIGHT, duration=3000, parent=self)
            return
            
        settings.update_llm_config(provider, model, api_key)
        settings.set_theme(theme)
        
        InfoBar.success(title='Success', content="Settings saved successfully!", orient=Qt.Horizontal, isClosable=True, position=InfoBarPosition.BOTTOM_RIGHT, duration=2000, parent=self)
        self.settings_saved.emit()
