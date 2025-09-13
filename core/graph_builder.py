import networkx as nx
import plotly.graph_objects as go
import plotly.offline as pyo
from typing import Dict, List
import json

class DependencyGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def build_dependency_graph(self, metadata: Dict) -> nx.DiGraph:
        """Build dependency graph from parsed metadata."""
        self.graph.clear()
        
        # Add nodes for all files
        for file_data in metadata['files']:
            file_path = file_data['path']
            self.graph.add_node(file_path, **file_data)
        
        # Add edges for dependencies
        for file_data in metadata['files']:
            file_path = file_data['path']
            imports = file_data.get('imports', [])
            
            for imp in imports:
                # Try to resolve import to actual file
                resolved_path = self._resolve_import(imp, file_path, metadata)
                if resolved_path:
                    self.graph.add_edge(file_path, resolved_path, import_name=imp)
        
        return self.graph
    
    def _resolve_import(self, import_name: str, current_file: str, metadata: Dict) -> str:
        """Try to resolve import to actual file path."""
        # Simple heuristic - look for files that might match the import
        for file_data in metadata['files']:
            file_path = file_data['path']
            
            # Check if import matches filename (without extension)
            filename = file_path.split('/')[-1].split('.')[0]
            if import_name.endswith(filename) or filename in import_name:
                return file_path
                
        return None
    
    def generate_dependency_visualization(self, output_path: str) -> str:
        """Generate interactive dependency graph visualization."""
        if not self.graph.nodes():
            return ""
            
        # Use spring layout for positioning
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # Extract node information
        node_trace = go.Scatter(
            x=[pos[node][0] for node in self.graph.nodes()],
            y=[pos[node][1] for node in self.graph.nodes()],
            mode='markers+text',
            text=[node.split('/')[-1] for node in self.graph.nodes()],
            textposition="middle center",
            hovertext=[f"File: {node}<br>Language: {self.graph.nodes[node].get('language', 'unknown')}" 
                      for node in self.graph.nodes()],
            hoverinfo='text',
            marker=dict(size=20, color='lightblue', line=dict(width=2, color='black'))
        )
        
        # Extract edge information
        edge_x = []
        edge_y = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Codebase Dependency Graph',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[dict(
                               text="Dependency relationships between files",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="#888", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        # Save as HTML
        graph_path = f"{output_path}/dependency_graph.html"
        pyo.plot(fig, filename=graph_path, auto_open=False)
        return graph_path
    
    def get_graph_statistics(self) -> Dict:
        """Get statistics about the dependency graph."""
        if not self.graph.nodes():
            return {}
            
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph),
            'strongly_connected_components': nx.number_strongly_connected_components(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
        }

