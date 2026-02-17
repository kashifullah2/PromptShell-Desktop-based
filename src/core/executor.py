import subprocess
import os

class CommandExecutor:
    BLACKLIST = [
        "rm ", "rmdir", ":(){ :|:& };:", "mkfs", "dd ", "> /dev/",
        "mv /", "shutdown", "reboot", "init 0", "chmod", "chown", "wget", "curl",
        "kill", "systemctl", "service"
    ]

    def is_safe(self, command: str) -> bool:
        """Simple heuristic to check if a command might be dangerous."""
        command = command.strip()
        # Always flag sudo commands as unsafe/requiring confirmation
        if command.startswith("sudo"):
            return False
            
        for bad in self.BLACKLIST:
            if bad in command:
                return False
        return True

    def execute(self, command: str) -> (str, str):
        """
        Executes a shell command and returns (stdout, stderr).
        Handles 'cd' command internally.
        """
        if not command:
            return "", "Empty command"

        # Handle Directory Change
        if command.startswith("cd "):
            path = command[3:].strip()
            # Expand ~ to home directory
            path = os.path.expanduser(path)
            
            try:
                os.chdir(path)
                return f"Changed directory to {os.getcwd()}", ""
            except FileNotFoundError:
                return "", f"Directory not found: {path}"
            except NotADirectoryError:
                return "", f"Not a directory: {path}"
            except PermissionError:
                return "", f"Permission denied: {path}"
            except Exception as e:
                return "", str(e)

        # Execute other commands
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)
