import os
import subprocess
from typing import Tuple, List


class CommandExecutor:
    """Executes shell commands with safety checks"""
    
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        'rm -rf /',
        'rm -rf /*',
        'mkfs',
        'dd if=',
        ':(){:|:&};:',  # Fork bomb
        'chmod -R 777 /',
        'wget http',  # Potentially dangerous downloads
        'curl http',
    ]
    
    # Moderately risky patterns
    RISKY_PATTERNS = [
        'rm -rf',
        'rm -r',
        'sudo rm',
        'chmod -R',
        'chown -R',
        '> /dev/sda',
        'mv /',
    ]
    
    def __init__(self):
        self.last_output = ""
        self.last_error = ""
    
    def is_dangerous(self, command: str) -> bool:
        """Check if command is dangerous"""
        cmd_lower = command.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in cmd_lower:
                return True
        return False
    
    def is_risky(self, command: str) -> bool:
        """Check if command is risky"""
        cmd_lower = command.lower()
        for pattern in self.RISKY_PATTERNS:
            if pattern.lower() in cmd_lower:
                return True
        return False
    
    def is_safe(self, command: str) -> bool:
        """Check if command is safe to execute"""
        return not (self.is_dangerous(command) or self.is_risky(command))
    
    def get_risk_level(self, command: str) -> str:
        """Get risk level: safe, risky, or dangerous"""
        if self.is_dangerous(command):
            return "dangerous"
        elif self.is_risky(command):
            return "risky"
        return "safe"
    
    def get_risk_explanation(self, command: str) -> str:
        """Get explanation of why command is risky"""
        cmd_lower = command.lower()
        
        if 'rm -rf /' in cmd_lower:
            return "This command will delete all files on your system!"
        elif 'rm -rf' in cmd_lower or 'rm -r' in cmd_lower:
            return "This command will recursively delete files. Make sure you specify the correct path."
        elif 'chmod -R 777' in cmd_lower:
            return "This command will make all files world-writable, which is a security risk."
        elif 'sudo' in cmd_lower:
            return "This command runs with administrator privileges. Verify it's correct."
        elif 'dd if=' in cmd_lower:
            return "This command can overwrite disk data. Double-check the parameters."
        elif 'mkfs' in cmd_lower:
            return "This command will format a disk, destroying all data on it."
        
        return "This command may have unintended consequences. Review carefully."
    
    def execute(self, command: str, cwd: str = None) -> Tuple[str, str]:
        """Execute a shell command and return (stdout, stderr)"""
        try:
            # Use shell=True to support pipes, redirects, etc.
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or os.getcwd(),
                timeout=30  # 30 second timeout
            )
            
            self.last_output = result.stdout
            self.last_error = result.stderr
            
            return result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            error = "Command timed out after 30 seconds"
            self.last_error = error
            return "", error
        except Exception as e:
            error = f"Execution error: {str(e)}"
            self.last_error = error
            return "", error
    
    def get_command_preview(self, command: str) -> dict:
        """Get detailed preview of what command will do"""
        parts = command.split()
        if not parts:
            return {"command": "", "description": "Empty command"}
        
        base_cmd = parts[0]
        
        previews = {
            'ls': "List directory contents",
            'cd': f"Change directory to: {parts[1] if len(parts) > 1 else 'home'}",
            'mkdir': f"Create directory: {parts[1] if len(parts) > 1 else ''}",
            'rm': "Remove files/directories",
            'cp': "Copy files/directories",
            'mv': "Move/rename files/directories",
            'cat': "Display file contents",
            'grep': "Search for patterns in files",
            'find': "Search for files",
            'chmod': "Change file permissions",
            'chown': "Change file ownership",
            'git': "Git version control operation",
            'python': "Execute Python script",
            'pip': "Python package manager",
            'npm': "Node package manager",
            'docker': "Docker container operation",
        }
        
        return {
            "command": base_cmd,
            "description": previews.get(base_cmd, f"Execute: {base_cmd}"),
            "full_command": command,
            "risk_level": self.get_risk_level(command)
        }
