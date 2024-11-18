import os
import ast
from typing import List
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QTreeWidget, QTreeWidgetItem, QProgressBar, QMessageBox, QGridLayout
)
from PyQt6.QtGui import QColor, QPalette
from src.code_analyzer import CodeAnalyzer
from src.code_element import CodeElement
from src.dashboard_card import DashboardCard
from src.analysis_worker import AnalysisWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Structure Analyzer")
        self.setMinimumSize(1200, 800)
        self.analyzer = CodeAnalyzer()
        self._setup_theme()
        self.setup_ui()
        
    def _setup_theme(self):
        # Set up color palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f5f6fa"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f5f6fa"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2c3e50"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#3498db"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#3498db"))
        self.setPalette(palette)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ Header Section
        # -----------------------------------------------------------------------------------------------------
        header = QHBoxLayout()
        title = QLabel("Code Structure Analyzer")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        header.addWidget(title)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ Toolbar Section
        # -----------------------------------------------------------------------------------------------------
        toolbar = QHBoxLayout()
        self.file_button = QPushButton("Select File")
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.file_button.clicked.connect(self.select_file)
        
        self.start_button = QPushButton("Start Analysis")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.start_button.clicked.connect(self.start_analysis)
        self.start_button.setEnabled(False)

        self.split_button = QPushButton("Split Classes")
        self.split_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.split_button.clicked.connect(self.split_classes)

        # Add widgets to toolbar layout
        toolbar.addWidget(self.file_button)
        toolbar.addWidget(self.start_button)
        toolbar.addWidget(self.split_button)
        toolbar.addStretch()
        header.addLayout(toolbar)
        main_layout.addLayout(header)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ Dashboard Section
        # -----------------------------------------------------------------------------------------------------
        dashboard = QGridLayout()
        dashboard.setSpacing(15)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ File Info Card
        # -----------------------------------------------------------------------------------------------------
        self.file_info_card = DashboardCard("File Information")
        self.file_info_content = QTextEdit()
        self.file_info_content.setReadOnly(True)
        self.file_info_content.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.file_info_card.content_layout.addWidget(self.file_info_content)
        dashboard.addWidget(self.file_info_card, 0, 0)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ Code Structure Card
        # -----------------------------------------------------------------------------------------------------
        structure_card = DashboardCard("Code Structure")
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Element", "Type", "Line"])
        self.tree_widget.setColumnWidth(0, 200)
        self.tree_widget.setColumnWidth(1, 100)
        self.tree_widget.setColumnWidth(2, 50)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        structure_card.content_layout.addWidget(self.tree_widget)
        dashboard.addWidget(structure_card, 0, 1, 2, 1)

        # -----------------------------------------------------------------------------------------------------
        #  @ Code Metrics Card
        # -----------------------------------------------------------------------------------------------------
        self.metrics_card = DashboardCard("Code Metrics")
        self.metrics_content = QTextEdit()
        self.metrics_content.setReadOnly(True)
        self.metrics_content.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.metrics_card.content_layout.addWidget(self.metrics_content)
        dashboard.addWidget(self.metrics_card, 1, 0)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ Set column stretch for responsive design
        # -----------------------------------------------------------------------------------------------------
        dashboard.setColumnStretch(0, 1)
        dashboard.setColumnStretch(1, 2)
        main_layout.addLayout(dashboard)
        
        # -----------------------------------------------------------------------------------------------------
        #  @ Progress Bar Section
        # -----------------------------------------------------------------------------------------------------
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #f8f9fa;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

    # -----------------------------------------------------------------------------------------------------
    #  @ select_file Method
    # -----------------------------------------------------------------------------------------------------
    def select_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar Archivo",
                "",
                "Archivos de código (*.py *.ts *.js *.tsx *.jsx)"
            )
            if file_path:
                self.current_file = file_path
                self.start_button.setEnabled(True)
                self.file_button.setText(os.path.basename(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select file: {str(e)}")

    # -----------------------------------------------------------------------------------------------------
    #  @ start_analysis Method
    # -----------------------------------------------------------------------------------------------------
    def start_analysis(self):
        try:
            self.worker = AnalysisWorker(self.analyzer, self.current_file)
            self.worker.finished.connect(self.update_ui)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start analysis: {str(e)}")

    # -----------------------------------------------------------------------------------------------------
    #  @ update_ui Method
    # -----------------------------------------------------------------------------------------------------
    def update_ui(self, elements: List[CodeElement]):
        try:
            self.tree_widget.clear()
            
            # -----------------------------------------------------------------------------------------------------
            #  @ Metrics Update Section
            # -----------------------------------------------------------------------------------------------------
            total_classes = len([e for e in elements if e.type == 'class'])
            total_methods = sum(len(e.methods) for e in elements)
            total_imports = sum(len(e.imports) for e in elements)
            
            metrics_text = f"""
            📊 Code Metrics Summary:
            -------------------------
            Total Classes: {total_classes}
            Total Methods: {total_methods}
            Total Imports: {total_imports}
            Average Methods per Class: {total_methods/total_classes if total_classes > 0 else 0:.1f}
            """
            self.metrics_content.setText(metrics_text)
            
            # -----------------------------------------------------------------------------------------------------
            #  @ File Information Update Section
            # -----------------------------------------------------------------------------------------------------
            file_info = f"""
            📁 File: {os.path.basename(self.current_file)}
            📍 Location: {os.path.dirname(self.current_file)}
            📏 Size: {os.path.getsize(self.current_file)/1024:.1f} KB
            🔄 Last Modified: {os.path.getmtime(self.current_file)}
            """
            self.file_info_content.setText(file_info)
            
            # -----------------------------------------------------------------------------------------------------
            #  @ Tree Widget Update Section
            # -----------------------------------------------------------------------------------------------------
            for element in elements:
                item = QTreeWidgetItem([
                    element.name,
                    element.type,
                    str(element.line_number)
                ])
                
                # -----------------------------------------------------------------------------------------------------
                #  @ Color coding based on element type
                # -----------------------------------------------------------------------------------------------------
                if element.type == 'class':
                    item.setForeground(0, QColor("#3498db"))
                elif element.type == 'function':
                    item.setForeground(0, QColor("#2ecc71"))
                    
                # -----------------------------------------------------------------------------------------------------
                #  @ Add Subitems with Icons Section
                # -----------------------------------------------------------------------------------------------------
                if element.decorators:
                    decorators_item = QTreeWidgetItem(["Decorators", "", ""])
                    decorators_item.setForeground(0, QColor("#9b59b6"))
                    item.addChild(decorators_item)
                    for decorator in element.decorators:
                        QTreeWidgetItem(decorators_item, [decorator, "", ""])
                        
                if element.imports:
                    imports_item = QTreeWidgetItem(["Imports", "", ""])
                    imports_item.setForeground(0, QColor("#e67e22"))
                    item.addChild(imports_item)
                    for imp in element.imports:
                        QTreeWidgetItem(imports_item, [imp, "", ""])
                        
                if element.methods:
                    methods_item = QTreeWidgetItem(["Methods", "", ""])
                    methods_item.setForeground(0, QColor("#2ecc71"))
                    item.addChild(methods_item)
                    for method in element.methods:
                        method_item = QTreeWidgetItem(methods_item, [method, "", ""])
                        method_item.setForeground(0, QColor("#27ae60"))
                        
                self.tree_widget.addTopLevelItem(item)
            
            lines = [element.line_number for element in elements]
            if lines:
                self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(lines.index(min(lines))))
            
            self.tree_widget.expandAll()
            for i in range(self.tree_widget.columnCount()):
                self.tree_widget.resizeColumnToContents(i)
            self.progress_bar.setValue(100)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update UI: {str(e)}")

    # -----------------------------------------------------------------------------------------------------
    #  @ split_classes Method
    # -----------------------------------------------------------------------------------------------------
    def split_classes(self):
        try:
            if not hasattr(self, 'current_file'):
                return
                
            with open(self.current_file, 'r') as file:
                content = file.read()
            
            if self.current_file.endswith('.py'):
                tree = ast.parse(content)
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                base_path = os.path.dirname(self.current_file)
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                
                for i, class_node in enumerate(classes):
                    try:
                        class_content = ast.get_source_segment(content, class_node)
                        imports = self._get_class_imports(content, class_node)
                        
                        new_content = "\n".join(imports + ["", class_content])
                        new_file_path = os.path.join(
                            base_path,
                            f"{base_name}_{class_node.name.lower()}.py"
                        )
                        
                        with open(new_file_path, 'w') as new_file:
                            new_file.write(new_content)
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Failed to process class {class_node.name}: {str(e)}")
            
            QMessageBox.information(
                self,
                "Éxito",
                "Las clases han sido separadas en archivos individuales"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to split classes: {str(e)}")
        
    # -----------------------------------------------------------------------------------------------------
    #  @ _get_class_imports Method
    # -----------------------------------------------------------------------------------------------------
    def _get_class_imports(self, source: str, class_node: ast.ClassDef) -> List[str]:
        try:
            imports = []
            class_content = ast.get_source_segment(source, class_node)
            
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_content = ast.get_source_segment(source, node)
                    if any(name in class_content for name in self._get_imported_names(node)):
                        imports.append(import_content)
                        
            return imports
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve class imports: {str(e)}")
            return []
        
    # -----------------------------------------------------------------------------------------------------
    #  @ _get_imported_names Method
    # -----------------------------------------------------------------------------------------------------
    def _get_imported_names(self, node: ast.AST) -> List[str]:
        try:
            if isinstance(node, ast.Import):
                return [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                return [alias.name for alias in node.names]
            return []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve imported names: {str(e)}")
            return []
        
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()