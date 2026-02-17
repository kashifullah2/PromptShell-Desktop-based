# PromptShell Professional - AI Terminal Assistant

A modern, professional desktop application for AI-powered terminal command generation built with PySide6.

## Features

### 🎨 **Modern UI/UX**
- **Dark Theme**: Professional dark mode with #1E1E2F background
- **Smooth Animations**: Sidebar collapse/expand with cubic easing
- **Responsive Layout**: Resizable panels and windows
- **Professional Styling**: Rounded corners, subtle shadows, modern fonts

### 🤖 **Multi-Provider LLM Support**
- **Groq**: Fast inference with Mixtral models
- **OpenAI**: GPT-4 and other OpenAI models
- **OpenRouter**: Access to multiple model providers
- **Gemini**: Google's Gemini models

### 💻 **Terminal Features**
- **Command Generation**: Natural language to shell commands
- **Syntax Highlighting**: Colored output for commands and responses
- **Command History**: Browse and reuse past commands
- **Safety Checks**: Automatic detection of dangerous commands
- **Threaded Execution**: Non-blocking UI during LLM calls

### ⚙️ **Configuration**
- **Secure Settings**: API keys stored in `~/.promptshell/config.json`
- **Easy Switching**: Change providers and models on the fly
- **Persistent Config**: Settings saved automatically

## Installation

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/kashifullah2/PromptShell-Desktop-based.git
cd PromptShell-Desktop-based
```

2. **Install dependencies**
```bash
# Using uv (recommended)
uv pip install -r requirements.txt --python /path/to/your/python

# Or using pip
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

## Usage

### First Time Setup

1. Click the **Settings** button in the sidebar
2. Select your preferred LLM provider
3. Enter the model name (e.g., `gpt-4`, `mixtral-8x7b-32768`)
4. Enter your API key
5. Click **Save**

### Using the Terminal

1. Type your command request in natural language
   - Example: "list all Python files in the current directory"
2. Click **Run** or press Enter
3. Review the generated command
4. The command will auto-execute if deemed safe

### Command History

1. Click **History** in the sidebar
2. Browse past commands
3. Click any command to reuse it

## Architecture

```
PromptShell-Desktop-based/
├── main.py                          # Application entry point
├── requirements.txt                 # Dependencies
├── src/
│   ├── core/                        # Core logic
│   │   ├── config.py               # Configuration management
│   │   ├── executor.py             # Command execution
│   │   ├── history.py              # Command history
│   │   ├── worker.py               # Background threading
│   │   ├── llm_engine.py           # LLM interface
│   │   └── llm/
│   │       └── factory.py          # LLM provider factory
│   └── ui/                          # User interface
│       ├── main_window.py          # Main application window
│       ├── settings_dialog.py      # Settings configuration
│       └── widgets/
│           ├── sidebar.py          # Navigation sidebar
│           ├── terminal.py         # Terminal widget
│           └── history_view.py     # History browser
└── .promptshell/                    # User config (created at runtime)
    └── config.json                  # Settings and API keys
```

## Technology Stack

- **UI Framework**: PySide6
- **LLM Integration**: LangChain
- **Providers**: Groq, OpenAI, OpenRouter, Gemini
- **Language**: Python 3.11
- **Fonts**: Segoe UI, Fira Code (monospace)

## Configuration File

Located at `~/.promptshell/config.json`:

```json
{
    "theme": "dark",
    "llm": {
        "provider": "groq",
        "model_name": "mixtral-8x7b-32768",
        "api_key": "your_api_key_here",
        "temperature": 0.1
    },
    "history_limit": 1000
}
```

## Keyboard Shortcuts

- **Enter**: Submit command
- **↑/↓**: Navigate command history (in input field)
- **Esc**: Clear input field

## Development

### Project Structure

- **Modular Architecture**: Separated core logic from UI
- **Factory Pattern**: LLM provider abstraction
- **Threading**: Background workers for responsive UI
- **Configuration Management**: Centralized settings

### Adding a New LLM Provider

1. Create provider class in `src/core/llm/factory.py`
2. Implement `create_client()` method
3. Add to `LLMFactory.PROVIDERS` dict
4. Update settings dialog dropdown

## Troubleshooting

### LLM Not Initialized
- Check that API key is set in Settings
- Verify provider and model name are correct
- Check internet connection

### Command Not Executing
- Review safety warnings
- Check command syntax
- Verify executor permissions

### UI Not Responsive
- Commands run in background threads
- Check terminal output for errors
- Restart application if needed

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- **GitHub Issues**: [Report bugs](https://github.com/kashifullah2/PromptShell-Desktop-based/issues)
- **Email**: kashifullah2@example.com

## Acknowledgments

- **PySide6** for the UI framework
- **LangChain** for LLM integration
- **Groq**, **OpenAI**, **OpenRouter**, **Google** for AI capabilities

---

**Built with ❤️ by Kashif Ullah**