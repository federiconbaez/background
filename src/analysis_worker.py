import re
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from src.code_analyzer import CodeAnalyzer

class AnalysisWorker(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    
    def __init__(self, analyzer: CodeAnalyzer, file_path: str):
        super().__init__()
        self.analyzer = analyzer
        self.file_path = file_path
        
    def run(self):
        elements = self.analyzer.analyze_file(self.file_path)
        self.finished.emit(elements)