import os
import cv2
import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image
from PySide6.QtCore import QObject, Signal, QThread

class MediaProcessorWorker(QObject):
    """Worker thread for processing media files (PDF, Image, Video)"""
    finished = Signal(str, str)  # content, file_type
    error = Signal(str)
    progress = Signal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            _, ext = os.path.splitext(self.file_path)
            ext = ext.lower()
            
            content = ""
            file_type = "unknown"

            if ext == '.pdf':
                self.progress.emit("Extracting text from PDF...")
                content = self._process_pdf(self.file_path)
                file_type = "pdf"
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                self.progress.emit("Performing OCR on Image...")
                content = self._process_image(self.file_path)
                file_type = "image"
            elif ext in ['.mp4', '.avi', '.mov']:
                self.progress.emit("Processing Video Frames...")
                content = self._process_video(self.file_path)
                file_type = "video"
            else:
                self.error.emit(f"Unsupported file type: {ext}")
                return

            self.finished.emit(content, file_type)

        except Exception as e:
            self.error.emit(str(e))

    def _process_pdf(self, path):
        return extract_text(path)

    def _process_image(self, path):
        return pytesseract.image_to_string(Image.open(path))

    def _process_video(self, path):
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise Exception("Could not open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * 5)  # Extract 1 frame every 5 seconds
        
        extracted_text = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                text = pytesseract.image_to_string(pil_img)
                if text.strip():
                    extracted_text.append(text.strip())
            
            frame_count += 1
            
        cap.release()
        
        # Deduplication (simple line-based)
        unique_lines = []
        seen = set()
        for block in extracted_text:
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if line and line not in seen:
                    unique_lines.append(line)
                    seen.add(line)
        
        return "\n".join(unique_lines)
