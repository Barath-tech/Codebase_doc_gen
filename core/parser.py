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
            '.jsp': 'jsp',  # Added JSP support
            '.jspx': 'jsp',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css',
            '.sql': 'sql',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.properties': 'properties'
        }
        
        self.ignore_patterns = {
            'node_modules', '__pycache__', '.git', '.venv', 'venv',
            'env', '.env', 'dist', 'build', '.next', '.nuxt',
            'coverage', '.coverage', 'target', 'bin', 'obj',
            '.gradle', '.idea', '.vscode', '*.pyc', '*.pyo',
            '*.pyd', '*.so', '*.dll', '*.class', '*.jar'
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
            'exports': [],
            'dependencies': []  # Enhanced for better dependency tracking
        }
        
        if language == 'python':
            metadata.update(self._parse_python(content, file_path))
        elif language in ['javascript', 'typescript']:
            metadata.update(self._parse_javascript(content, file_path))
        elif language == 'java':
            metadata.update(self._parse_java(content, file_path))
        elif language == 'jsp':
            metadata.update(self._parse_jsp(content, file_path))
        elif language == 'html':
            metadata.update(self._parse_html(content, file_path))
        elif language == 'css':
            metadata.update(self._parse_css(content, file_path))
        elif language == 'sql':
            metadata.update(self._parse_sql(content, file_path))
            
        return metadata
    
    def _parse_python(self, content: str, file_path: str) -> Dict:
        """Parse Python file for functions, classes, imports."""
        try:
            tree = ast.parse(content)
        except:
            return {'functions': [], 'classes': [], 'imports': [], 'dependencies': []}
            
        functions = []
        classes = []
        imports = []
        dependencies = []
        
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
                    for alias in node.names:
                        imports.append(alias.name)
                        dependencies.append({
                            'type': 'import',
                            'name': alias.name,
                            'line': node.lineno
                        })
                else:
                    module = node.module or ''
                    imports.append(module)
                    dependencies.append({
                        'type': 'from_import',
                        'name': module,
                        'line': node.lineno
                    })
                    
        return {'functions': functions, 'classes': classes, 'imports': imports, 'dependencies': dependencies}
    
    def _parse_javascript(self, content: str, file_path: str) -> Dict:
        """Parse JavaScript/TypeScript for functions, classes, imports."""
        functions = []
        classes = []
        imports = []
        exports = []
        dependencies = []
        
        # Enhanced regex patterns
        func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*{)|(\w+)\s*:\s*function)'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        export_pattern = r'export\s+(?:default\s+)?(?:function\s+(\w+)|class\s+(\w+)|const\s+(\w+))'
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Functions
            func_matches = re.finditer(func_pattern, line)
            for match in func_matches:
                name = match.group(1) or match.group(2) or match.group(3)
                if name:
                    functions.append({'name': name, 'line': i + 1})
            
            # Classes
            class_matches = re.finditer(class_pattern, line)
            for match in class_matches:
                classes.append({'name': match.group(1), 'line': i + 1})
            
            # Imports
            import_matches = re.finditer(import_pattern, line)
            for match in import_matches:
                imp_name = match.group(1) or match.group(2)
                if imp_name:
                    imports.append(imp_name)
                    dependencies.append({
                        'type': 'import',
                        'name': imp_name,
                        'line': i + 1
                    })
            
            # Exports
            export_matches = re.finditer(export_pattern, line)
            for match in export_matches:
                name = match.group(1) or match.group(2) or match.group(3)
                if name:
                    exports.append(name)
        
        return {'functions': functions, 'classes': classes, 'imports': imports, 'exports': exports, 'dependencies': dependencies}
    
    def _parse_java(self, content: str, file_path: str) -> Dict:
        """Parse Java for classes, methods, imports."""
        functions = []
        classes = []
        imports = []
        dependencies = []
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Java class pattern
            class_match = re.search(r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)', line)
            if class_match:
                classes.append({'name': class_match.group(1), 'line': i + 1})
            
            # Java method pattern
            method_match = re.search(r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{', line)
            if method_match:
                functions.append({'name': method_match.group(1), 'line': i + 1})
            
            # Java import pattern
            import_match = re.search(r'import\s+([^;]+);', line)
            if import_match:
                imp_name = import_match.group(1).strip()
                imports.append(imp_name)
                dependencies.append({
                    'type': 'import',
                    'name': imp_name,
                    'line': i + 1
                })
        
        return {'functions': functions, 'classes': classes, 'imports': imports, 'dependencies': dependencies}
    
    def _parse_jsp(self, content: str, file_path: str) -> Dict:
        """Parse JSP files for tags, imports, includes."""
        jsp_tags = []
        java_imports = []
        jsp_includes = []
        dependencies = []
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # JSP page directive imports
            page_import = re.search(r'<%@\s*page\s+.*?import\s*=\s*["\']([^"\']+)["\']', line)
            if page_import:
                imp_name = page_import.group(1)
                java_imports.append(imp_name)
                dependencies.append({
                    'type': 'jsp_import',
                    'name': imp_name,
                    'line': i + 1
                })
            
            # JSP includes
            include_match = re.search(r'<%@\s*include\s+file\s*=\s*["\']([^"\']+)["\']', line)
            if include_match:
                inc_file = include_match.group(1)
                jsp_includes.append(inc_file)
                dependencies.append({
                    'type': 'jsp_include',
                    'name': inc_file,
                    'line': i + 1
                })
            
            # JSP forward
            forward_match = re.search(r'<jsp:forward\s+page\s*=\s*["\']([^"\']+)["\']', line)
            if forward_match:
                forward_page = forward_match.group(1)
                jsp_includes.append(forward_page)
                dependencies.append({
                    'type': 'jsp_forward',
                    'name': forward_page,
                    'line': i + 1
                })
            
            # Custom JSP tags
            custom_tags = re.findall(r'<(\w+):(\w+)', line)
            for namespace, tag in custom_tags:
                jsp_tags.append(f"{namespace}:{tag}")
        
        return {
            'jsp_tags': jsp_tags,
            'java_imports': java_imports,
            'jsp_includes': jsp_includes,
            'imports': java_imports + jsp_includes,
            'dependencies': dependencies
        }
    
    def _parse_html(self, content: str, file_path: str) -> Dict:
        """Parse HTML for structure information."""
        tag_pattern = r'<(\w+)(?:\s+[^>]*)?>'
        link_pattern = r'(?:src|href)\s*=\s*["\']([^"\']+)["\']'
        
        tags = re.findall(tag_pattern, content.lower())
        links = re.findall(link_pattern, content)
        
        tag_counts = {}
        dependencies = []
        
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for i, link in enumerate(links):
            if not link.startswith(('http://', 'https://', 'mailto:', '#')):
                dependencies.append({
                    'type': 'resource_link',
                    'name': link,
                    'line': i + 1
                })
            
        return {
            'tags': tag_counts, 
            'total_tags': len(tags),
            'resource_links': links,
            'dependencies': dependencies
        }
    
    def _parse_css(self, content: str, file_path: str) -> Dict:
        """Parse CSS for selectors and rules."""
        selector_pattern = r'([^{}\n]+)\s*{'
        import_pattern = r'@import\s+["\']([^"\']+)["\']'
        
        selectors = re.findall(selector_pattern, content)
        css_imports = re.findall(import_pattern, content)
        
        selectors = [s.strip() for s in selectors if s.strip()]
        dependencies = []
        
        for imp in css_imports:
            dependencies.append({
                'type': 'css_import',
                'name': imp,
                'line': 1  # Would need line-by-line parsing for exact line numbers
            })
        
        return {
            'selectors': selectors, 
            'total_rules': len(selectors),
            'css_imports': css_imports,
            'dependencies': dependencies
        }
    
    def _parse_sql(self, content: str, file_path: str) -> Dict:
        """Parse SQL files for tables, procedures, functions."""
        tables = []
        procedures = []
        functions = []
        dependencies = []
        
        # SQL patterns
        create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)'
        create_proc_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)'
        create_func_pattern = r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)'
        reference_pattern = r'REFERENCES\s+(\w+)'
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Tables
            table_matches = re.finditer(create_table_pattern, line, re.IGNORECASE)
            for match in table_matches:
                tables.append({'name': match.group(1), 'line': i + 1})
            
            # Procedures
            proc_matches = re.finditer(create_proc_pattern, line, re.IGNORECASE)
            for match in proc_matches:
                procedures.append({'name': match.group(1), 'line': i + 1})
            
            # Functions
            func_matches = re.finditer(create_func_pattern, line, re.IGNORECASE)
            for match in func_matches:
                functions.append({'name': match.group(1), 'line': i + 1})
            
            # Foreign key references
            ref_matches = re.finditer(reference_pattern, line, re.IGNORECASE)
            for match in ref_matches:
                dependencies.append({
                    'type': 'table_reference',
                    'name': match.group(1),
                    'line': i + 1
                })
        
        return {
            'tables': tables,
            'procedures': procedures,
            'functions': functions,
            'dependencies': dependencies
        }
    
    def parse_codebase(self, repo_path: str) -> Dict:
        """Parse entire codebase and extract metadata."""
        metadata = {
            'files': [],
            'language_stats': {},
            'total_files': 0,
            'total_lines': 0,
            'project_structure': {}
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
                    # Make path relative to repo root
                    rel_path = os.path.relpath(file_path, repo_path)
                    file_metadata['path'] = rel_path
                    
                    metadata['files'].append(file_metadata)
                    
                    lang = file_metadata['language']
                    if lang not in metadata['language_stats']:
                        metadata['language_stats'][lang] = {'files': 0, 'lines': 0}
                    
                    metadata['language_stats'][lang]['files'] += 1
                    metadata['language_stats'][lang]['lines'] += file_metadata['lines']
                    metadata['total_lines'] += file_metadata['lines']
        
        metadata['total_files'] = len(metadata['files'])
        metadata['project_structure'] = self._analyze_project_structure(metadata['files'])
        
        return metadata
    
    def _analyze_project_structure(self, files: List[Dict]) -> Dict:
        """Analyze project structure and identify patterns."""
        structure = {
            'web_files': [],
            'backend_files': [],
            'database_files': [],
            'config_files': [],
            'test_files': [],
            'documentation_files': []
        }
        
        for file_data in files:
            path = file_data['path'].lower()
            lang = file_data['language']
            
            if lang in ['html', 'css', 'javascript', 'jsp']:
                structure['web_files'].append(file_data)
            elif lang in ['java', 'python']:
                if 'test' in path or 'spec' in path:
                    structure['test_files'].append(file_data)
                else:
                    structure['backend_files'].append(file_data)
            elif lang == 'sql':
                structure['database_files'].append(file_data)
            elif lang in ['json', 'yaml', 'properties', 'xml'] or 'config' in path:
                structure['config_files'].append(file_data)
            elif lang == 'markdown' or path.endswith('.md'):
                structure['documentation_files'].append(file_data)
        
        return structure
