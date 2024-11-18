from typing import List, Dict, Any

class CodeElement:
    name: str
    type: str
    decorators: List[str]
    imports: List[str]
    methods: List[str]
    line_number: int
    dependencies: List[str]