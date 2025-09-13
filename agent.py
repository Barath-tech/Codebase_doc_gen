import os
import sys
import json
import argparse
import shutil
from datetime import datetime
from typing import Dict, Optional

from core.parser import CodebaseParser
from core.graph_builder import DependencyGraphBuilder
from core.llm_client import LLMClient
from docs.generator import DocumentationGenerator

class DocumentationAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.parser = CodebaseParser()
        self.graph_builder = DependencyGraphBuilder()
        self.llm_client = LLMClient()
        self.doc_generator = DocumentationGenerator(output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def run(self, github_url: str, max_file_summaries: int = 20) -> Dict[str, str]:
        """
        Run the complete documentation generation pipeline.
        
        Args:
            github_url: GitHub repository URL
            max_file_summaries: Maximum number of files to generate detailed summaries for
            
        Returns:
            Dictionary with paths to generated files
        """
        print("🚀 Starting AI Code Documentation Agent...")
        
        try:
            # Step 1: Clone and parse repository
            print("📥 Cloning repository...")
            repo_path = self.parser.clone_repository(github_url)
            
            print("🔍 Parsing codebase...")
            metadata = self.parser.parse_codebase(repo_path)
            
            if metadata['total_files'] == 0:
                raise Exception("No supported files found in repository")
            
            print(f"✅ Found {metadata['total_files']} files in {len(metadata['language_stats'])} languages")
            
            # Step 2: Build dependency graph
            print("🕸️ Building dependency graph...")
            dependency_graph = self.graph_builder.build_dependency_graph(metadata)
            graph_stats = self.graph_builder.get_graph_statistics()
            
            # Generate dependency visualization
            dependency_graph_path = self.graph_builder.generate_dependency_visualization(self.output_dir)
            
            # Step 3: Generate LLM summaries
            print("🤖 Generating AI summaries...")
            llm_summaries = self._generate_summaries(metadata, graph_stats, max_file_summaries)
            
            # Step 4: Generate documentation
            print("📝 Generating documentation...")
            html_path, pdf_path, markdown_path = self.doc_generator.generate_documentation(
                metadata, llm_summaries, graph_stats, dependency_graph_path
            )
            
            # Step 5: Save metadata
            metadata_path = os.path.join(self.output_dir, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': metadata,
                    'graph_stats': graph_stats,
                    'generation_time': datetime.now().isoformat(),
                    'repository_url': github_url
                }, f, indent=2, default=str)
            
            # Cleanup temporary repository
            shutil.rmtree(repo_path, ignore_errors=True)
            
            # Prepare results
            results = {
                'html_documentation': html_path,
                'markdown_documentation': markdown_path,
                'metadata': metadata_path,
                'dependency_graph': dependency_graph_path
            }
            
            if pdf_path:
                results['pdf_documentation'] = pdf_path
            
            print("✨ Documentation generation complete!")
            print(f"📄 HTML: {html_path}")
            if pdf_path:
                print(f"📄 PDF: {pdf_path}")
            print(f"📄 Markdown: {markdown_path}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def _generate_summaries(self, metadata: Dict, graph_stats: Dict, max_files: int) -> Dict:
        """Generate LLM summaries for codebase and selected files."""
        summaries = {
            'file_summaries': {},
            'codebase_summary': '',
            'architectural_insights': ''
        }
        
        try:
            # Generate overall codebase summary
            print("  📊 Analyzing overall codebase...")
            summaries['codebase_summary'] = self.llm_client.summarize_codebase(metadata)
            
            # Generate architectural insights
            print("  🏗️ Generating architectural insights...")
            summaries['architectural_insights'] = self.llm_client.generate_architectural_insights(
                metadata, graph_stats
            )
            
            # Generate file summaries for most important files
            important_files = self._select_important_files(metadata['files'], max_files)
            
            for i, file_data in enumerate(important_files):
                print(f"  📄 Analyzing file {i+1}/{len(important_files)}: {file_data['path']}")
                summary = self.llm_client.summarize_file(file_data)
                summaries['file_summaries'][file_data['path']] = summary
                
        except Exception as e:
            print(f"⚠️  Warning: LLM summary generation failed: {e}")
            summaries['codebase_summary'] = "LLM analysis unavailable - check API key configuration"
            summaries['architectural_insights'] = "Architectural analysis unavailable"
        
        return summaries
    
    def _select_important_files(self, files: list, max_files: int) -> list:
        """Select the most important files for detailed analysis."""
        # Priority scoring based on multiple factors
        def score_file(file_data):
            score = 0
            
            # Language importance (Python, JS, Java get higher scores)
            lang_scores = {'python': 10, 'javascript': 9, 'typescript': 9, 'java': 8, 'html': 5, 'css': 3}
            score += lang_scores.get(file_data['language'], 1)
            
            # File size (moderate size preferred - not too small, not too large)
            lines = file_data['lines']
            if 50 <= lines <= 500:
                score += 8
            elif 20 <= lines <= 1000:
                score += 5
            elif lines > 1000:
                score += 2
            
            # Complexity indicators
            score += min(len(file_data.get('functions', [])) * 2, 10)
            score += min(len(file_data.get('classes', [])) * 3, 15)
            score += min(len(file_data.get('imports', [])), 5)
            
            # File name patterns (main files, configs, etc.)
            filename = file_data['path'].lower()
            if any(term in filename for term in ['main', 'index', 'app', 'server', 'client']):
                score += 15
            if any(term in filename for term in ['config', 'setting', 'util', 'helper']):
                score += 8
            if any(term in filename for term in ['test', 'spec']):
                score -= 5  # Lower priority for tests
                
            return score
        
        # Sort files by importance score
        scored_files = [(score_file(f), f) for f in files]
        scored_files.sort(key=lambda x: x[0], reverse=True)
        
        return [f for _, f in scored_files[:max_files]]

def main():
    parser = argparse.ArgumentParser(description='AI Code Documentation Agent')
    parser.add_argument('github_url', help='GitHub repository URL')
    parser.add_argument('--output', '-o', default='output', help='Output directory (default: output)')
    parser.add_argument('--max-summaries', '-m', type=int, default=20, 
                       help='Maximum number of file summaries to generate (default: 20)')
    parser.add_argument('--no-pdf', action='store_true', help='Skip PDF generation')
    
    args = parser.parse_args()
    
    # Validate GitHub URL
    if not args.github_url.startswith(('https://github.com/', 'git@github.com:')):
        print("❌ Error: Please provide a valid GitHub URL")
        sys.exit(1)
    
    # Check for API key
    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  Warning: GITHUB_TOKEN not found. LLM summaries will be unavailable.")
        print("   Set your API key: export GITHUB_TOKEN='your-key-here'")
    
    try:
        agent = DocumentationAgent(args.output)
        results = agent.run(args.github_url, args.max_summaries)
        
        print("\n🎉 Documentation generated successfully!")
        print("📂 Generated files:")
        for name, path in results.items():
            if path:
                print(f"   {name}: {path}")
                
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
