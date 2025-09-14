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
    
    def _generate_database_md(self, metadata: Dict, database_content: str) -> str:
        """Generate database.md with database documentation."""
        
        db_files = metadata.get('project_structure', {}).get('database_files', [])
        
        content = f"""# Database Documentation

## Database Overview

{database_content}

## Database Files

Total SQL files found: **{len(db_files)}**

"""
        
        if db_files:
            content += "### SQL Scripts\n\n"
            content += "| File | Lines | Purpose |\n"
            content += "|------|-------|--------|\n"
            
            for file_data in sorted(db_files, key=lambda x: x.get('lines', 0), reverse=True):
                purpose = self._infer_sql_purpose(file_data['path'])
                content += f"| `{file_data['path']}` | {file_data.get('lines', 0)} | {purpose} |\n"
            
            # Extract and display tables/procedures
            all_tables = []
            all_procedures = []
            
            for file_data in db_files:
                all_tables.extend(file_data.get('tables', []))
                all_procedures.extend(file_data.get('procedures', []))
            
            if all_tables:
                content += f"\n### Database Tables ({len(all_tables)} found)\n\n"
                for table in sorted(all_tables, key=lambda x: x['name']):
                    content += f"- **{table['name']}** (defined in line {table['line']})\n"
            
            if all_procedures:
                content += f"\n### Stored Procedures ({len(all_procedures)} found)\n\n"
                for proc in sorted(all_procedures, key=lambda x: x['name']):
                    content += f"- **{proc['name']}** (defined in line {proc['line']})\n"
        else:
            content += "*No SQL files detected in the project.*\n"
        
        content += """

## Database Setup

*Refer to the specific SQL scripts for database setup and configuration instructions.*

## Data Relationships

*Entity relationships are defined through foreign key constraints and table references found in the SQL scripts.*

---

[← Architecture](./architecture.md) | [Classes Documentation →](./classes.md)
"""
        
        db_path = os.path.join(self.docs_dir, 'database.md')
        with open(db_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return db_path
    
    def _generate_classes_md(self, metadata: Dict, classes_content: str) -> str:
        """Generate classes.md with class documentation."""
        
        content = f"""# Classes and Object-Oriented Design

## Class Overview

{classes_content}

## Class Analysis

"""
        
        # Collect all classes by language
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
        
        # Display classes by language
        for lang, classes in classes_by_lang.items():
            content += f"### {lang.title()} Classes\n\n"
            content += f"Total classes found: **{len(classes)}**\n\n"
            
            # Group by file for better organization
            classes_by_file = {}
            for cls in classes:
                file_path = cls['file']
                if file_path not in classes_by_file:
                    classes_by_file[file_path] = []
                classes_by_file[file_path].append(cls)
            
            for file_path, file_classes in classes_by_file.items():
                content += f"#### {file_path}\n\n"
                for cls in sorted(file_classes, key=lambda x: x['line']):
                    content += f"**{cls['name']}** (line {cls['line']})\n"
                    if cls.get('docstring'):
                        content += f"- *{cls['docstring'][:100]}...*\n"
                    if cls.get('methods'):
                        content += f"- Methods: {', '.join(cls['methods'])}\n"
                    content += "\n"
        
        # Function summary
        if functions_by_lang:
            content += "## Function Summary\n\n"
            content += "| Language | Function Count |\n"
            content += "|----------|---------------|\n"
            for lang, count in functions_by_lang.items():
                content += f"| {lang.title()} | {count} |\n"
        
        content += """

## Design Patterns

*Object-oriented design patterns and architectural decisions are reflected in the class structure and relationships documented above.*

---

[← Database](./database.md) | [Web Documentation →](./web.md)
"""
        
        classes_path = os.path.join(self.docs_dir, 'classes.md')
        with open(classes_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return classes_path
    
    def _generate_web_md(self, metadata: Dict, web_content: str) -> str:
        """Generate web.md with web interface documentation."""
        
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        
        content = f"""# Web Interface Documentation

## Web Overview

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
            
            # JSP Pages
            if jsp_files:
                content += f"### JSP Pages ({len(jsp_files)})\n\n"
                content += "| Page | Lines | Includes | Java Imports |\n"
                content += "|------|-------|----------|-------------|\n"
                
                for jsp in sorted(jsp_files, key=lambda x: x['path']):
                    includes = len(jsp.get('jsp_includes', []))
                    imports = len(jsp.get('java_imports', []))
                    content += f"| `{jsp['path']}` | {jsp.get('lines', 0)} | {includes} | {imports} |\n"
                
                # Navigation flow analysis
                content += "\n#### Navigation Flow\n\n"
                all_includes = []
                all_forwards = []
                
                for jsp in jsp_files:
                    all_includes.extend(jsp.get('jsp_includes', []))
                    for dep in jsp.get('dependencies', []):
                        if dep['type'] == 'jsp_forward':
                            all_forwards.append(dep['name'])
                
                if all_includes:
                    content += f"**Common Includes**: {', '.join(set(all_includes))}\n\n"
                if all_forwards:
                    content += f"**Page Forwards**: {', '.join(set(all_forwards))}\n\n"
            
            # HTML Pages
            if html_files:
                content += f"### HTML Pages ({len(html_files)})\n\n"
                for html in sorted(html_files, key=lambda x: x['path']):
                    content += f"- **{html['path']}** ({html.get('lines', 0)} lines)\n"
                    if html.get('tags'):
                        top_tags = sorted(html['tags'].items(), key=lambda x: x[1], reverse=True)[:5]
                        content += f"  - Top tags: {', '.join([f'{tag}({count})' for tag, count in top_tags])}\n"
            
            # CSS Stylesheets
            if css_files:
                content += f"\n### Stylesheets ({len(css_files)})\n\n"
                for css in sorted(css_files, key=lambda x: x['path']):
                    content += f"- **{css['path']}** ({css.get('lines', 0)} lines, {css.get('total_rules', 0)} rules)\n"
            
            # JavaScript Files
            if js_files:
                content += f"\n### JavaScript ({len(js_files)})\n\n"
                for js in sorted(js_files, key=lambda x: x['path']):
                    functions = len(js.get('functions', []))
                    content += f"- **{js['path']}** ({js.get('lines', 0)} lines, {functions} functions)\n"
        
        else:
            content += "*No web files detected in the project.*\n"
        
        content += """

## User Interface Flow

*The navigation flow and user experience paths are defined through the JSP includes, forwards, and HTML linking structure documented above.*

## API Endpoints

*REST API endpoints and web service interfaces would be documented here based on the backend implementation.*

---

[← Classes](./classes.md) | [Back to Overview](./index.md)
"""
        
        web_path = os.path.join(self.docs_dir, 'web.md')
        with open(web_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return web_path
    
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