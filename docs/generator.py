import os
from datetime import datetime
from typing import Dict
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

class DocumentationGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_documentation(self, metadata: Dict, llm_summaries: Dict,
                               graph_stats: Dict, dependency_graph_path: str) -> tuple:
        """Generate complete documentation in HTML and PDF formats (using ReportLab for PDF)."""

        # Generate markdown content
        markdown_content = self._create_markdown_content(
            metadata, llm_summaries, graph_stats, dependency_graph_path
        )

        markdown_path = os.path.join(self.output_dir, 'documentation.md')
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Generate HTML
        html_content = self._create_html_content(
            metadata, llm_summaries, graph_stats, dependency_graph_path
        )
        html_path = os.path.join(self.output_dir, 'documentation.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Generate PDF with ReportLab
        pdf_path = os.path.join(self.output_dir, 'documentation.pdf')
        try:
            self._create_pdf(markdown_content, pdf_path)
        except Exception as e:
            print(f"Warning: PDF generation failed: {e}")
            pdf_path = None

        return html_path, pdf_path, markdown_path

    def _create_pdf(self, text_content: str, pdf_path: str):
        """Create a simple PDF using ReportLab from the markdown content (as plain text)."""
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        for line in text_content.split("\n"):
            if line.startswith("# "):
                story.append(Paragraph(f"<b><font size=16>{line[2:]}</font></b>", styles["Heading1"]))
            elif line.startswith("## "):
                story.append(Paragraph(f"<b><font size=14>{line[3:]}</font></b>", styles["Heading2"]))
            elif line.startswith("### "):
                story.append(Paragraph(f"<b><font size=12>{line[4:]}</font></b>", styles["Heading3"]))
            else:
                story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

        doc.build(story)

    def _create_markdown_content(self, metadata: Dict, llm_summaries: Dict,
                                graph_stats: Dict, dependency_graph_path: str) -> str:
        """(Unchanged) Create markdown documentation content."""
        content = f"""# Codebase Documentation

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

{llm_summaries.get('codebase_summary', 'No summary available')}

## Project Statistics

- **Total Files**: {metadata['total_files']}
- **Total Lines of Code**: {metadata['total_lines']}
- **Languages Used**: {len(metadata['language_stats'])}
"""
        for lang, stats in metadata['language_stats'].items():
            content += f"- **{lang.title()}**: {stats['files']} files, {stats['lines']} lines\n"

        content += f"""
## Architectural Insights

{llm_summaries.get('architectural_insights', 'No insights available')}

## Dependency Analysis

- **Total Modules**: {graph_stats.get('total_nodes', 0)}
- **Dependencies**: {graph_stats.get('total_edges', 0)}
- **Graph Density**: {graph_stats.get('density', 0):.3f}
- **Is Connected**: {graph_stats.get('is_connected', False)}
- **Average Degree**: {graph_stats.get('average_degree', 0):.2f}

## File Analysis
"""
        files_by_lang = {}
        for file_data in metadata['files']:
            lang = file_data['language']
            files_by_lang.setdefault(lang, []).append(file_data)

        for lang, files in files_by_lang.items():
            content += f"\n### {lang.title()} Files\n\n"
            for file_data in files[:10]:
                content += f"#### {file_data['path']}\n\n"
                content += f"- **Lines**: {file_data['lines']}\n"
                if file_data.get('functions'):
                    content += f"- **Functions**: {len(file_data['functions'])}\n"
                if file_data.get('classes'):
                    content += f"- **Classes**: {len(file_data['classes'])}\n"
                if file_data.get('imports'):
                    content += f"- **Imports**: {len(file_data['imports'])}\n"
                file_summary = llm_summaries.get('file_summaries', {}).get(file_data['path'])
                if file_summary:
                    content += f"\n**Summary**: {file_summary}\n"
                content += "\n"

            if len(files) > 10:
                content += f"*... and {len(files) - 10} more {lang} files*\n\n"

        return content
    
    def _create_html_content(self, metadata: Dict, llm_summaries: Dict, 
                            graph_stats: Dict, dependency_graph_path: str) -> str:
        """Create HTML documentation content."""
        
        # Embed dependency graph if it exists
        graph_embed = ""
        if dependency_graph_path and os.path.exists(dependency_graph_path):
            try:
                with open(dependency_graph_path, 'r', encoding='utf-8') as f:
                    graph_content = f.read()
                # Extract the div content from the plotly HTML
                start = graph_content.find('<div')
                end = graph_content.rfind('</div>') + 6
                if start != -1 and end != -1:
                    graph_embed = graph_content[start:end]
            except Exception as e:
                graph_embed = f"<p>Error loading dependency graph: {e}</p>"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codebase Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-bottom: 1px solid #ecf0f1; padding-bottom: 8px; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 6px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .lang-breakdown {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }}
        .lang-tag {{ background: #3498db; color: white; padding: 5px 12px; border-radius: 15px; font-size: 0.9em; }}
        .file-analysis {{ margin-top: 30px; }}
        .file-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #3498db; }}
        .file-path {{ font-weight: bold; color: #2c3e50; }}
        .file-meta {{ color: #7f8c8d; font-size: 0.9em; margin: 5px 0; }}
        .summary {{ background: #e8f4fd; padding: 10px; border-radius: 4px; margin-top: 10px; }}
        .graph-container {{ margin: 30px 0; text-align: center; }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🔍 Codebase Documentation</h1>
        <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Project Overview</h2>
        <div class="summary">
            {llm_summaries.get('codebase_summary', 'No summary available')}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{metadata['total_files']}</div>
                <div>Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{metadata['total_lines']:,}</div>
                <div>Lines of Code</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(metadata['language_stats'])}</div>
                <div>Languages</div>
            </div>
        </div>
        
        <h3>Language Breakdown</h3>
        <div class="lang-breakdown">
"""
        
        for lang, stats in metadata['language_stats'].items():
            html_content += f'<div class="lang-tag">{lang.title()}: {stats["files"]} files</div>'
        
        html_content += f"""
        </div>
        
        <h2>🏗️ Architectural Insights</h2>
        <div class="summary">
            {llm_summaries.get('architectural_insights', 'No insights available')}
        </div>
        
        <h2>🕸️ Dependency Analysis</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{graph_stats.get('total_nodes', 0)}</div>
                <div>Modules</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{graph_stats.get('total_edges', 0)}</div>
                <div>Dependencies</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{graph_stats.get('density', 0):.3f}</div>
                <div>Graph Density</div>
            </div>
        </div>
        
        {f'<div class="graph-container"><h3>Dependency Graph</h3>{graph_embed}</div>' if graph_embed else ''}
        
        <h2>📁 File Analysis</h2>
        <div class="file-analysis">
"""
        
        # Group files by language
        files_by_lang = {}
        for file_data in metadata['files']:
            lang = file_data['language']
            if lang not in files_by_lang:
                files_by_lang[lang] = []
            files_by_lang[lang].append(file_data)
        
        for lang, files in files_by_lang.items():
            html_content += f'<h3>{lang.title()} Files ({len(files)})</h3>'
            
            # Show top 10 files per language
            for file_data in files[:10]:
                path = file_data['path']
                html_content += f"""
                <div class="file-item">
                    <div class="file-path">{path}</div>
                    <div class="file-meta">
                        Lines: {file_data['lines']} | 
                        Functions: {len(file_data.get('functions', []))} | 
                        Classes: {len(file_data.get('classes', []))} | 
                        Imports: {len(file_data.get('imports', []))}
                    </div>
"""
                
                # Add LLM summary if available
                file_summary = llm_summaries.get('file_summaries', {}).get(path)
                if file_summary:
                    html_content += f'<div class="summary">{file_summary}</div>'
                
                html_content += "</div>"
            
            if len(files) > 10:
                html_content += f'<p><em>... and {len(files) - 10} more {lang} files</em></p>'
        
        html_content += """
        </div>
    </div>
</body>
</html>"""
        
        return html_content
