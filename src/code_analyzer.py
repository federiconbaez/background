import os
import ast
import re

from typing import List, Dict, Any
from src.code_element import CodeElement

class CodeAnalyzer:
    def __init__(self):
        self.patterns = {
            'angular': {
                'component': r'@Component\(',
                'service': r'@Injectable\(',
                'module': r'@NgModule\(',
                'pipe': r'@Pipe\(',
            },
            'react': {
                'component': r'(class\s+\w+\s+extends\s+React\.Component|function\s+\w+\s*\([^)]*\)\s*{)',
                'hook': r'use[A-Z]',
                'context': r'createContext',
            },
            'python': {
                'class': r'class\s+\w+',
                'function': r'def\s+\w+',
                'decorator': r'@\w+',
            },
            'nestjs': {
                'controller': r'@Controller\(',
                'service': r'@Injectable\(',
                'module': r'@Module\(',
                'guard': r'@Injectable\(',
            }
        }
        
    def analyze_file(self, file_path: str) -> List[CodeElement]:
        elements = []
        file_content = self._read_file(file_path)
        file_ext = os.path.splitext(file_path)[1]
        
        if file_ext in ['.py']:
            elements.extend(self._analyze_python(file_content))
        elif file_ext in ['.ts', '.tsx']:
            elements.extend(self._analyze_typescript(file_content))
        elif file_ext in ['.js', '.jsx']:
            elements.extend(self._analyze_javascript(file_content))
            
        return elements

    def _analyze_python(self, content: str) -> List[CodeElement]:
        elements = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    decorators = [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                    methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    elements.append(CodeElement(
                        name=node.name,
                        type='class',
                        decorators=decorators,
                        imports=self._get_imports(tree),
                        methods=methods,
                        line_number=node.lineno,
                        dependencies=self._get_dependencies(node)
                    ))
        except Exception as e:
            print(f"Error analyzing Python file: {e}")
        return elements

    def _analyze_typescript(self, content: str) -> List[CodeElement]:
        elements = []
        lines = content.split('\n')
        current_element = None
        
        for i, line in enumerate(lines):
            # Detectar decoradores Angular/NestJS
            for pattern_type, pattern in self.patterns['angular'].items():
                if re.search(pattern, line):
                    current_element = CodeElement(
                        name=self._extract_name(lines[i+1]),
                        type=pattern_type,
                        decorators=[line.strip()],
                        imports=self._extract_imports(content),
                        methods=self._extract_methods(content),
                        line_number=i+1,
                        dependencies=[]
                    )
                    elements.append(current_element)
                    
        return elements

    def _get_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"from {node.module} import {', '.join(n.name for n in node.names)}")
        return imports

    def _get_dependencies(self, node: ast.AST) -> List[str]:
        deps = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                deps.append(child.id)
        return list(set(deps))

    def _extract_name(self, line: str) -> str:
        match = re.search(r'class\s+(\w+)|export\s+class\s+(\w+)', line)
        if match:
            return match.group(1) or match.group(2)
        return "Unknown"

    def _extract_imports(self, content: str) -> List[str]:
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        return imports

    def _extract_methods(self, content: str) -> List[str]:
        methods = []
        method_pattern = r'(?:public|private|protected)?\s*\w+\s*\([^)]*\)\s*{'
        matches = re.finditer(method_pattern, content)
        for match in matches:
            methods.append(match.group().strip())
        return methods

    def _read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()