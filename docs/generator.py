# docs/generator.py
import os
import re
import json
import markdown
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class StructuredDocumentationGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.docs_dir = os.path.join(output_dir, 'docs')
        os.makedirs(self.docs_dir, exist_ok=True)
        
    def generate_structured_docs(self, metadata: Dict, llm_sections: Dict, 
                                 graph_stats: Dict, dependency_graph_path: str) -> Dict:
        """Generate structured documentation files."""
        
        generated_files = {}
        
        # 1. Generate index.md (Overview)
        generated_files['index'] = self._generate_index_md(metadata, llm_sections.get('overview', ''))
        
        # 2. Generate architecture.md
        generated_files['architecture'] = self._generate_architecture_md(
            metadata, llm_sections.get('architecture', ''), graph_stats, dependency_graph_path
        )
        
        # 3. Generate database.md
        generated_files['database'] = self._generate_database_md(
            metadata, llm_sections.get('database', '')
        )
        
        # 4. Generate classes.md
        generated_files['classes'] = self._generate_classes_md(
            metadata, llm_sections.get('classes', '')
        )
        
        # 5. Generate web.md
        generated_files['web'] = self._generate_web_md(
            metadata, llm_sections.get('web', '')
        )
        
        # Generate consolidated HTML and PDF
        generated_files['html'] = self._generate_consolidated_html(generated_files, metadata)
        generated_files['pdf'] = self._generate_consolidated_pdf(generated_files, metadata)
        
        return generated_files
    
    def _generate_index_md(self, metadata: Dict, overview_content: str) -> str:
        """Generate index.md with project overview."""
        
        content = f"""# Project Documentation

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

{overview_content}

## Project Statistics

| Metric | Value |
|--------|-------|
| Total Files | {metadata['total_files']} |
| Total Lines of Code | {metadata['total_lines']:,} |
| Languages Used | {len(metadata['language_stats'])} |

### Technology Stack

"""
        
        for lang, stats in metadata['language_stats'].items():
            percentage = (stats['lines'] / metadata['total_lines'] * 100) if metadata['total_lines'] > 0 else 0
            content += f"- **{lang.title()}**: {stats['files']} files, {stats['lines']:,} lines ({percentage:.1f}%)\n"
        
        content += f"""

## Documentation Sections

- [🏗️ Architecture](./architecture.md) - System architecture and design patterns
- [🗄️ Database](./database.md) - Database schema and data management
- [🏷️ Classes](./classes.md) - Object-oriented design and class structures  
- [🌐 Web](./web.md) - Web interface and API documentation

## Quick Navigation

### Project Structure
- **Web Components**: {len(metadata.get('project_structure', {}).get('web_files', []))} files
- **Backend Logic**: {len(metadata.get('project_structure', {}).get('backend_files', []))} files
- **Database Scripts**: {len(metadata.get('project_structure', {}).get('database_files', []))} files
- **Configuration**: {len(metadata.get('project_structure', {}).get('config_files', []))} files
- **Tests**: {len(metadata.get('project_structure', {}).get('test_files', []))} files
- **Documentation**: {len(metadata.get('project_structure', {}).get('documentation_files', []))} files

---

*This documentation is automatically generated and provides both technical details for developers and explanatory content for stakeholders.*
"""
        
        index_path = os.path.join(self.docs_dir, 'index.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return index_path
    
    def _generate_architecture_md(self, metadata: Dict, architecture_content: str, 
                                  graph_stats: Dict, dependency_graph_path: str) -> str:
        """Generate architecture.md with system design documentation."""
        
        content = f"""# System Architecture

## Architecture Overview

{architecture_content}

## Dependency Analysis

### Graph Metrics
- **Total Modules**: {graph_stats.get('total_nodes', 0)}
- **Dependencies**: {graph_stats.get('total_edges', 0)}
- **Graph Density**: {graph_stats.get('density', 0):.3f}
- **Connectivity**: {'Well Connected' if graph_stats.get('is_connected', False) else 'Loosely Connected'}
- **Average Connections per Module**: {graph_stats.get('average_degree', 0):.2f}

### Component Breakdown

"""
        
        # Analyze components by type
        project_structure = metadata.get('project_structure', {})
        
        for component_type, files in project_structure.items():
            if files:
                content += f"#### {component_type.replace('_', ' ').title()}\n"
                content += f"- **Count**: {len(files)} files\n"
                content += f"- **Total Lines**: {sum(f.get('lines', 0) for f in files):,}\n"
                
                # Show key files
                key_files = sorted(files, key=lambda x: x.get('lines', 0), reverse=True)[:5]
                content += "- **Key Files**:\n"
                for file_data in key_files:
                    content += f"  - `{file_data['path']}` ({file_data.get('lines', 0)} lines)\n"
                content += "\n"
        
        if dependency_graph_path:
            content += f"""
## Dependency Visualization

An interactive dependency graph has been generated showing the relationships between modules.

*View the dependency graph: [dependency_graph.html](../dependency_graph.html)*

## Integration Patterns

Based on the analysis, the system follows these integration patterns:
"""
        
        # Add technical architecture details
        content += """
## Technical Layers

### Presentation Layer
- User interface components
- Web pages and forms
- Client-side scripting

### Business Logic Layer  
- Application logic and workflows
- Data processing and validation
- Business rules implementation

### Data Access Layer
- Database connections and queries
- Data persistence and retrieval
- Transaction management

---

[← Back to Overview](./index.md) | [Database Documentation →](./database.md)
"""
        
        arch_path = os.path.join(self.docs_dir, 'architecture.md')
        with open(arch_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return arch_path
    
#     def _generate_database_md(self, metadata: Dict, database_content: str) -> str:
#         """Generate database.md with database documentation."""
        
#         db_files = metadata.get('project_structure', {}).get('database_files', [])
        
#         content = f"""# Database Documentation

# ## Database Overview

# {database_content}

# ## Database Files

# Total SQL files found: **{len(db_files)}**

# """
        
#         if db_files:
#             content += "### SQL Scripts\n\n"
#             content += "| File | Lines | Purpose |\n"
#             content += "|------|-------|--------|\n"
            
#             for file_data in sorted(db_files, key=lambda x: x.get('lines', 0), reverse=True):
#                 purpose = self._infer_sql_purpose(file_data['path'])
#                 content += f"| `{file_data['path']}` | {file_data.get('lines', 0)} | {purpose} |\n"
            
#             # Extract and display tables/procedures
#             all_tables = []
#             all_procedures = []
            
#             for file_data in db_files:
#                 all_tables.extend(file_data.get('tables', []))
#                 all_procedures.extend(file_data.get('procedures', []))
            
#             if all_tables:
#                 content += f"\n### Database Tables ({len(all_tables)} found)\n\n"
#                 for table in sorted(all_tables, key=lambda x: x['name']):
#                     content += f"- **{table['name']}** (defined in line {table['line']})\n"
            
#             if all_procedures:
#                 content += f"\n### Stored Procedures ({len(all_procedures)} found)\n\n"
#                 for proc in sorted(all_procedures, key=lambda x: x['name']):
#                     content += f"- **{proc['name']}** (defined in line {proc['line']})\n"
#         else:
#             content += "*No SQL files detected in the project.*\n"
        
#         content += """

# ## Database Setup

# *Refer to the specific SQL scripts for database setup and configuration instructions.*

# ## Data Relationships

# *Entity relationships are defined through foreign key constraints and table references found in the SQL scripts.*

# ---

# [← Architecture](./architecture.md) | [Classes Documentation →](./classes.md)
# """
        
#         db_path = os.path.join(self.docs_dir, 'database.md')
#         with open(db_path, 'w', encoding='utf-8') as f:
#             f.write(content)
        
#         return db_path
    
#     def _generate_classes_md(self, metadata: Dict, classes_content: str) -> str:
#         """Generate classes.md with class documentation."""
        
#         content = f"""# Classes and Object-Oriented Design

# ## Class Overview

# {classes_content}

# ## Class Analysis

# """
        
#         # Collect all classes by language
#         classes_by_lang = {}
#         functions_by_lang = {}
        
#         for file_data in metadata['files']:
#             lang = file_data['language']
#             if file_data.get('classes'):
#                 if lang not in classes_by_lang:
#                     classes_by_lang[lang] = []
#                 for cls in file_data['classes']:
#                     cls_info = cls.copy()
#                     cls_info['file'] = file_data['path']
#                     classes_by_lang[lang].append(cls_info)
            
#             if file_data.get('functions'):
#                 if lang not in functions_by_lang:
#                     functions_by_lang[lang] = 0
#                 functions_by_lang[lang] += len(file_data['functions'])
        
#         # Display classes by language
#         for lang, classes in classes_by_lang.items():
#             content += f"### {lang.title()} Classes\n\n"
#             content += f"Total classes found: **{len(classes)}**\n\n"
            
#             # Group by file for better organization
#             classes_by_file = {}
#             for cls in classes:
#                 file_path = cls['file']
#                 if file_path not in classes_by_file:
#                     classes_by_file[file_path] = []
#                 classes_by_file[file_path].append(cls)
            
#             for file_path, file_classes in classes_by_file.items():
#                 content += f"#### {file_path}\n\n"
#                 for cls in sorted(file_classes, key=lambda x: x['line']):
#                     content += f"**{cls['name']}** (line {cls['line']})\n"
#                     if cls.get('docstring'):
#                         content += f"- *{cls['docstring'][:100]}...*\n"
#                     if cls.get('methods'):
#                         content += f"- Methods: {', '.join(cls['methods'])}\n"
#                     content += "\n"
        
#         # Function summary
#         if functions_by_lang:
#             content += "## Function Summary\n\n"
#             content += "| Language | Function Count |\n"
#             content += "|----------|---------------|\n"
#             for lang, count in functions_by_lang.items():
#                 content += f"| {lang.title()} | {count} |\n"
        
#         content += """

# ## Design Patterns

# *Object-oriented design patterns and architectural decisions are reflected in the class structure and relationships documented above.*

# ---

# [← Database](./database.md) | [Web Documentation →](./web.md)
# """
        
#         classes_path = os.path.join(self.docs_dir, 'classes.md')
#         with open(classes_path, 'w', encoding='utf-8') as f:
#             f.write(content)
        
#         return classes_path
    
#     def _generate_web_md(self, metadata: Dict, web_content: str) -> str:
#         """Generate web.md with web interface documentation."""
        
#         web_files = metadata.get('project_structure', {}).get('web_files', [])
        
#         content = f"""# Web Interface Documentation

# ## Web Overview

# {web_content}

# ## Web Components Analysis

# Total web files: **{len(web_files)}**

# """
        
#         if web_files:
#             # Categorize web files
#             jsp_files = [f for f in web_files if f['language'] == 'jsp']
#             html_files = [f for f in web_files if f['language'] == 'html']
#             css_files = [f for f in web_files if f['language'] == 'css']
#             js_files = [f for f in web_files if f['language'] in ['javascript', 'typescript']]
            
#             # JSP Pages
#             if jsp_files:
#                 content += f"### JSP Pages ({len(jsp_files)})\n\n"
#                 content += "| Page | Lines | Includes | Java Imports |\n"
#                 content += "|------|-------|----------|-------------|\n"
                
#                 for jsp in sorted(jsp_files, key=lambda x: x['path']):
#                     includes = len(jsp.get('jsp_includes', []))
#                     imports = len(jsp.get('java_imports', []))
#                     content += f"| `{jsp['path']}` | {jsp.get('lines', 0)} | {includes} | {imports} |\n"
                
#                 # Navigation flow analysis
#                 content += "\n#### Navigation Flow\n\n"
#                 all_includes = []
#                 all_forwards = []
                
#                 for jsp in jsp_files:
#                     all_includes.extend(jsp.get('jsp_includes', []))
#                     for dep in jsp.get('dependencies', []):
#                         if dep['type'] == 'jsp_forward':
#                             all_forwards.append(dep['name'])
                
#                 if all_includes:
#                     content += f"**Common Includes**: {', '.join(set(all_includes))}\n\n"
#                 if all_forwards:
#                     content += f"**Page Forwards**: {', '.join(set(all_forwards))}\n\n"
            
#             # HTML Pages
#             if html_files:
#                 content += f"### HTML Pages ({len(html_files)})\n\n"
#                 for html in sorted(html_files, key=lambda x: x['path']):
#                     content += f"- **{html['path']}** ({html.get('lines', 0)} lines)\n"
#                     if html.get('tags'):
#                         top_tags = sorted(html['tags'].items(), key=lambda x: x[1], reverse=True)[:5]
#                         content += f"  - Top tags: {', '.join([f'{tag}({count})' for tag, count in top_tags])}\n"
            
#             # CSS Stylesheets
#             if css_files:
#                 content += f"\n### Stylesheets ({len(css_files)})\n\n"
#                 for css in sorted(css_files, key=lambda x: x['path']):
#                     content += f"- **{css['path']}** ({css.get('lines', 0)} lines, {css.get('total_rules', 0)} rules)\n"
            
#             # JavaScript Files
#             if js_files:
#                 content += f"\n### JavaScript ({len(js_files)})\n\n"
#                 for js in sorted(js_files, key=lambda x: x['path']):
#                     functions = len(js.get('functions', []))
#                     content += f"- **{js['path']}** ({js.get('lines', 0)} lines, {functions} functions)\n"
        
#         else:
#             content += "*No web files detected in the project.*\n"
        
#         content += """

# ## User Interface Flow

# *The navigation flow and user experience paths are defined through the JSP includes, forwards, and HTML linking structure documented above.*

# ## API Endpoints

# *REST API endpoints and web service interfaces would be documented here based on the backend implementation.*

# ---

# [← Classes](./classes.md) | [Back to Overview](./index.md)
# """
        
#         web_path = os.path.join(self.docs_dir, 'web.md')
#         with open(web_path, 'w', encoding='utf-8') as f:
#             f.write(content)
        
#         return web_path
        # Enhanced generator methods for docs/generator.py

    def _generate_classes_md(self, metadata: Dict, classes_content: str) -> str:
        """Generate classes.md with comprehensive class documentation and UML diagrams."""
        
        content = f"""# Classes and Object-Oriented Design

    ## Class Overview and UML Diagrams

    {classes_content}

    ## Class Analysis Summary

    """
        
        # Collect all classes by language for summary
        classes_by_lang = {}
        functions_by_lang = {}
        
        for file_data in metadata['files']:
            lang = file_data['language']
            if file_data.get('classes'):
                if lang not in classes_by_lang:
                    classes_by_lang[lang] = []
                for cls in file_data['classes']:
                    cls_info = cls.copy()
                    cls_info['file'] = file_data['path']
                    classes_by_lang[lang].append(cls_info)
            
            if file_data.get('functions'):
                if lang not in functions_by_lang:
                    functions_by_lang[lang] = 0
                functions_by_lang[lang] += len(file_data['functions'])
        
        # Add detailed class breakdown
        for lang, classes in classes_by_lang.items():
            content += f"### {lang.title()} Classes ({len(classes)})\n\n"
            
            # Group by file for better organization
            classes_by_file = {}
            for cls in classes:
                file_path = cls['file']
                if file_path not in classes_by_file:
                    classes_by_file[file_path] = []
                classes_by_file[file_path].append(cls)
            
            for file_path, file_classes in classes_by_file.items():
                content += f"#### {file_path}\n\n"
                
                # Create a mini class diagram for this file
                if len(file_classes) > 1:
                    content += "```\n"
                    content += "File Class Structure:\n"
                    for i, cls in enumerate(sorted(file_classes, key=lambda x: x['line'])):
                        connector = "├──" if i < len(file_classes) - 1 else "└──"
                        content += f"{connector} {cls['name']}\n"
                        if cls.get('methods'):
                            for j, method in enumerate(cls['methods'][:3]):  # Show first 3 methods
                                method_connector = "│   ├─" if j < min(len(cls['methods']), 3) - 1 else "│   └─"
                                content += f"{method_connector} {method}()\n"
                            if len(cls['methods']) > 3:
                                content += "│   └─ ... and more methods\n"
                    content += "```\n\n"
                
                # Detailed class information
                for cls in sorted(file_classes, key=lambda x: x['line']):
                    content += f"**{cls['name']}** (line {cls['line']})\n"
                    if cls.get('docstring'):
                        content += f"- *Description*: {cls['docstring'][:150]}{'...' if len(cls['docstring']) > 150 else ''}\n"
                    if cls.get('methods'):
                        content += f"- *Methods* ({len(cls['methods'])}): {', '.join(cls['methods'][:5])}{'...' if len(cls['methods']) > 5 else ''}\n"
                    content += "\n"
        
        # Function summary
        if functions_by_lang:
            content += "## Function Summary\n\n"
            content += "| Language | Classes | Functions | Avg Functions/Class |\n"
            content += "|----------|---------|-----------|--------------------|\n"
            for lang in classes_by_lang.keys():
                class_count = len(classes_by_lang[lang])
                func_count = functions_by_lang.get(lang, 0)
                avg_funcs = func_count / class_count if class_count > 0 else 0
                content += f"| {lang.title()} | {class_count} | {func_count} | {avg_funcs:.1f} |\n"
        
        content += """

    ## Implementation Notes

    The UML diagrams and class relationships shown above are generated based on static analysis of the codebase. 
    Actual runtime relationships may include additional dynamic interactions not captured in the static structure.

    For complete class implementation details, refer to the individual source files listed in each section.

    ---

    [← Database](./database.md) | [Web Documentation →](./web.md)
    """
        
        classes_path = os.path.join(self.docs_dir, 'classes.md')
        with open(classes_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return classes_path

    def _generate_database_md(self, metadata: Dict, database_content: str) -> str:
        """Generate database.md with comprehensive database documentation and ERD diagrams."""
        
        db_files = metadata.get('project_structure', {}).get('database_files', [])
        
        content = f"""# Database Documentation

    ## Database Overview and Entity Relationship Diagrams

    {database_content}

    ## Database Analysis Summary

    Total SQL files found: **{len(db_files)}**

    """
        
        if db_files:
            # Detailed SQL file analysis
            content += "## SQL Scripts Analysis\n\n"
            content += "| File | Lines | Tables | Procedures | Purpose |\n"
            content += "|------|-------|--------|------------|--------|\n"
            
            all_tables = []
            all_procedures = []
            all_functions = []
            
            for file_data in sorted(db_files, key=lambda x: x.get('lines', 0), reverse=True):
                purpose = self._infer_sql_purpose(file_data['path'])
                tables_count = len(file_data.get('tables', []))
                procedures_count = len(file_data.get('procedures', []))
                
                content += f"| `{file_data['path']}` | {file_data.get('lines', 0)} | {tables_count} | {procedures_count} | {purpose} |\n"
                
                # Collect all database objects
                all_tables.extend(file_data.get('tables', []))
                all_procedures.extend(file_data.get('procedures', []))
                all_functions.extend(file_data.get('functions', []))
            
            # Database Objects Summary
            if all_tables:
                content += f"\n## Database Tables ({len(all_tables)} found)\n\n"
                
                # Group tables by SQL file for better organization
                tables_by_file = {}
                for table in all_tables:
                    # Find which file contains this table
                    for file_data in db_files:
                        if table in file_data.get('tables', []):
                            file_path = file_data['path']
                            if file_path not in tables_by_file:
                                tables_by_file[file_path] = []
                            tables_by_file[file_path].append(table)
                            break
                
                for file_path, tables in tables_by_file.items():
                    content += f"### {file_path}\n\n"
                    for table in sorted(tables, key=lambda x: x.get('line', 0)):
                        content += f"- **{table['name']}** (line {table.get('line', 'unknown')})\n"
                    content += "\n"
            
            if all_procedures:
                content += f"## Stored Procedures and Functions ({len(all_procedures)} found)\n\n"
                
                # Group procedures by file
                procs_by_file = {}
                for proc in all_procedures:
                    # Find which file contains this procedure
                    for file_data in db_files:
                        if proc in file_data.get('procedures', []):
                            file_path = file_data['path']
                            if file_path not in procs_by_file:
                                procs_by_file[file_path] = []
                            procs_by_file[file_path].append(proc)
                            break
                
                for file_path, procedures in procs_by_file.items():
                    content += f"### {file_path}\n\n"
                    for proc in sorted(procedures, key=lambda x: x.get('line', 0)):
                        content += f"- **{proc['name']}** (line {proc.get('line', 'unknown')})\n"
                    content += "\n"
            
            # Database Dependencies Analysis
            content += "## Database Dependencies\n\n"
            dependencies = []
            for file_data in db_files:
                for dep in file_data.get('dependencies', []):
                    if dep['type'] == 'table_reference':
                        dependencies.append({
                            'file': file_data['path'],
                            'references': dep['name'],
                            'line': dep.get('line', 'unknown')
                        })
            
            if dependencies:
                content += "Foreign key references and table dependencies:\n\n"
                deps_by_file = {}
                for dep in dependencies:
                    file_path = dep['file']
                    if file_path not in deps_by_file:
                        deps_by_file[file_path] = []
                    deps_by_file[file_path].append(dep)
                
                for file_path, file_deps in deps_by_file.items():
                    content += f"**{file_path}**:\n"
                    for dep in file_deps:
                        content += f"- References `{dep['references']}` (line {dep['line']})\n"
                    content += "\n"
            else:
                content += "No explicit foreign key references detected in the SQL files.\n\n"
        
        else:
            content += "*No SQL files detected in the project.*\n\n"
            content += "If this project uses a database, the connection might be configured through:\n"
            content += "- External database configuration\n"
            content += "- ORM frameworks (Hibernate, JPA, etc.)\n"
            content += "- Application property files\n"
            content += "- Environment variables\n\n"
        
        content += """
    ## Database Setup and Configuration

    *Refer to the specific SQL scripts above for detailed database setup and configuration instructions.*

    ## Data Relationships and Integrity

    *Entity relationships are defined through foreign key constraints and table references found in the SQL scripts. The ERD diagrams above show the logical relationships between data entities.*

    ## Performance and Optimization

    Based on the database structure analysis:
    - Consider indexing strategies for frequently queried columns
    - Implement proper normalization based on the table relationships shown
    - Use connection pooling for database access optimization
    - Monitor query performance for complex joins between related tables

    ---

    [← Architecture](./architecture.md) | [Classes Documentation →](./classes.md)
    """
        
        db_path = os.path.join(self.docs_dir, 'database.md')
        with open(db_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return db_path

    def _generate_web_md(self, metadata: Dict, web_content: str) -> str:
        """Generate web.md with comprehensive web interface documentation and flow diagrams."""
        
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        
        content = f"""# Web Interface Documentation

    ## Web Application Flow and Response Diagrams

    {web_content}

    ## Web Components Analysis

    Total web files: **{len(web_files)}**

    """
        
        if web_files:
            # Categorize web files
            jsp_files = [f for f in web_files if f['language'] == 'jsp']
            html_files = [f for f in web_files if f['language'] == 'html']
            css_files = [f for f in web_files if f['language'] == 'css']
            js_files = [f for f in web_files if f['language'] in ['javascript', 'typescript']]
            
            # JSP Pages Analysis
            if jsp_files:
                content += f"## JSP Pages Analysis ({len(jsp_files)})\n\n"
                content += "| Page | Lines | Includes | Java Imports | Purpose |\n"
                content += "|------|-------|----------|--------------|--------|\n"
                
                for jsp in sorted(jsp_files, key=lambda x: x['path']):
                    includes = len(jsp.get('jsp_includes', []))
                    imports = len(jsp.get('java_imports', []))
                    purpose = self._infer_jsp_purpose(jsp['path'])
                    content += f"| `{jsp['path']}` | {jsp.get('lines', 0)} | {includes} | {imports} | {purpose} |\n"
                
                # Navigation Flow Analysis
                content += "\n### Navigation Flow Analysis\n\n"
                all_includes = []
                all_forwards = []
                navigation_map = {}
                
                for jsp in jsp_files:
                    jsp_path = jsp['path']
                    navigation_map[jsp_path] = {
                        'includes': jsp.get('jsp_includes', []),
                        'forwards': [],
                        'dependencies': []
                    }
                    
                    all_includes.extend(jsp.get('jsp_includes', []))
                    for dep in jsp.get('dependencies', []):
                        if dep['type'] == 'jsp_forward':
                            all_forwards.append({'from': jsp_path, 'to': dep['name']})
                            navigation_map[jsp_path]['forwards'].append(dep['name'])
                        elif dep['type'] == 'jsp_include':
                            navigation_map[jsp_path]['dependencies'].append(dep['name'])
                
                # Create navigation flow diagram
                if all_forwards:
                    content += "#### Page Navigation Flow\n\n"
                    content += "```\nJSP Navigation Map:\n"
                    for jsp_path, nav_info in navigation_map.items():
                        if nav_info['forwards'] or nav_info['includes']:
                            jsp_name = jsp_path.split('/')[-1]
                            content += f"\n{jsp_name}\n"
                            
                            if nav_info['forwards']:
                                content += "├── Forwards to:\n"
                                for i, forward in enumerate(nav_info['forwards']):
                                    connector = "│   ├──" if i < len(nav_info['forwards']) - 1 else "│   └──"
                                    content += f"{connector} {forward}\n"
                            
                            if nav_info['includes']:
                                content += "└── Includes:\n"
                                for i, include in enumerate(nav_info['includes']):
                                    connector = "    ├──" if i < len(nav_info['includes']) - 1 else "    └──"
                                    content += f"{connector} {include}\n"
                    content += "```\n\n"
                
                if all_includes:
                    unique_includes = list(set(all_includes))
                    content += f"**Common Includes**: {', '.join(unique_includes[:10])}{'...' if len(unique_includes) > 10 else ''}\n\n"
                
                if all_forwards:
                    content += f"**Page Forwards**: {len(all_forwards)} navigation paths detected\n\n"
            
            # HTML Pages Analysis
            if html_files:
                content += f"## HTML Pages Analysis ({len(html_files)})\n\n"
                content += "| File | Lines | Major Tags | Purpose |\n"
                content += "|------|-------|------------|--------|\n"
                
                for html in sorted(html_files, key=lambda x: x['path']):
                    major_tags = ""
                    if html.get('tags'):
                        top_tags = sorted(html['tags'].items(), key=lambda x: x[1], reverse=True)[:3]
                        major_tags = ', '.join([f'{tag}({count})' for tag, count in top_tags])
                    
                    purpose = self._infer_html_purpose(html['path'])
                    content += f"| `{html['path']}` | {html.get('lines', 0)} | {major_tags} | {purpose} |\n"
                content += "\n"
            
            # CSS Stylesheets Analysis
            if css_files:
                content += f"## Stylesheets Analysis ({len(css_files)})\n\n"
                content += "| File | Lines | Rules | Purpose |\n"
                content += "|------|-------|-------|--------|\n"
                
                for css in sorted(css_files, key=lambda x: x['path']):
                    purpose = self._infer_css_purpose(css['path'])
                    rules_count = css.get('total_rules', 0)
                    content += f"| `{css['path']}` | {css.get('lines', 0)} | {rules_count} | {purpose} |\n"
                content += "\n"
            
            # JavaScript Analysis
            if js_files:
                content += f"## JavaScript Analysis ({len(js_files)})\n\n"
                content += "| File | Lines | Functions | Purpose |\n"
                content += "|------|-------|-----------|--------|\n"
                
                for js in sorted(js_files, key=lambda x: x['path']):
                    functions = len(js.get('functions', []))
                    purpose = self._infer_js_purpose(js['path'])
                    content += f"| `{js['path']}` | {js.get('lines', 0)} | {functions} | {purpose} |\n"
                content += "\n"
            
            # Web Technology Stack Summary
            content += "## Technology Stack Summary\n\n"
            content += f"- **Server-Side Rendering**: {len(jsp_files)} JSP pages\n"
            content += f"- **Static Content**: {len(html_files)} HTML pages\n"
            content += f"- **Styling**: {len(css_files)} CSS files\n"
            content += f"- **Client-Side Logic**: {len(js_files)} JavaScript files\n\n"
            
            # Response Pattern Analysis
            content += "## Web Application Response Patterns\n\n"
            
            if jsp_files:
                content += "### Server-Side Response Pattern (JSP)\n"
                content += "```\n"
                content += "User Request → Web Server → JSP Engine → Java Processing → HTML Response\n"
                content += "     ↑                                                        │\n"
                content += "     └──────────────── Rendered HTML Page ──────────────────┘\n"
                content += "```\n\n"
                
                content += "**Characteristics:**\n"
                content += "- Dynamic content generation on server\n"
                content += "- Java business logic integration\n"
                content += "- Session state management\n"
                content += "- Form processing and validation\n\n"
            
            if js_files:
                content += "### Client-Side Response Pattern (JavaScript)\n"
                content += "```\n"
                content += "User Action → JavaScript Handler → DOM Manipulation → Visual Update\n"
                content += "     ↑              │                                     │\n"
                content += "     │              └── AJAX Request → Server → JSON ──┘\n"
                content += "     └────────────────── Interactive Response ──────────────\n"
                content += "```\n\n"
                
                content += "**Characteristics:**\n"
                content += "- Immediate user feedback\n"
                content += "- Asynchronous server communication\n"
                content += "- Dynamic content updates\n"
                content += "- Enhanced user experience\n\n"
            
            # User Experience Flow
            content += "## User Experience Flow\n\n"
            
            # Identify entry points
            entry_points = []
            for jsp in jsp_files:
                jsp_name = jsp['path'].split('/')[-1].lower()
                if any(keyword in jsp_name for keyword in ['index', 'home', 'main', 'login', 'welcome']):
                    entry_points.append(jsp['path'])
            
            if entry_points:
                content += f"### Identified Entry Points\n"
                for entry in entry_points:
                    content += f"- `{entry}` - Primary application entry\n"
                content += "\n"
            
            # Create user journey map
            content += "### Typical User Journey\n\n"
            content += "```\n"
            if entry_points:
                main_entry = entry_points[0].split('/')[-1]
                content += f"1. User visits {main_entry}\n"
                content += "   ├── Authentication check\n"
                content += "   ├── Session initialization\n"
                content += "   └── Content rendering\n"
                content += "        │\n"
                content += "2. User interacts with interface\n"
                content += "   ├── Form submissions\n"
                content += "   ├── Navigation actions\n"
                content += "   └── Dynamic updates\n"
                content += "        │\n"
                content += "3. Server processes requests\n"
                content += "   ├── Business logic execution\n"
                content += "   ├── Data persistence\n"
                content += "   └── Response generation\n"
            else:
                content += "1. User accesses web application\n"
                content += "2. Server processes request\n"
                content += "3. Dynamic content generated\n"
                content += "4. Response sent to browser\n"
                content += "5. Client-side enhancements applied\n"
            content += "```\n\n"
        
        else:
            content += "*No web files detected in the project.*\n\n"
            content += "This might indicate:\n"
            content += "- A backend-only service (API)\n"
            content += "- Console/desktop application\n"
            content += "- Web files located outside the scanned directory\n"
            content += "- Framework-based application with non-standard file extensions\n\n"
        
        content += """
    ## API Endpoints and Web Services

    *REST API endpoints and web service interfaces are documented based on the backend implementation analysis. Refer to the Architecture section for service layer details.*

    ## Security Considerations

    - **Input Validation**: Server-side validation for all user inputs
    - **Session Management**: Secure session handling and timeout policies  
    - **XSS Prevention**: Output encoding and CSP headers
    - **CSRF Protection**: Token-based request validation
    - **Authentication**: Secure login and authorization mechanisms

    ## Performance Optimization

    - **Static Resource Caching**: CSS, JavaScript, and image optimization
    - **Database Query Optimization**: Efficient data retrieval patterns
    - **Session Management**: Optimized session storage and cleanup
    - **Response Compression**: Gzip compression for better performance

    ---

    [← Classes](./classes.md) | [Back to Overview](./index.md)
    """
        
        web_path = os.path.join(self.docs_dir, 'web.md')
        with open(web_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return web_path

    # Helper methods for purpose inference

    def _infer_jsp_purpose(self, file_path: str) -> str:
        """Infer the purpose of JSP file based on name and path."""
        path_lower = file_path.lower()
        filename = path_lower.split('/')[-1]
        
        if 'index' in filename or 'home' in filename or 'main' in filename:
            return "Main entry page"
        elif 'login' in filename or 'auth' in filename:
            return "Authentication"
        elif 'dashboard' in filename or 'admin' in filename:
            return "Admin interface"
        elif 'form' in filename or 'input' in filename:
            return "Data input form"
        elif 'list' in filename or 'table' in filename:
            return "Data display"
        elif 'detail' in filename or 'view' in filename:
            return "Detail view"
        elif 'error' in filename:
            return "Error handling"
        elif 'include' in path_lower or 'fragment' in path_lower:
            return "Reusable component"
        else:
            return "Business functionality"

    def _infer_html_purpose(self, file_path: str) -> str:
        """Infer the purpose of HTML file based on name."""
        path_lower = file_path.lower()
        filename = path_lower.split('/')[-1]
        
        if 'index' in filename:
            return "Landing page"
        elif 'template' in filename or 'layout' in filename:
            return "Page template"
        elif 'component' in filename:
            return "UI component"
        elif 'form' in filename:
            return "Form interface"
        elif 'modal' in filename or 'popup' in filename:
            return "Modal dialog"
        else:
            return "Static content"

    def _infer_css_purpose(self, file_path: str) -> str:
        """Infer the purpose of CSS file based on name."""
        path_lower = file_path.lower()
        filename = path_lower.split('/')[-1]
        
        if 'style' in filename or 'main' in filename:
            return "Main stylesheet"
        elif 'bootstrap' in filename or 'framework' in filename:
            return "UI framework"
        elif 'component' in filename:
            return "Component styles"
        elif 'theme' in filename:
            return "Theme/branding"
        elif 'responsive' in filename or 'mobile' in filename:
            return "Responsive design"
        else:
            return "Custom styling"

    def _infer_js_purpose(self, file_path: str) -> str:
        """Infer the purpose of JavaScript file based on name."""
        path_lower = file_path.lower()
        filename = path_lower.split('/')[-1]
        
        if 'main' in filename or 'app' in filename:
            return "Main application"
        elif 'jquery' in filename or 'library' in filename:
            return "JavaScript library"
        elif 'component' in filename:
            return "UI component logic"
        elif 'api' in filename or 'service' in filename:
            return "API communication"
        elif 'validation' in filename:
            return "Form validation"
        elif 'util' in filename or 'helper' in filename:
            return "Utility functions"
        else:
            return "Interactive features"
    
    def _generate_consolidated_html(self, generated_files: Dict, metadata: Dict) -> str:
        """Generate consolidated HTML documentation."""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .nav {{ background: #343a40; padding: 15px; text-align: center; }}
        .nav a {{ color: white; text-decoration: none; margin: 0 15px; padding: 8px 16px; border-radius: 4px; display: inline-block; }}
        .nav a:hover {{ background: #495057; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; padding-bottom: 30px; border-bottom: 1px solid #dee2e6; }}
        .section:last-child {{ border-bottom: none; }}
        h1 {{ color: #2c3e50; margin-bottom: 20px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h3 {{ color: #7f8c8d; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #3498db; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        code {{ background: #f1f3f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 6px; overflow-x: auto; }}
        .toc {{ background: #e9ecef; padding: 20px; border-radius: 6px; margin-bottom: 30px; }}
        .toc ul {{ list-style-type: none; padding-left: 0; }}
        .toc li {{ margin: 8px 0; }}
        .toc a {{ text-decoration: none; color: #495057; }}
        .toc a:hover {{ color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Project Documentation</h1>
            <p>Comprehensive codebase analysis and documentation</p>
            <p><small>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
        
        <div class="nav">
            <a href="#overview">Overview</a>
            <a href="#architecture">Architecture</a>
            <a href="#database">Database</a>
            <a href="#classes">Classes</a>
            <a href="#web">Web Interface</a>
        </div>
        
        <div class="content">
"""
        
        # Add table of contents
        html_content += """
            <div class="toc">
                <h3>Table of Contents</h3>
                <ul>
                    <li><a href="#overview">📊 Project Overview</a></li>
                    <li><a href="#architecture">🏗️ System Architecture</a></li>
                    <li><a href="#database">🗄️ Database Design</a></li>
                    <li><a href="#classes">🏷️ Classes & Objects</a></li>
                    <li><a href="#web">🌐 Web Interface</a></li>
                </ul>
            </div>
"""
        
        # Convert each markdown file to HTML section
        sections = [
            ('overview', 'Project Overview', 'index'),
            ('architecture', 'System Architecture', 'architecture'),
            ('database', 'Database Design', 'database'),
            ('classes', 'Classes & Objects', 'classes'),
            ('web', 'Web Interface', 'web')
        ]
        
        for section_id, section_title, file_key in sections:
            file_path = generated_files.get(file_key)
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Convert markdown to HTML (basic conversion)
                html_section = self._markdown_to_html(md_content)
                
                html_content += f"""
            <div class="section" id="{section_id}">
                <h1>{section_title}</h1>
                {html_section}
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>"""
        
        html_path = os.path.join(self.output_dir, 'documentation.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _generate_consolidated_pdf(self, generated_files: Dict, metadata: Dict) -> str:
        """Generate PDF from documentation using ReportLab."""
        pdf_path = os.path.join(self.output_dir, 'documentation.pdf')
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2c3e50')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                textColor=colors.HexColor('#34495e')
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=6,
                textColor=colors.HexColor('#7f8c8d')
            )
            
            # Build PDF content
            story = []
            
            # Title page
            story.append(Paragraph("Project Documentation", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            
            # Project statistics table
            stats_data = [
                ['Metric', 'Value'],
                ['Total Files', str(metadata['total_files'])],
                ['Total Lines of Code', f"{metadata['total_lines']:,}"],
                ['Languages Used', str(len(metadata['language_stats']))]
            ]
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Project Statistics", heading_style))
            story.append(stats_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Language breakdown
            story.append(Paragraph("Technology Stack", heading_style))
            for lang, stats in metadata['language_stats'].items():
                percentage = (stats['lines'] / metadata['total_lines'] * 100) if metadata['total_lines'] > 0 else 0
                story.append(Paragraph(
                    f"<b>{lang.title()}:</b> {stats['files']} files, {stats['lines']:,} lines ({percentage:.1f}%)",
                    styles['Normal']
                ))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Add content from each section
            sections = [
                ('Overview', 'index'),
                ('Architecture', 'architecture'),
                ('Database', 'database'),
                ('Classes', 'classes'),
                ('Web Interface', 'web')
            ]
            
            for section_title, file_key in sections:
                file_path = generated_files.get(file_key)
                if file_path and os.path.exists(file_path):
                    story.append(Paragraph(section_title, heading_style))
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            md_content = f.read()
                        
                        # Convert markdown content to paragraphs
                        paragraphs = self._markdown_to_pdf_paragraphs(md_content, styles)
                        story.extend(paragraphs)
                        
                    except Exception as e:
                        story.append(Paragraph(f"Error reading {section_title}: {str(e)}", styles['Normal']))
                    
                    story.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(story)
            return pdf_path
            
        except Exception as e:
            print(f"Warning: PDF generation with ReportLab failed: {e}")
            return None
    
    def _markdown_to_html(self, md_content: str) -> str:
        """Convert markdown to HTML (basic implementation)."""
        try:
            return markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        except:
            # Fallback: basic conversion
            html = md_content
            # Convert headers
            html = re.sub(r'^### (.*)', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.*)', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'^# (.*)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
            
            # Convert tables (basic)
            html = re.sub(r'\|(.+)\|', r'<tr><td>\1</td></tr>', html)
            
            # Convert paragraphs
            html = html.replace('\n\n', '</p><p>')
            html = '<p>' + html + '</p>'
            
            # Convert code blocks
            html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
            
            return html
    
    def _markdown_to_pdf_paragraphs(self, md_content: str, styles):
        """Convert markdown content to ReportLab paragraphs."""
        paragraphs = []
        lines = md_content.split('\n')
        
        current_paragraph = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                continue
            
            # Handle headers
            if line.startswith('### '):
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                paragraphs.append(Paragraph(line[4:], styles['Heading3']))
                continue
            elif line.startswith('## '):
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                paragraphs.append(Paragraph(line[3:], styles['Heading2']))
                continue
            elif line.startswith('# '):
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                paragraphs.append(Paragraph(line[2:], styles['Heading1']))
                continue
            
            # Handle tables (simplified)
            if '|' in line and not in_table:
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                in_table = True
                # Add table as simple text for now
                paragraphs.append(Paragraph(line.replace('|', ' | '), styles['Normal']))
                continue
            elif '|' in line and in_table:
                paragraphs.append(Paragraph(line.replace('|', ' | '), styles['Normal']))
                continue
            elif in_table and not '|' in line:
                in_table = False
            
            # Handle bullet points
            if line.startswith('- ') or line.startswith('* '):
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                paragraphs.append(Paragraph(line[2:], styles['Normal']))
                continue
            
            # Handle code blocks (simple)
            if line.startswith('```'):
                if current_paragraph:
                    paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                    current_paragraph = []
                continue
            
            # Regular text
            current_paragraph.append(line)
        
        # Add any remaining paragraph
        if current_paragraph:
            paragraphs.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
        
        return paragraphs
    
    def _infer_sql_purpose(self, file_path: str) -> str:
        """Infer the purpose of SQL file based on name."""
        path_lower = file_path.lower()
        if 'create' in path_lower or 'schema' in path_lower:
            return "Table creation/schema"
        elif 'insert' in path_lower or 'data' in path_lower:
            return "Data insertion"
        elif 'update' in path_lower:
            return "Data updates"
        elif 'proc' in path_lower or 'function' in path_lower:
            return "Stored procedures"
        elif 'view' in path_lower:
            return "Database views"
        elif 'trigger' in path_lower:
            return "Database triggers"
        else:
            return "General SQL script"