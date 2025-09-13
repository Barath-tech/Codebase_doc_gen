import requests
import json
from typing import Dict
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

load_dotenv()

class LLMClient:
    def __init__(self, model="meta/Llama-3.3-70B-Instruct"):
        self.client = ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
        )
        self.model = model

    def summarize_file(self, file_metadata: Dict) -> str:
        """Generate summary for a single file."""
        prompt = self._create_file_summary_prompt(file_metadata)
        return self._send_request(prompt, max_tokens=500, temperature=0.3)

    def summarize_codebase(self, metadata: Dict) -> str:
        """Generate overall codebase summary."""
        prompt = self._create_codebase_summary_prompt(metadata)
        return self._send_request(prompt, max_tokens=1000, temperature=0.3)

    def generate_architectural_insights(self, metadata: Dict, graph_stats: Dict) -> str:
        """Generate architectural insights based on codebase analysis."""
        prompt = f"""
        Analyze this codebase and provide architectural insights:
        
        Language Statistics: {json.dumps(metadata['language_stats'], indent=2)}
        Total Files: {metadata['total_files']}
        Total Lines: {metadata['total_lines']}
        
        Dependency Graph Statistics:
        - Total modules/files: {graph_stats.get('total_nodes', 0)}
        - Dependencies: {graph_stats.get('total_edges', 0)}
        - Graph density: {graph_stats.get('density', 0):.3f}
        - Is connected: {graph_stats.get('is_connected', False)}
        
        Provide insights on:
        1. Overall architecture patterns
        2. Code organization and structure
        3. Technology stack analysis
        4. Potential areas for improvement
        5. Complexity assessment
        """
        return self._send_request(prompt, max_tokens=800, temperature=0.4)

    def _create_file_summary_prompt(self, file_metadata: Dict) -> str:
        """Create prompt for file summarization."""
        content = f"""
        Analyze and summarize this {file_metadata['language']} file:
        
        File: {file_metadata['path']}
        Language: {file_metadata['language']}
        Lines of code: {file_metadata['lines']}
        
        Functions: {file_metadata.get('functions', [])}
        Classes: {file_metadata.get('classes', [])}
        Imports: {file_metadata.get('imports', [])}
        
        Provide a concise summary of:
        1. File purpose and functionality
        2. Key components (functions/classes)
        3. Dependencies and relationships
        4. Notable patterns or techniques used
        """
        return content

    def _create_codebase_summary_prompt(self, metadata: Dict) -> str:
        """Create prompt for overall codebase summarization."""
        return f"""
        Provide a comprehensive summary of this codebase:
        
        Total Files: {metadata['total_files']}
        Total Lines of Code: {metadata['total_lines']}
        
        Languages Used:
        {json.dumps(metadata['language_stats'], indent=2)}
        
        Please provide:
        1. Overall project purpose and scope
        2. Technology stack and architecture
        3. Main components and their roles
        4. Code quality and organization assessment
        5. Notable features or patterns
        """

    def _send_request(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage("You are a code documentation assistant."),
                    UserMessage(prompt),
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"