import os
import re
import ast
import json
from typing import Dict, List, Set, Tuple
from pathlib import Path
import subprocess
import tempfile
import shutil

class CodebaseParser:
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css'
        }
        
        self.ignore_patterns = {
            'node_modules', '__pycache__', '.git', '.venv', 'venv',
            'env', '.env', 'dist', 'build', '.next', '.nuxt',
            'coverage', '.coverage', 'target', 'bin', 'obj',
            '.gradle', '.idea', '.vscode', '*.pyc', '*.pyo',
            '*.pyd', '*.so', '*.dll', '*.class', '*.jar','*.class'
        }
    
    def clone_repository(self, github_url: str) -> str:
        """Clone GitHub repository to temporary directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(['git', 'clone', github_url, temp_dir], 
                         check=True, capture_output=True, text=True)
            return temp_dir
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to clone repository: {e}")
    
    def should_ignore_path(self, path: str) -> bool:
        """Check if path should be ignored based on patterns."""
        path_parts = Path(path).parts
        for part in path_parts:
            if any(pattern in part or part.startswith('.') and pattern.startswith('.') 
                   for pattern in self.ignore_patterns):
                return True
        return False
    
    def classify_language(self, file_path: str) -> str:
        """Classify file language based on extension."""
        ext = Path(file_path).suffix.lower()
        return self.supported_languages.get(ext, 'unknown')
    
    def extract_file_metadata(self, file_path: str) -> Dict:
        """Extract metadata from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return None
            
        language = self.classify_language(file_path)
        if language == 'unknown':
            return None
            
        metadata = {
            'path': file_path,
            'language': language,
            'size': len(content),
            'lines': len(content.splitlines()),
            'functions': [],
            'classes': [],
            'imports': [],
            'exports': []
        }
        
        if language == 'python':
            metadata.update(self._parse_python(content))
        elif language in ['javascript', 'typescript']:
            metadata.update(self._parse_javascript(content))
        elif language == 'java':
            metadata.update(self._parse_java(content))
        elif language == 'html':
            metadata.update(self._parse_html(content))
        elif language == 'css':
            metadata.update(self._parse_css(content))
            
        return metadata
    
    def _parse_python(self, content: str) -> Dict:
        """Parse Python file for functions, classes, imports."""
        try:
            tree = ast.parse(content)
        except:
            return {'functions': [], 'classes': [], 'imports': []}
            
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module or '')
                    
        return {'functions': functions, 'classes': classes, 'imports': imports}
    
    def _parse_javascript(self, content: str) -> Dict:
        """Parse JavaScript/TypeScript for functions, classes, imports."""
        functions = []
        classes = []
        imports = []
        exports = []
        
        # Basic regex patterns for JS/TS parsing
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*{))'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        export_pattern = r'export\s+(?:default\s+)?(?:function\s+(\w+)|class\s+(\w+)|const\s+(\w+))'
        
        for match in re.finditer(func_pattern, content):
            name = match.group(1) or match.group(2)
            if name:
                line_num = content[:match.start()].count('\n') + 1
                functions.append({'name': name, 'line': line_num})
        
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            classes.append({'name': match.group(1), 'line': line_num})
            
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
            
        for match in re.finditer(export_pattern, content):
            name = match.group(1) or match.group(2) or match.group(3)
            if name:
                exports.append(name)
        
        return {'functions': functions, 'classes': classes, 'imports': imports, 'exports': exports}
    
    def _parse_java(self, content: str) -> Dict:
        """Parse Java for classes, methods, imports."""
        functions = []
        classes = []
        imports = []
        
        # Java parsing patterns
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)'
        method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{'
        import_pattern = r'import\s+([^;]+);'
        
        for match in re.finditer(class_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            classes.append({'name': match.group(1), 'line': line_num})
            
        for match in re.finditer(method_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            functions.append({'name': match.group(1), 'line': line_num})
            
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1).strip())
            
        return {'functions': functions, 'classes': classes, 'imports': imports}
    
    def _parse_html(self, content: str) -> Dict:
        """Parse HTML for structure information."""
        tag_pattern = r'<(\w+)(?:\s+[^>]*)?>'
        tags = re.findall(tag_pattern, content.lower())
        tag_counts = {}
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
        return {'tags': tag_counts, 'total_tags': len(tags)}
    
    def _parse_css(self, content: str) -> Dict:
        """Parse CSS for selectors and rules."""
        selector_pattern = r'([^{}\n]+)\s*{'
        selectors = re.findall(selector_pattern, content)
        selectors = [s.strip() for s in selectors if s.strip()]
        
        return {'selectors': selectors, 'total_rules': len(selectors)}
    
    def parse_codebase(self, repo_path: str) -> Dict:
        """Parse entire codebase and extract metadata."""
        metadata = {
            'files': [],
            'language_stats': {},
            'total_files': 0,
            'total_lines': 0
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self.should_ignore_path(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if self.should_ignore_path(file_path):
                    continue
                    
                file_metadata = self.extract_file_metadata(file_path)
                if file_metadata:
                    metadata['files'].append(file_metadata)
                    
                    lang = file_metadata['language']
                    if lang not in metadata['language_stats']:
                        metadata['language_stats'][lang] = {'files': 0, 'lines': 0}
                    
                    metadata['language_stats'][lang]['files'] += 1
                    metadata['language_stats'][lang]['lines'] += file_metadata['lines']
                    metadata['total_lines'] += file_metadata['lines']
        
        metadata['total_files'] = len(metadata['files'])
        return metadata
