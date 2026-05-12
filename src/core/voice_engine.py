import speech_recognition as sr
from PySide6.QtCore import QObject, Signal, QThread

class VoiceWorker(QObject):
    recognized = Signal(str)
    error = Signal(str)
    listening_started = Signal()
    listening_stopped = Signal()
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def run(self):
        """Listening process to be run in a thread"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self.listening_started.emit()
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                self.listening_stopped.emit()
            
            try:
                text = self.recognizer.recognize_google(audio)
                self.recognized.emit(text)
            except sr.UnknownValueError:
                self.error.emit("Could not understand audio")
            except sr.RequestError as e:
                self.error.emit(f"Could not request results; {e}")
                
        except Exception as e:
            self.listening_stopped.emit()
            self.error.emit(str(e))
