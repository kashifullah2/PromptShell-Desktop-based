# PromptShell Professional - AI Terminal Assistant

A professional, enterprise-grade AI-powered terminal assistant built with PyQt6 and Groq AI.

## Features

### 1. **Command History & Autocomplete** ✨
- Scrollable command history in right sidebar
- Search functionality to filter past commands
- Smart autocomplete suggestions as you type
- Click any history item to reuse commands
- Persistent storage across sessions

### 2. **Command Preview / Safety Check** 🛡️
- **Risk Level Analysis**: Commands are classified as SAFE, RISKY, or DANGEROUS
- **Visual Warnings**: Color-coded indicators (Green/Yellow/Red)
- **Detailed Explanations**: Understand why a command might be risky
- **Preview Before Execution**: See exactly what will run
- **Confirmation Dialogs**: Extra protection for dangerous operations
- Checks for patterns like `rm -rf`, `sudo`, `dd`, `chmod 777`, etc.

### 3. **Syntax Highlighting & Output Styling** 🎨
- **Command Highlighting**: First word highlighted in blue
- **Option Highlighting**: Flags (--flag, -f) in purple
- **String Highlighting**: Quoted text in green
- **Path Highlighting**: File paths in amber
- **Monospace Output**: Professional JetBrains Mono font
- **Styled Results**: Color-coded output and errors with borders

### 4. **File Explorer / Quick Access Panel** 📁
- **Left Sidebar**: Directory tree navigation
- **Quick Navigation**: Starts at home directory
- **Click to Use**: Clicking files/folders auto-populates input
- **Smart Suggestions**: 
  - Files → "show me the contents of..."
  - Directories → "list files in..."
- **Resizable**: Adjust panel size via splitter

### 5. **Custom Command Aliases & Macros** ⚡
- **Alias Manager**: Dedicated dialog for managing shortcuts
- **Custom Shortcuts**: Create aliases like "update system" → `sudo apt update && sudo apt upgrade`
- **Auto-Expansion**: Aliases automatically expand when used
- **Autocomplete Integration**: Aliases appear in suggestions
- **Persistent Storage**: Saved to `command_aliases.json`
- **Visual Feedback**: Shows when an alias is expanded

## Installation

### Prerequisites
- Python 3.11+
- Groq API Key

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/kashifullah2/PromptShell-Desktop-based.git
cd PromptShell-Desktop-based
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

5. **Run the application**
```bash
python main.py
```

## Usage

### Basic Workflow

1. **Describe Your Task**: Type what you want to do in natural language
   - Example: "Find all Python files modified in the last 7 days"

2. **Review Command**: The AI generates a command with:
   - Risk level assessment
   - Syntax-highlighted preview
   - Detailed explanation

3. **Execute or Copy**: 
   - Click "Execute" to run immediately
   - Click "Copy" to copy to clipboard

### Using Aliases

1. Click the "Aliases" button in the header
2. Add a new alias:
   - **Name**: `update system`
   - **Command**: `sudo apt update && sudo apt upgrade`
3. Type the alias name in the input field
4. The command automatically expands

### Using History

1. Browse recent commands in the right sidebar
2. Use the search box to filter
3. Click any command to reuse it
4. Clear history with the "Clear History" button

### File Explorer

1. Navigate directories in the left sidebar
2. Click a file to generate "show contents" command
3. Click a directory to generate "list files" command
4. Resize panels by dragging the splitter

## Architecture

```
PromptShell-Desktop-based/
├── main.py                 # Main application UI
├── src/
│   ├── core/
│   │   ├── llm_engine.py   # Groq AI integration
│   │   ├── executor.py     # Command execution & safety
│   │   ├── history.py      # History & alias management
│   │   └── config.py       # Configuration
│   └── ui/
│       ├── app_layout.py   # (Legacy)
│       └── components.py   # (Legacy)
├── requirements.txt
├── .env                    # API keys (not in git)
├── .gitignore
└── README.md
```

## Technology Stack

- **UI Framework**: PyQt6
- **AI Model**: Groq (qwen/qwen3-32b)
- **Language**: Python 3.11
- **Fonts**: Inter, JetBrains Mono
- **Design**: Tailwind-inspired color system

## Professional Design Features

- **Typography**: Inter for UI, JetBrains Mono for code
- **Color Palette**: Tailwind-inspired professional colors
- **Spacing**: Consistent 16-32px margins
- **Shadows**: Subtle depth effects
- **Responsive**: Minimum 1200x700 resolution
- **Accessibility**: WCAG-compliant contrast ratios

## Safety Features

- **Safe Mode**: Toggle to require confirmation for risky commands
- **Risk Analysis**: Automatic detection of dangerous patterns
- **Command Preview**: See before you execute
- **Execution Timeout**: 30-second limit
- **Error Handling**: Clear error messages

## Data Storage

- `promptshell_history.json`: Command history (max 100 entries)
- `command_aliases.json`: Custom aliases and macros

## Keyboard Shortcuts

- **Enter**: Submit command / Generate
- **Ctrl+C**: Copy selected text
- **Esc**: Clear input field

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/kashifullah2/PromptShell-Desktop-based/issues)
- Email: kashifullah2@example.com

## Acknowledgments

- Groq for AI capabilities
- PyQt6 for the UI framework
- Tailwind CSS for design inspiration

---

**Made with ❤️ by Kashif Ullah**