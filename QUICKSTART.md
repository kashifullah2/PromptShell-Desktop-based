# PromptShell Professional - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd PromptShell-Desktop-based
uv pip install -r requirements.txt --python /home/kashifullah/ai/bin/python
```

### Step 2: Configure Your LLM Provider
```bash
python main.py
```
1. Click **Settings** in the sidebar
2. Choose your provider (Groq, OpenAI, OpenRouter, or Gemini)
3. Enter model name (e.g., `mixtral-8x7b-32768` for Groq)
4. Enter your API key
5. Click **Save**

### Step 3: Start Using!
1. Type a command in natural language
   - Example: "find all Python files modified today"
2. Click **Run** or press Enter
3. Review the generated command
4. Command executes automatically if safe

## 🎯 Quick Tips

### Terminal Usage
- **Enter**: Submit command
- **↑/↓**: Navigate history (coming soon)
- **Esc**: Clear input

### Navigation
- **Terminal**: Main command interface
- **History**: Browse past commands
- **Settings**: Configure LLM provider

### Safety Features
- 🟢 **Safe**: Auto-executes (ls, cat, grep, etc.)
- 🟡 **Risky**: Shows warning (rm, chmod, etc.)
- 🔴 **Dangerous**: Requires manual review (rm -rf, dd, etc.)

## 📝 Example Commands

Try these natural language requests:

```
"list all files in the current directory"
"show disk usage"
"find Python files larger than 1MB"
"count lines in all JavaScript files"
"show running processes"
"check system memory"
```

## ⚙️ Configuration File

Your settings are stored at: `~/.promptshell/config.json`

Example configuration:
```json
{
    "theme": "dark",
    "llm": {
        "provider": "groq",
        "model_name": "mixtral-8x7b-32768",
        "api_key": "gsk_...",
        "temperature": 0.1
    },
    "history_limit": 1000
}
```

## 🔑 Getting API Keys

### Groq (Recommended - Free & Fast)
1. Visit: https://console.groq.com
2. Sign up for free account
3. Go to API Keys section
4. Create new key
5. Use model: `mixtral-8x7b-32768`

### OpenAI
1. Visit: https://platform.openai.com
2. Create account
3. Add payment method
4. Generate API key
5. Use model: `gpt-4` or `gpt-3.5-turbo`

### OpenRouter
1. Visit: https://openrouter.ai
2. Sign up
3. Get API key
4. Use any supported model

### Gemini
1. Visit: https://makersuite.google.com
2. Get API key
3. Use model: `gemini-pro`

## 🧪 Testing

Run the test suite to verify everything works:
```bash
python test_app.py
```

Expected output:
```
==================================================
PromptShell Professional - Test Suite
==================================================
Testing Configuration Manager...
  ✓ Config loaded
Testing Command History...
  ✓ History entries
Testing Command Executor...
  ✓ Risk assessment
Testing LLM Factory...
  ✓ Available providers
Testing UI Widgets...
  ✓ All widgets imported
==================================================
Results: 5 passed, 0 failed
==================================================
```

## 🐛 Troubleshooting

### "LLM not configured"
→ Open Settings and add your API key

### "Command failed to execute"
→ Check the command syntax in terminal output

### UI not responding
→ Check terminal for error messages
→ Restart the application

### Import errors
→ Reinstall dependencies: `pip install -r requirements.txt`

## 📚 Learn More

- **README.md**: Full documentation
- **REFACTORING_SUMMARY.md**: Technical details
- **GitHub**: https://github.com/kashifullah2/PromptShell-Desktop-based

---

**Happy commanding! 🎉**
