from PySide6.QtCore import QObject, Signal, QThread
from src.core.llm_engine import LLMEngine

class CommandWorker(QObject):
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, user_input, llm_engine, task_type="command"):
        super().__init__()
        self.user_input = user_input
        self.llm_engine = llm_engine
        self.task_type = task_type
        
    def run(self):
        try:
            result = self.llm_engine.process_query(self.user_input, self.task_type)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
