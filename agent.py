#!/usr/bin/env python3
"""
Enhanced AI Code Documentation Agent
Generates structured documentation with JSP support and improved dependency analysis.
"""

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
from docs.generator import StructuredDocumentationGenerator

class EnhancedDocumentationAgent:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.parser = CodebaseParser()
        self.graph_builder = DependencyGraphBuilder()
        self.llm_client = LLMClient()
        self.doc_generator = StructuredDocumentationGenerator(output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def run(self, github_url: str, max_file_summaries: int = 20) -> Dict[str, str]:
        """
        Run the enhanced documentation generation pipeline.
        
        Args:
            github_url: GitHub repository URL
            max_file_summaries: Maximum number of files to generate detailed summaries for
            
        Returns:
            Dictionary with paths to generated files
        """
        print("🚀 Starting Enhanced AI Code Documentation Agent...")
        
        try:
            # Step 1: Clone and parse repository
            print("📥 Cloning repository...")
            repo_path = self.parser.clone_repository(github_url)
            
            print("🔍 Parsing codebase (including JSP files)...")
            metadata = self.parser.parse_codebase(repo_path)
            
            if metadata['total_files'] == 0:
                raise Exception("No supported files found in repository")
            
            print(f"✅ Found {metadata['total_files']} files in {len(metadata['language_stats'])} languages")
            
            # Display language breakdown
            for lang, stats in metadata['language_stats'].items():
                print(f"   - {lang.title()}: {stats['files']} files")
            
            # Step 2: Build enhanced dependency graph
            print("🕸️ Building enhanced dependency graph...")
            dependency_graph = self.graph_builder.build_dependency_graph(metadata)
            graph_stats = self.graph_builder.get_graph_statistics()
            
            print(f"   - Graph nodes: {graph_stats.get('total_nodes', 0)}")
            print(f"   - Dependencies: {graph_stats.get('total_edges', 0)}")
            
            # Generate dependency visualization
            dependency_graph_path = self.graph_builder.generate_dependency_visualization(self.output_dir)
            
            # Step 3: Generate structured LLM documentation
            print("🤖 Generating structured AI documentation...")
            print("   - Overview section...")
            print("   - Architecture analysis...")
            print("   - Database documentation...")
            print("   - Class documentation...")
            print("   - Web interface documentation...")
            
            llm_sections = self.llm_client.generate_structured_documentation(metadata, graph_stats)
            
            # Step 4: Generate structured documentation files
            print("📝 Generating structured documentation files...")
            print("   - ./docs/index.md")
            print("   - ./docs/architecture.md")
            print("   - ./docs/database.md")
            print("   - ./docs/classes.md")
            print("   - ./docs/web.md")
            
            generated_files = self.doc_generator.generate_structured_docs(
                metadata, llm_sections, graph_stats, dependency_graph_path
            )
            
            # Step 5: Save metadata
            metadata_path = os.path.join(self.output_dir, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': metadata,
                    'graph_stats': graph_stats,
                    'generation_time': datetime.now().isoformat(),
                    'repository_url': github_url,
                    'supported_languages': list(self.parser.supported_languages.values())
                }, f, indent=2, default=str)
            
            # Cleanup temporary repository
            shutil.rmtree(repo_path, ignore_errors=True)
            
            # Prepare results
            results = generated_files.copy()
            results['metadata'] = metadata_path
            results['dependency_graph'] = dependency_graph_path
            
            print("\n✨ Enhanced documentation generation complete!")
            print("\n📂 Generated documentation structure:")
            print(f"   📄 Overview: {generated_files.get('index', 'N/A')}")
            print(f"   🏗️  Architecture: {generated_files.get('architecture', 'N/A')}")
            print(f"   🗄️  Database: {generated_files.get('database', 'N/A')}")
            print(f"   🏷️  Classes: {generated_files.get('classes', 'N/A')}")
            print(f"   🌐 Web: {generated_files.get('web', 'N/A')}")
            print(f"   📊 Interactive Graph: {dependency_graph_path}")
            print(f"   📋 Consolidated HTML: {generated_files.get('html', 'N/A')}")
            if generated_files.get('pdf'):
                print(f"   📄 PDF Report: {generated_files.get('pdf')}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Enhanced AI Code Documentation Agent with JSP Support')
    parser.add_argument('github_url', help='GitHub repository URL')
    parser.add_argument('--output', '-o', default='output', help='Output directory (default: output)')
    parser.add_argument('--max-summaries', '-m', type=int, default=20, 
                       help='Maximum number of file summaries to generate (default: 20)')
    
    args = parser.parse_args()
    
    # Validate GitHub URL
    if not args.github_url.startswith(('https://github.com/', 'git@github.com:')):
        print("❌ Error: Please provide a valid GitHub URL")
        sys.exit(1)
    
    # Check for API key
    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  Warning: GITHUB_TOKEN not found. LLM documentation will be unavailable.")
        print("   Set your API key: export GITHUB_TOKEN='your-key-here'")
        print("   Or create a .env file with: GITHUB_TOKEN=your-key-here")
    
    try:
        agent = EnhancedDocumentationAgent(args.output)
        results = agent.run(args.github_url, args.max_summaries)
        
        print(f"\n🎉 Documentation generated successfully in '{args.output}' directory!")
        print("\n📖 To view the documentation:")
        print(f"   - Open: {results.get('html', 'documentation.html')}")
        print("   - Browse individual markdown files in the docs/ folder")
        print(f"   - View dependency graph: {results.get('dependency_graph', 'dependency_graph.html')}")
                
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()