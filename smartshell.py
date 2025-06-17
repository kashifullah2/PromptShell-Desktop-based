# from langchain_google_genai import ChatGoogleGenerativeAI
# import subprocess
# import platform
# from functools import lru_cache
# import os

# api_key = "You-Geminin-Api_Key"

# class SmartShell:
#     def __init__(self, api_key):
#         self.api_key = api_key
#         self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=self.api_key)
#         self.current_directory = os.getcwd()
    
#     def filtered_command(self, command: str):
#         blacklisted = ['rm', 'shutdown', 'reboot', 'mkfs', ':(){ :|:& };:', 'dd', 'kill', '>:']
#         if any(word in command for word in blacklisted):
#             raise ValueError("Blocked potentially dangerous command")
#         return command

#     @lru_cache(maxsize=100)
#     def generate_command(self, user_input):
#         prompt = (
#             f"You are a Linux terminal assistant. Return only a valid shell command for the user's intent below. "
#             f"Do not include explanations or quotes. "
#             f"System: {platform.system()}. Input: {user_input}")
#         command = self.llm.invoke(prompt).content.strip()
#         return self.filtered_command(command)
    
#     def run_command(self, user_input):
#         try:
#             command = self.generate_command(user_input)
#             if command.startswith("cd "):
#                 new_path = command[3:].strip()
#                 new_full_path = os.path.abspath(os.path.join(self.current_directory, new_path))
#                 if os.path.isdir(new_full_path):
#                     self.current_directory = new_full_path
#                     return f"Changed directory to {self.current_directory}", None
#                 else:
#                     return None, f"Directory not found: {new_path}"
            
#             result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.current_directory)
#             stdout = result.stdout.strip()
#             stderr = result.stderr.strip() if result.stderr else None
#             return stdout, stderr

#         except ValueError as ve:
#             return None, str(ve)
#         except subprocess.SubprocessError as e:
#             return None, str(e)

# # if api_key:
# #     app = SmartShell(api_key)
# #     user = input("Command: ")
# #     while user != "stop":
# #         output, error = app.run_command(user)
# #         print("Output:", output)
# #         # print("Error:", error)
# #         user = input("Command: ")
# # else:
# #     print("API Key Not Found")



from langchain_google_genai import ChatGoogleGenerativeAI
import subprocess
import platform
from functools import lru_cache
import os

class SmartShell:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=self.api_key)
        self.current_directory = os.getcwd()
    
    def filtered_command(self, command: str):
        blacklisted = ['rm', 'shutdown', 'reboot', 'mkfs', ':(){ :|:& };:', 'dd', 'kill', '>:']
        if any(word in command for word in blacklisted):
            raise ValueError("Blocked potentially dangerous command")
        return command

    @lru_cache(maxsize=100)
    def generate_command(self, user_input):
        prompt = (
            f"You are a Linux terminal assistant. Return only a valid shell command for the user's intent below. "
            f"Do not include explanations or quotes. "
            f"System: {platform.system()}. Input: {user_input}")
        command = self.llm.invoke(prompt).content.strip()
        return self.filtered_command(command)
    
    def run_command(self, user_input):
        try:
            command = self.generate_command(user_input)
            if command.startswith("cd "):
                new_path = command[3:].strip()
                new_full_path = os.path.abspath(os.path.join(self.current_directory, new_path))
                if os.path.isdir(new_full_path):
                    self.current_directory = new_full_path
                    return f"Changed directory to {self.current_directory}", None
                else:
                    return None, f"Directory not found: {new_path}"
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.current_directory)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip() if result.stderr else None
            return stdout, stderr

        except ValueError as ve:
            return None, str(ve)
        except subprocess.SubprocessError as e:
            return None, str(e)
