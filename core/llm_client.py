import requests
import json
from typing import Dict
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

load_dotenv()

DOC_PROMPT = """
You are an AI Documentation Agent. Your task is to create developer-friendly and non-technical-friendly documentation for the codebase project repository.

The documentation should be structured as follows:
1. Overview - tools used, overall explanation of how this project is laid out, and links to all docs
2. Architecture - System architecture, flow diagrams  
3. Database - Supported DBs, ERD, table descriptions
4. Classes - Classes, UML diagram, plain English explanation
5. Web - REST API endpoints, pages, navigation flow

Ensure readability for both developers and non-technical users. Instead of giving one-liner descriptions, provide detailed explanations with examples where applicable.
"""


class LLMClient:
    def __init__(self, model="meta/Llama-3.3-70B-Instruct"):
        self.client = ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
        )
        self.model = model

    def generate_structured_documentation(self, metadata: Dict, graph_stats: Dict) -> Dict:
        """Generate comprehensive structured documentation sections."""
        return {
            'overview': self._generate_overview(metadata),
            'architecture': self._generate_architecture(metadata, graph_stats),
            'database': self._generate_database_docs(metadata),
            'classes': self._generate_class_docs(metadata),
            'web': self._generate_web_docs(metadata)
        }
    
    def _generate_overview(self, metadata: Dict) -> str:
        """Generate comprehensive overview documentation."""
        
        # Analyze project characteristics
        languages = list(metadata['language_stats'].keys())
        project_structure = metadata.get('project_structure', {})
        
        # Determine project type and tech stack
        project_type = self._determine_project_type(metadata)
        tech_stack = self._analyze_tech_stack(metadata)
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate a comprehensive PROJECT OVERVIEW section for this {project_type} project:
        
        ## Project Analysis:
        - Total Files: {metadata['total_files']}
        - Total Lines: {metadata['total_lines']:,}
        - Languages: {languages}
        - Project Type: {project_type}
        
        ## Language Distribution:
        {json.dumps(metadata['language_stats'], indent=2)}
        
        ## Project Structure Analysis:
        - Web Files: {len(project_structure.get('web_files', []))}
        - Backend Files: {len(project_structure.get('backend_files', []))}
        - Database Files: {len(project_structure.get('database_files', []))}
        - Config Files: {len(project_structure.get('config_files', []))}
        - Test Files: {len(project_structure.get('test_files', []))}
        
        ## Technology Stack Detected:
        {json.dumps(tech_stack, indent=2)}
        
        Create a detailed overview that includes:
        
        ## Purpose
        - What this application does (infer from structure and files)
        - Target audience (developers, end users, businesses)
        - Problem it solves
        - Key business value
        
        ## Target Audience
        ### For [User Type] (Non-Technical Users)
        - Specific user roles and their needs
        - How they interact with the system
        - Benefits for each user type
        
        ### For Developers  
        - Technical audience segments
        - Development team roles
        - Technical benefits and features
        
        ## Key Features
        Based on the codebase structure, identify and list the main features with:
        - Feature descriptions
        - Technical implementation
        - User benefits
        - Use icons/emojis where appropriate
        
        ## Technology Stack
        ### Frontend Technologies
        - Detailed breakdown of frontend tech
        - Versions where detectable
        - Purpose of each technology
        
        ### Backend Technologies  
        - Backend framework analysis
        - Database technologies
        - API frameworks
        
        ### Development Tools
        - Build tools and bundlers
        - Testing frameworks
        - CI/CD tools (if detectable)
        
        ## Project Structure
        Create a detailed directory tree showing:
        ```
        project/
        ├── feature-directories/
        ├── core-directories/
        └── supporting-files/
        ```
        
        ## Getting Started
        Based on the project structure, provide:
        1. Installation steps
        2. Environment setup
        3. Running the application
        4. Key commands
        
        ## Documentation Sections
        - Link to other documentation with descriptions
        - What each section covers
        - Who should read each section
        
        Write in the professional style shown in the examples, with detailed explanations, proper formatting, and both technical depth and business clarity.
        """
        
        return self._call_llm(prompt)
    
    def _generate_architecture(self, metadata: Dict, graph_stats: Dict) -> str:
        """Generate comprehensive architecture documentation with detailed diagrams."""
        
        # Deep analysis of architecture patterns
        arch_patterns = self._analyze_architecture_patterns(metadata)
        component_analysis = self._analyze_component_relationships(metadata)
        data_flow = self._analyze_data_flow_patterns(metadata)
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive SYSTEM ARCHITECTURE documentation for this project:
        
        ## Architectural Analysis:
        {json.dumps(arch_patterns, indent=2)}
        
        ## Component Relationships:
        {json.dumps(component_analysis, indent=2)}
        
        ## Data Flow Patterns:
        {json.dumps(data_flow, indent=2)}
        
        ## System Statistics:
        - Total Modules: {graph_stats.get('total_nodes', 0)}
        - Dependencies: {graph_stats.get('total_edges', 0)}
        - Graph Density: {graph_stats.get('density', 0):.3f}
        - Connectivity: {graph_stats.get('is_connected', False)}
        - Complexity: {graph_stats.get('graph_complexity', 'Unknown')}
        
        Create detailed architecture documentation that includes:
        
        ## High-Level Overview
        - Architectural style and patterns used
        - Key design principles
        - Overall system approach
        
        ## Architecture Diagram
        Create a professional Mermaid diagram showing the high-level architecture:
        ```mermaid
        graph TD
            %% Create a comprehensive architecture diagram
            %% Show all major components and their relationships
            %% Use proper Mermaid syntax for different component types
            %% Include data flow arrows
            %% Group related components
        ```
        
        ## Core Components
        
        ### 1. Presentation Layer
        - Frontend technologies and frameworks
        - UI component structure
        - Client-side state management
        - User interaction patterns
        
        ### 2. Business Logic Layer
        - Application logic organization
        - Service layer architecture
        - Business rules implementation
        - Processing workflows
        
        ### 3. Data Access Layer
        - Database integration patterns
        - Data persistence strategies
        - API design and implementation
        - Caching mechanisms
        
        ### 4. Infrastructure Layer
        - Configuration management
        - Environment handling
        - Build and deployment
        - External integrations
        
        ## Data Flow Architecture
        Create a detailed Mermaid sequence diagram showing data flow:
        ```mermaid
        sequenceDiagram
            %% Show typical user interaction flow
            %% Include all major components
            %% Show data transformation points
            %% Include error handling paths
        ```
        
        ## Component Breakdown
        Detailed analysis of each major component with:
        - Purpose and responsibility
        - Key files and directories
        - Dependencies and relationships
        - Performance considerations
        
        ## Integration Patterns
        - How components communicate
        - API integration strategies
        - Event handling patterns
        - Error propagation
        
        ## Scalability Analysis
        - Current architecture scalability
        - Bottlenecks and limitations
        - Scaling strategies
        - Performance considerations
        
        ## Security Architecture
        - Authentication and authorization
        - Data protection strategies
        - Security boundaries
        - Vulnerability considerations
        
        Use professional formatting, detailed technical analysis, and comprehensive Mermaid diagrams throughout.
        """
        
        return self._call_llm(prompt)
    
    def _generate_database_docs(self, metadata: Dict) -> str:
        """Generate comprehensive database documentation with ERD diagrams."""
        
        db_analysis = self._analyze_database_structure(metadata)
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive DATABASE documentation for this project:
        
        ## Database Analysis:
        {json.dumps(db_analysis, indent=2)}
        
        Create detailed database documentation that includes:
        
        ## Database Platform
        - Database technology used
        - Version and features
        - Key capabilities
        - Integration approach
        
        ## Entity-Relationship Diagram
        Create a comprehensive Mermaid ERD:
        ```mermaid
        erDiagram
            %% Define all entities with their attributes
            %% Show relationships between entities
            %% Include cardinality indicators
            %% Use proper ERD notation
        ```
        
        ## Table Descriptions
        For each identified table:
        
        ### [Table Name]
        Brief description of table purpose
        
        #### Fields
        | Field | Type | Description | Constraints |
        |-------|------|-------------|-------------|
        
        #### Example
        ```sql
        CREATE TABLE example (
            -- Actual SQL based on analysis
        );
        ```
        
        ## Database Relations
        
        ### One-to-Many Relations
        - Detailed relationship descriptions
        - Business logic behind relationships
        - Data integrity considerations
        
        ### Many-to-Many Relations
        - Junction table analysis
        - Complex relationship handling
        - Performance implications
        
        ## Data Access Patterns
        - How the application interacts with data
        - Query patterns and optimization
        - Connection management
        - Transaction handling
        
        ## Database Migrations
        - Schema evolution strategy
        - Migration management
        - Version control integration
        - Rollback procedures
        
        ## Performance Considerations
        - Indexing strategies
        - Query optimization
        - Connection pooling
        - Caching approaches
        
        ## Data Security
        - Access control mechanisms
        - Data encryption
        - Audit trails
        - Backup and recovery
        
        Include real SQL examples where possible and professional database design analysis.
        """
        
        return self._call_llm(prompt)
    
    def _generate_class_docs(self, metadata: Dict) -> str:
        """Generate comprehensive class/component documentation with UML diagrams."""
        
        class_analysis = self._analyze_class_structure(metadata)
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive CLASSES/COMPONENTS documentation for this project:
        
        ## Class Structure Analysis:
        {json.dumps(class_analysis, indent=2)}
        
        Create detailed component documentation that includes:
        
        ## Component Hierarchy
        Create a comprehensive Mermaid diagram showing component relationships:
        ```mermaid
        classDiagram
            %% Define all major classes/components
            %% Show inheritance relationships
            %% Include composition relationships
            %% Show method signatures where relevant
        ```
        
        ## Core Components
        
        ### 1. [Component Category]
        
        #### `ComponentName` Component
        Location: `path/to/component`
        ```mermaid
        classDiagram
            class ComponentName 
                +State property: type
                +Prop property: type
                +Function method()
                +Render() JSX
            
        ```
        **Purpose**: Detailed description of component purpose
        **Key Features**:
        - Feature 1 with explanation
        - Feature 2 with explanation
        - Integration points
        
        ## Custom Hooks (if applicable)
        
        ### [Hook Category]
        
        #### `useHookName` Hook
        Location: `path/to/hook`
        ```javascript
        const useHookName = (parameters) => 
            // Show actual hook implementation structure
            return returnValues ;
        ```
        **Purpose**: Detailed hook explanation
        **Usage**: How and when to use this hook
        **Returns**: What the hook returns and how to use it
        
        ## Utility Functions
        
        ### [Utility Category]
        Location: `path/to/utils`
        ```javascript
        export const utilityFunction = (params) => 
            // Show actual utility structure
        ;
        ```
        
        ## Component Interaction Examples
        
        ### [Workflow Name]
        ```mermaid
        sequenceDiagram
            %% Show how components interact
            %% Include data flow
            %% Show state changes
        ```
        
        ## Design Patterns
        - Pattern identification and explanation
        - Implementation examples
        - Benefits and trade-offs
        - Usage guidelines
        
        ## State Management
        - How state is managed across components
        - State flow patterns
        - Performance implications
        - Best practices
        
        Include real code examples, detailed component analysis, and professional UML/component diagrams.
        """
        
        return self._call_llm(prompt)
    
    def _generate_web_docs(self, metadata: Dict) -> str:
        """Generate comprehensive web interface documentation with flow diagrams."""
        
        web_analysis = self._analyze_web_structure(metadata)
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive WEB INTERFACE documentation for this project:
        
        ## Web Structure Analysis:
        {json.dumps(web_analysis, indent=2)}
        
        Create detailed web documentation that includes:
        
        ## Pages Structure
        
        ### [Page Category]
        
        #### [Page Name] (`/route`)
        - **Component**: `ComponentName.jsx`
        - **Purpose**: Page purpose and functionality
        - **Features**:
          - Feature list with detailed explanations
          - User interactions supported
          - Data displayed and managed
        
        ## API Endpoints
        
        ### [API Category]
        Location: `services/apiFile.js`
        
        #### [Operation Name]
        ```javascript
        [HTTP_METHOD] /api/endpoint
        Body: 
          field: type,
          field: type
        
        Response: 
          responseStructure
        ```
        
        ## Navigation Flow
        
        ### [Flow Name]
        ```mermaid
        graph TD
            %% Create detailed navigation flow
            %% Show user journey paths
            %% Include decision points
            %% Show error handling paths
        ```
        
        ## Protected Routes
        Location: `path/to/protection`
        
        ### Route Protection Logic
        ```javascript
        // Show actual route protection implementation
        ```
        
        ### Protected Routes Configuration
        ```javascript
        // Show routing configuration
        ```
        
        ## User Workflows
        
        ### [Workflow Name]
        ```mermaid
        sequenceDiagram
            %% Show complete user workflow
            %% Include all steps and decision points
            %% Show system responses
        ```
        
        ## Error Handling
        
        ### [Error Category]
        ```javascript
        // Show actual error handling patterns
        ```
        
        ## Response Handling
        - Success response patterns
        - Loading state management
        - Error state handling
        - User feedback mechanisms
        
        ## Performance Optimizations
        - Loading strategies
        - Caching approaches
        - Bundle optimization
        - Runtime performance
        
        ## Security Measures
        - Authentication flows
        - Authorization patterns
        - Input validation
        - XSS protection
        
        Include comprehensive flow diagrams, real code examples, and detailed user experience analysis.
        """
        
        return self._call_llm(prompt)
    
    # Enhanced analysis methods
    
    def _determine_project_type(self, metadata: Dict) -> str:
        """Determine the type of project based on file analysis."""
        languages = metadata['language_stats'].keys()
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        backend_files = metadata.get('project_structure', {}).get('backend_files', [])
        
        if 'javascript' in languages or 'typescript' in languages:
            if any('react' in str(f).lower() for f in web_files):
                return "React Web Application"
            elif any('vue' in str(f).lower() for f in web_files):
                return "Vue.js Web Application" 
            elif any('angular' in str(f).lower() for f in web_files):
                return "Angular Web Application"
            else:
                return "JavaScript Web Application"
        elif 'java' in languages:
            jsp_files = [f for f in web_files if f.get('language') == 'jsp']
            if jsp_files:
                return "Java Web Application (JSP/Servlet)"
            else:
                return "Java Enterprise Application"
        elif 'python' in languages:
            return "Python Web Application"
        else:
            return "Multi-language Application"
    
    def _analyze_tech_stack(self, metadata: Dict) -> Dict:
        """Analyze and categorize the technology stack."""
        tech_stack = {
            'frontend': [],
            'backend': [],
            'database': [],
            'tools': []
        }
        
        languages = metadata['language_stats'].keys()
        
        # Frontend technologies
        if 'javascript' in languages:
            tech_stack['frontend'].append('JavaScript')
        if 'typescript' in languages:
            tech_stack['frontend'].append('TypeScript')
        if 'html' in languages:
            tech_stack['frontend'].append('HTML')
        if 'css' in languages:
            tech_stack['frontend'].append('CSS')
        if 'jsx' in languages:
            tech_stack['frontend'].append('React JSX')
        
        # Backend technologies
        if 'java' in languages:
            tech_stack['backend'].append('Java')
        if 'python' in languages:
            tech_stack['backend'].append('Python')
        if 'jsp' in languages:
            tech_stack['backend'].append('JSP (JavaServer Pages)')
        
        # Database technologies
        if 'sql' in languages:
            tech_stack['database'].append('SQL Database')
        
        # Configuration and tools
        config_files = metadata.get('project_structure', {}).get('config_files', [])
        for config_file in config_files:
            if 'package.json' in config_file.get('path', ''):
                tech_stack['tools'].append('npm/Node.js')
            elif 'pom.xml' in config_file.get('path', ''):
                tech_stack['tools'].append('Maven')
            elif 'build.gradle' in config_file.get('path', ''):
                tech_stack['tools'].append('Gradle')
        
        return tech_stack
    
    def _analyze_architecture_patterns(self, metadata: Dict) -> Dict:
        """Analyze architectural patterns in the codebase."""
        patterns = {
            'architectural_style': 'Unknown',
            'design_patterns': [],
            'component_organization': 'Unknown',
            'state_management': 'Unknown'
        }
        
        # Detect common patterns
        all_files = metadata['files']
        file_paths = [f['path'] for f in all_files]
        
        # Check for MVC pattern
        if any('controller' in path.lower() for path in file_paths):
            patterns['design_patterns'].append('MVC (Model-View-Controller)')
        
        # Check for component-based architecture
        if any('component' in path.lower() for path in file_paths):
            patterns['architectural_style'] = 'Component-based Architecture'
        
        # Check for feature-based organization
        if any('feature' in path.lower() for path in file_paths):
            patterns['component_organization'] = 'Feature-based Organization'
        
        # Check for service layer
        if any('service' in path.lower() for path in file_paths):
            patterns['design_patterns'].append('Service Layer Pattern')
        
        return patterns
    
    def _analyze_component_relationships(self, metadata: Dict) -> Dict:
        """Analyze relationships between components."""
        relationships = {
            'total_components': 0,
            'dependency_depth': 0,
            'coupling_analysis': 'Unknown',
            'cohesion_analysis': 'Unknown'
        }
        
        # Basic relationship analysis based on dependencies
        total_deps = sum(len(f.get('dependencies', [])) for f in metadata['files'])
        total_files = len(metadata['files'])
        
        if total_files > 0:
            relationships['total_components'] = total_files
            avg_deps = total_deps / total_files
            
            if avg_deps > 10:
                relationships['coupling_analysis'] = 'High Coupling'
            elif avg_deps > 5:
                relationships['coupling_analysis'] = 'Medium Coupling'
            else:
                relationships['coupling_analysis'] = 'Low Coupling'
        
        return relationships
    
    def _analyze_data_flow_patterns(self, metadata: Dict) -> Dict:
        """Analyze data flow patterns in the application."""
        data_flow = {
            'pattern_type': 'Unknown',
            'state_management': 'Unknown',
            'data_persistence': 'Unknown',
            'api_integration': 'Unknown'
        }
        
        # Analyze based on file types and patterns
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        db_files = metadata.get('project_structure', {}).get('database_files', [])
        
        if web_files and db_files:
            data_flow['pattern_type'] = 'Full-stack Application'
            data_flow['data_persistence'] = 'Database-backed'
        elif web_files:
            data_flow['pattern_type'] = 'Frontend Application'
            data_flow['api_integration'] = 'External API Integration'
        
        return data_flow
    
    def _analyze_database_structure(self, metadata: Dict) -> Dict:
        """Analyze database structure and relationships."""
        db_analysis = {
            'database_type': 'Unknown',
            'tables_identified': [],
            'relationships': [],
            'patterns': []
        }
        
        db_files = metadata.get('project_structure', {}).get('database_files', [])
        
        for db_file in db_files:
            tables = db_file.get('tables', [])
            db_analysis['tables_identified'].extend([t['name'] for t in tables])
            
            # Analyze for common database patterns
            dependencies = db_file.get('dependencies', [])
            for dep in dependencies:
                if dep['type'] == 'table_reference':
                    db_analysis['relationships'].append({
                        'type': 'Foreign Key Reference',
                        'target': dep['name']
                    })
        
        if db_files:
            db_analysis['database_type'] = 'SQL Database'
            
        return db_analysis
    
    def _analyze_class_structure(self, metadata: Dict) -> Dict:
        """Analyze class/component structure."""
        class_analysis = {
            'total_classes': 0,
            'inheritance_chains': [],
            'design_patterns': [],
            'component_types': {}
        }
        
        all_classes = []
        for file_data in metadata['files']:
            classes = file_data.get('classes', [])
            all_classes.extend(classes)
        
        class_analysis['total_classes'] = len(all_classes)
        
        # Analyze class names for patterns
        for cls in all_classes:
            class_name = cls['name'].lower()
            if 'service' in class_name:
                class_analysis['design_patterns'].append('Service Pattern')
            elif 'factory' in class_name:
                class_analysis['design_patterns'].append('Factory Pattern')
            elif 'dao' in class_name:
                class_analysis['design_patterns'].append('Data Access Object')
        
        return class_analysis
    
    def _analyze_web_structure(self, metadata: Dict) -> Dict:
        """Analyze web structure and patterns."""
        web_analysis = {
            'page_count': 0,
            'api_endpoints': [],
            'routing_pattern': 'Unknown',
            'authentication': 'Unknown'
        }
        
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        web_analysis['page_count'] = len(web_files)
        
        # Check for common web patterns
        all_files = metadata['files']
        for file_data in all_files:
            file_path = file_data['path'].lower()
            if 'route' in file_path or 'router' in file_path:
                web_analysis['routing_pattern'] = 'Client-side Routing'
            if 'auth' in file_path or 'login' in file_path:
                web_analysis['authentication'] = 'Authentication System Present'
        
        return web_analysis
    
    def _call_llm(self, prompt: str) -> str:
        """Make LLM API call with error handling."""
        try:
            response = self.client.complete(
                messages=[
                    SystemMessage("You are a code documentation assistant."),
                    UserMessage(prompt),
                ],
                model=self.model,
                # temperature=temperature,
                # max_tokens=max_tokens,
                top_p=0.9,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    # Legacy methods for backward compatibility (if needed)
    def summarize_file(self, file_metadata: Dict) -> str:
        """Legacy method - generates basic file summary."""
        return f"File: {file_metadata['path']} ({file_metadata['language']}) - {file_metadata['lines']} lines"
    
    def summarize_codebase(self, metadata: Dict) -> str:
        """Legacy method - generates basic codebase summary."""
        return self._generate_overview(metadata)
    
    def generate_architectural_insights(self, metadata: Dict, graph_stats: Dict) -> str:
        """Legacy method - generates architectural insights."""
        return self._generate_architecture(metadata, graph_stats)