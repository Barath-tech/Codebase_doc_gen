# core/graph_builder.py
import networkx as nx
import plotly.graph_objects as go
import plotly.offline as pyo
from typing import Dict, List
import json
import os

class DependencyGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def build_dependency_graph(self, metadata: Dict) -> nx.DiGraph:
        """Build improved dependency graph from parsed metadata."""
        self.graph.clear()
        
        # Create file mapping for better resolution
        file_map = {}
        for file_data in metadata['files']:
            path = file_data['path']
            filename = os.path.basename(path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Add to file mapping
            file_map[path] = file_data
            file_map[filename] = file_data
            file_map[name_without_ext] = file_data
        
        # Add nodes for all files
        for file_data in metadata['files']:
            file_path = file_data['path']
            self.graph.add_node(file_path, **file_data)
        
        # Add edges for dependencies with improved resolution
        for file_data in metadata['files']:
            current_file = file_data['path']
            dependencies = file_data.get('dependencies', [])
            
            for dep in dependencies:
                dep_name = dep['name']
                resolved_files = self._resolve_dependency(dep_name, current_file, file_map, metadata)
                
                for resolved_file in resolved_files:
                    if resolved_file != current_file:  # Avoid self-references
                        self.graph.add_edge(
                            current_file, 
                            resolved_file, 
                            dependency_type=dep['type'],
                            dependency_name=dep_name,
                            line_number=dep.get('line', 0)
                        )
        
        return self.graph
    
    def _resolve_dependency(self, dep_name: str, current_file: str, file_map: Dict, metadata: Dict) -> List[str]:
        """Enhanced dependency resolution."""
        resolved = []
        
        # Direct file path match
        if dep_name in file_map:
            resolved.append(file_map[dep_name]['path'])
            return resolved
        
        # Handle relative paths
        current_dir = os.path.dirname(current_file)
        
        # Check for relative path resolution
        potential_paths = [
            dep_name,
            os.path.join(current_dir, dep_name),
            os.path.join(current_dir, dep_name + '.jsp'),
            os.path.join(current_dir, dep_name + '.java'),
            os.path.join(current_dir, dep_name + '.js'),
            os.path.join(current_dir, dep_name + '.html'),
            dep_name + '.jsp',
            dep_name + '.java',
            dep_name + '.js',
            dep_name + '.html'
        ]
        
        for path in potential_paths:
            normalized_path = os.path.normpath(path)
            if normalized_path in file_map:
                resolved.append(file_map[normalized_path]['path'])
        
        # Pattern matching for package/class names
        if not resolved and '.' in dep_name:
            # Handle Java package imports
            class_name = dep_name.split('.')[-1]
            for file_data in metadata['files']:
                if file_data['language'] == 'java':
                    classes = file_data.get('classes', [])
                    if any(cls['name'] == class_name for cls in classes):
                        resolved.append(file_data['path'])
        
        # Fuzzy matching for similar names
        if not resolved:
            dep_base = os.path.splitext(os.path.basename(dep_name))[0].lower()
            for file_data in metadata['files']:
                file_base = os.path.splitext(os.path.basename(file_data['path']))[0].lower()
                if dep_base in file_base or file_base in dep_base:
                    resolved.append(file_data['path'])
        
        return resolved
    
    def generate_dependency_visualization(self, output_path: str) -> str:
        """Generate enhanced interactive dependency graph visualization."""
        if not self.graph.nodes():
            return ""
        
        # Use hierarchical layout for better visualization
        try:
            pos = nx.spring_layout(self.graph, k=2, iterations=100, seed=42)
        except:
            pos = nx.random_layout(self.graph, seed=42)
        
        # Color nodes by language
        language_colors = {
            'python': '#3776ab',
            'java': '#ed8b00',
            'javascript': '#f7df1e',
            'jsp': '#e76f00',
            'html': '#e34c26',
            'css': '#1572b6',
            'sql': '#336791',
            'unknown': '#808080'
        }
        
        node_colors = []
        node_text = []
        hover_text = []
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            lang = node_data.get('language', 'unknown')
            node_colors.append(language_colors.get(lang, '#808080'))
            node_text.append(os.path.basename(node))
            
            # Enhanced hover info
            hover_info = f"File: {node}<br>"
            hover_info += f"Language: {lang}<br>"
            hover_info += f"Lines: {node_data.get('lines', 0)}<br>"
            hover_info += f"Functions: {len(node_data.get('functions', []))}<br>"
            hover_info += f"Classes: {len(node_data.get('classes', []))}<br>"
            hover_info += f"Dependencies: {len(list(self.graph.successors(node)))}"
            hover_text.append(hover_info)
        
        # Node trace
        node_trace = go.Scatter(
            x=[pos[node][0] for node in self.graph.nodes()],
            y=[pos[node][1] for node in self.graph.nodes()],
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            hovertext=hover_text,
            hoverinfo='text',
            marker=dict(
                size=20,
                color=node_colors,
                line=dict(width=2, color='black'),
                colorscale='Viridis'
            )
        )
        
        # Edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in self.graph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            dep_type = edge[2].get('dependency_type', 'unknown')
            edge_info.append(f"{edge[0]} -> {edge[1]} ({dep_type})")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='rgba(125,125,125,0.5)'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create figure with enhanced layout
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Enhanced Codebase Dependency Graph',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[
                    dict(
                        text="Interactive dependency visualization - hover for details",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="#888", size=12)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )
        
        # Save as HTML
        graph_path = f"{output_path}/dependency_graph.html"
        pyo.plot(fig, filename=graph_path, auto_open=False)
        return graph_path
    
    def get_graph_statistics(self) -> Dict:
        """Get statistics about the dependency graph."""
        if not self.graph.nodes():
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'density': 0,
                'is_connected': False,
                'strongly_connected_components': 0,
                'average_degree': 0
            }
        
        try:
            # Calculate basic metrics
            num_nodes = self.graph.number_of_nodes()
            num_edges = self.graph.number_of_edges()
            
            # Calculate density (0 to 1, where 1 means all nodes are connected to all other nodes)
            density = nx.density(self.graph) if num_nodes > 1 else 0
            
            # Check connectivity (for directed graph, use weakly connected)
            is_connected = nx.is_weakly_connected(self.graph) if num_nodes > 1 else True
            
            # Count strongly connected components
            strongly_connected_components = nx.number_strongly_connected_components(self.graph)
            
            # Calculate average degree
            if num_nodes > 0:
                total_degree = sum(dict(self.graph.degree()).values())
                average_degree = total_degree / num_nodes
            else:
                average_degree = 0
            
            # Additional useful metrics
            in_degree_centrality = nx.in_degree_centrality(self.graph) if num_nodes > 0 else {}
            out_degree_centrality = nx.out_degree_centrality(self.graph) if num_nodes > 0 else {}
            
            # Find nodes with highest dependencies (most imported)
            most_dependent_files = []
            if in_degree_centrality:
                sorted_in_degree = sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)
                most_dependent_files = [file for file, centrality in sorted_in_degree[:5] if centrality > 0]
            
            # Find nodes that are most depended upon (most imported by others)
            most_depended_upon_files = []
            if out_degree_centrality:
                sorted_out_degree = sorted(out_degree_centrality.items(), key=lambda x: x[1], reverse=True)
                most_depended_upon_files = [file for file, centrality in sorted_out_degree[:5] if centrality > 0]
            
            return {
                'total_nodes': num_nodes,
                'total_edges': num_edges,
                'density': round(density, 4),
                'is_connected': is_connected,
                'strongly_connected_components': strongly_connected_components,
                'average_degree': round(average_degree, 2),
                'most_dependent_files': most_dependent_files,
                'most_depended_upon_files': most_depended_upon_files,
                'graph_complexity': 'High' if density > 0.5 else 'Medium' if density > 0.2 else 'Low'
            }
            
        except Exception as e:
            print(f"Warning: Error calculating graph statistics: {e}")
            return {
                'total_nodes': self.graph.number_of_nodes(),
                'total_edges': self.graph.number_of_edges(),
                'density': 0,
                'is_connected': False,
                'strongly_connected_components': 0,
                'average_degree': 0,
                'error': str(e)
            }