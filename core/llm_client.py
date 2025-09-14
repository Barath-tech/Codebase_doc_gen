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
        """Generate structured documentation sections."""
        return {
            'overview': self._generate_overview(metadata),
            'architecture': self._generate_architecture(metadata, graph_stats),
            'database': self._generate_database_docs(metadata),
            'classes': self._generate_class_docs(metadata),
            'web': self._generate_web_docs(metadata)
        }
    
    def _generate_overview(self, metadata: Dict) -> str:
        """Generate overview documentation."""
        prompt = f"""
        {DOC_PROMPT}
        
        Generate a comprehensive OVERVIEW section for this project:
        
        Project Statistics:
        - Total Files: {metadata['total_files']}
        - Total Lines: {metadata['total_lines']}
        - Languages: {list(metadata['language_stats'].keys())}
        
        Language Distribution:
        {json.dumps(metadata['language_stats'], indent=2)}
        
        Project Structure:
        - Web Files: {len(metadata.get('project_structure', {}).get('web_files', []))}
        - Backend Files: {len(metadata.get('project_structure', {}).get('backend_files', []))}
        - Database Files: {len(metadata.get('project_structure', {}).get('database_files', []))}
        - Config Files: {len(metadata.get('project_structure', {}).get('config_files', []))}
        - Test Files: {len(metadata.get('project_structure', {}).get('test_files', []))}
        - Documentation Files: {len(metadata.get('project_structure', {}).get('documentation_files', []))}
        
        Create a detailed overview that includes:
        1. Project purpose and domain (what this application does)
        2. Technology stack explanation (languages, frameworks, tools used)
        3. Tools and frameworks identified in the codebase
        4. Project layout and organization (how files and folders are structured)
        5. How different components work together (system integration)
        6. Development approach and methodology evident from structure
        7. Links and navigation to other documentation sections
        
        Write in a way that both developers and non-technical stakeholders can understand.
        Provide detailed explanations with examples where applicable, not just one-liner descriptions.
        """
        
        return self._call_llm(prompt)
    
    def _generate_architecture(self, metadata: Dict, graph_stats: Dict) -> str:
        """Generate architecture documentation."""
        
        # Extract architectural insights from file structure
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        backend_files = metadata.get('project_structure', {}).get('backend_files', [])
        db_files = metadata.get('project_structure', {}).get('database_files', [])
        config_files = metadata.get('project_structure', {}).get('config_files', [])
        
        # Analyze JSP and web structure
        jsp_files = [f for f in web_files if f['language'] == 'jsp']
        java_files = [f for f in backend_files if f['language'] == 'java']
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate a comprehensive ARCHITECTURE section for this project:
        
        System Statistics:
        - Total Modules: {graph_stats.get('total_nodes', 0)}
        - Dependencies: {graph_stats.get('total_edges', 0)}
        - Graph Density: {graph_stats.get('density', 0):.3f}
        - Is Connected: {graph_stats.get('is_connected', False)}
        
        Component Analysis:
        - Web Components: {len(web_files)} files (JSP: {len(jsp_files)}, HTML/CSS/JS: {len(web_files) - len(jsp_files)})
        - Backend Components: {len(backend_files)} files (Java: {len(java_files)})
        - Database Components: {len(db_files)} files
        - Configuration Files: {len(config_files)} files
        
        Key Files Identified:
        Top Web Files: {[f['path'] for f in sorted(web_files, key=lambda x: x.get('lines', 0), reverse=True)][:5]}
        Top Backend Files: {[f['path'] for f in sorted(backend_files, key=lambda x: x.get('lines', 0), reverse=True)][:5]}
        
        Create detailed architecture documentation that includes:
        1. **System Architecture Overview**: What type of application this is (web app, enterprise system, etc.)
        2. **Architectural Patterns**: MVC, layered architecture, or other patterns identified
        3. **Component Relationships**: How web, business, and data layers interact
        4. **Technology Layers**: 
           - Presentation layer (JSP, HTML, CSS, JavaScript)
           - Business logic layer (Java classes, services)
           - Data access layer (database connections, DAOs)
        5. **Data Flow**: How information flows through the system
        6. **Integration Points**: APIs, databases, external services
        7. **Deployment Architecture**: How components are organized for deployment
        8. **Flow Diagrams** (textual description): Step-by-step process flows
        9. **Scalability Considerations**: How the architecture supports growth
        10. **Security Architecture**: Authentication, authorization patterns
        
        Explain technical concepts in plain English for non-technical readers while maintaining depth for developers.
        Provide specific examples from the codebase structure where possible.
        """
        
        return self._call_llm(prompt)
    
    def _generate_database_docs(self, metadata: Dict) -> str:
        """Generate database documentation."""
        db_files = metadata.get('project_structure', {}).get('database_files', [])
        
        # Extract database information from parsed files
        tables = []
        procedures = []
        views = []
        references = []
        
        for file_data in db_files:
            tables.extend(file_data.get('tables', []))
            procedures.extend(file_data.get('procedures', []))
            # Extract foreign key references
            for dep in file_data.get('dependencies', []):
                if dep['type'] == 'table_reference':
                    references.append(dep['name'])
        
        # Analyze Java files for database patterns (DAO, Entity classes)
        backend_files = metadata.get('project_structure', {}).get('backend_files', [])
        dao_classes = []
        entity_classes = []
        
        for file_data in backend_files:
            if file_data['language'] == 'java':
                for cls in file_data.get('classes', []):
                    class_name = cls['name'].lower()
                    if 'dao' in class_name or 'repository' in class_name:
                        dao_classes.append(cls['name'])
                    elif 'entity' in class_name or 'model' in class_name:
                        entity_classes.append(cls['name'])
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive DATABASE documentation for this project:
        
        Database Files Analysis:
        - SQL Files Found: {len(db_files)}
        - Tables Identified: {[t['name'] for t in tables[:10]]} {'...' if len(tables) > 10 else ''}
        - Stored Procedures: {[p['name'] for p in procedures[:10]]} {'...' if len(procedures) > 10 else ''}
        - Foreign Key References: {list(set(references))[:10]} {'...' if len(set(references)) > 10 else ''}
        
        Database Integration Patterns:
        - DAO Classes Found: {dao_classes[:10]} {'...' if len(dao_classes) > 10 else ''}
        - Entity/Model Classes: {entity_classes[:10]} {'...' if len(entity_classes) > 10 else ''}
        
        SQL Files Details:
        {json.dumps([{
            'path': f['path'], 
            'lines': f['lines'],
            'tables': len(f.get('tables', [])),
            'procedures': len(f.get('procedures', []))
        } for f in db_files[:10]], indent=2)}
        
        Create detailed database documentation that includes:
        1. **Database System Overview**: What database systems are supported (MySQL, PostgreSQL, Oracle, etc.)
        2. **Database Schema Architecture**: Overall database design approach
        3. **Entity Relationship Diagram (ERD)** (textual description): 
           - Main entities and their relationships
           - Primary and foreign key relationships
           - Cardinality between tables
        4. **Table Descriptions**: Purpose and structure of each major table
        5. **Stored Procedures and Functions**: Business logic implemented in database
        6. **Data Access Patterns**: How the application connects to and uses the database
        7. **Database Integration**: Connection pooling, transaction management
        8. **Data Flow**: How data moves through the database layers
        9. **Performance Considerations**: Indexing, optimization strategies
        10. **Database Setup and Configuration**: Installation and setup requirements
        11. **Data Integrity**: Constraints, triggers, validation rules
        
        Provide both technical details for developers and conceptual explanations for non-technical users.
        Include specific examples from the identified tables and procedures.
        """
        
        return self._call_llm(prompt)
    
    def _generate_class_docs(self, metadata: Dict) -> str:
        """Generate class documentation."""
        
        # Collect comprehensive class information
        all_classes = []
        all_functions = []
        classes_by_file = {}
        
        for file_data in metadata['files']:
            if file_data.get('classes'):
                classes_by_file[file_data['path']] = file_data['classes']
                for cls in file_data['classes']:
                    cls_info = cls.copy()
                    cls_info['file'] = file_data['path']
                    cls_info['language'] = file_data['language']
                    all_classes.append(cls_info)
            
            all_functions.extend(file_data.get('functions', []))
        
        # Group by language and analyze patterns
        classes_by_lang = {}
        design_patterns = {
            'dao': [], 'service': [], 'controller': [], 'model': [], 'entity': [],
            'factory': [], 'singleton': [], 'builder': [], 'adapter': []
        }
        
        for cls in all_classes:
            lang = cls['language']
            if lang not in classes_by_lang:
                classes_by_lang[lang] = []
            classes_by_lang[lang].append(cls)
            
            # Detect design patterns from class names
            class_name_lower = cls['name'].lower()
            for pattern in design_patterns:
                if pattern in class_name_lower:
                    design_patterns[pattern].append(cls['name'])
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive CLASS documentation for this project:
        
        Object-Oriented Analysis:
        - Total Classes Found: {len(all_classes)}
        - Total Functions/Methods: {len(all_functions)}
        - Languages with Classes: {list(classes_by_lang.keys())}
        
        Classes by Language:
        {json.dumps({lang: [cls['name'] for cls in classes] for lang, classes in classes_by_lang.items()}, indent=2)}
        
        Design Patterns Detected:
        {json.dumps({pattern: classes for pattern, classes in design_patterns.items() if classes}, indent=2)}
        
        Key Classes (with methods):
        {json.dumps([{
            'name': cls['name'],
            'file': cls['file'],
            'methods': cls.get('methods', []),
            'docstring': cls.get('docstring', '')[:100] + '...' if cls.get('docstring', '') else 'No documentation'
        } for cls in all_classes[:15]], indent=2)}
        
        Create detailed class documentation that includes:
        1. **Object-Oriented Design Overview**: How OOP principles are applied in this project
        2. **Class Hierarchy and Relationships**: Inheritance trees and composition patterns
        3. **UML Diagram Explanation** (textual representation):
           - Class relationships (inheritance, composition, aggregation)
           - Method signatures and responsibilities
           - Dependencies between classes
        4. **Key Classes and Their Responsibilities**:
           - Core business classes
           - Data access objects (DAOs)
           - Service/Controller classes
           - Model/Entity classes
        5. **Design Patterns Used**:
           - Factory, Singleton, Observer, MVC patterns
           - How patterns are implemented
        6. **Method Analysis**: Key methods and their purposes
        7. **Inheritance and Composition**: How classes relate to each other
        8. **Interface Design**: Abstraction and contract definitions
        9. **Package Organization**: How classes are organized into packages/modules
        10. **Plain English Explanation**: Object-oriented concepts explained simply
        11. **Code Examples**: Illustrative examples of class usage patterns
        
        Make complex OOP concepts understandable for both technical and non-technical audiences.
        Provide specific examples from the identified classes and their actual methods.
        """
        
        return self._call_llm(prompt)
    
    def _generate_web_docs(self, metadata: Dict) -> str:
        """Generate web documentation with enhanced JSP support."""
        web_files = metadata.get('project_structure', {}).get('web_files', [])
        
        # Categorize web files
        jsp_files = [f for f in web_files if f['language'] == 'jsp']
        html_files = [f for f in web_files if f['language'] == 'html']
        css_files = [f for f in web_files if f['language'] == 'css']
        js_files = [f for f in web_files if f['language'] in ['javascript', 'typescript']]
        
        # Analyze JSP navigation and structure
        jsp_includes = []
        jsp_forwards = []
        jsp_tags = []
        java_integration = []
        
        for jsp_file in jsp_files:
            jsp_includes.extend(jsp_file.get('jsp_includes', []))
            java_integration.extend(jsp_file.get('java_imports', []))
            jsp_tags.extend(jsp_file.get('jsp_tags', []))
            
            # Extract forwards from dependencies
            for dep in jsp_file.get('dependencies', []):
                if dep['type'] == 'jsp_forward':
                    jsp_forwards.append({'from': jsp_file['path'], 'to': dep['name']})
                elif dep['type'] == 'jsp_include':
                    jsp_includes.append({'parent': jsp_file['path'], 'include': dep['name']})
        
        # Analyze backend integration (look for servlet-like patterns)
        backend_files = metadata.get('project_structure', {}).get('backend_files', [])
        servlet_classes = []
        controller_classes = []
        
        for file_data in backend_files:
            if file_data['language'] == 'java':
                for cls in file_data.get('classes', []):
                    class_name = cls['name'].lower()
                    if 'servlet' in class_name:
                        servlet_classes.append(cls['name'])
                    elif 'controller' in class_name:
                        controller_classes.append(cls['name'])
        
        prompt = f"""
        {DOC_PROMPT}
        
        Generate comprehensive WEB documentation for this project:
        
        Web Technology Stack:
        - JSP Files: {len(jsp_files)}
        - HTML Files: {len(html_files)}
        - CSS Files: {len(css_files)}
        - JavaScript Files: {len(js_files)}
        
        JSP Application Analysis:
        - JSP Pages: {[f['path'] for f in jsp_files[:10]]} {'...' if len(jsp_files) > 10 else ''}
        - Common Includes: {list(set([inc.get('include', inc) for inc in jsp_includes[:10]]))} {'...' if len(jsp_includes) > 10 else ''}
        - Page Forwards: {[fwd['to'] for fwd in jsp_forwards[:10]]} {'...' if len(jsp_forwards) > 10 else ''}
        - JSP Custom Tags: {list(set(jsp_tags))[:10]} {'...' if len(jsp_tags) > 10 else ''}
        
        Backend Integration:
        - Servlet Classes: {servlet_classes[:10]} {'...' if len(servlet_classes) > 10 else ''}
        - Controller Classes: {controller_classes[:10]} {'...' if len(controller_classes) > 10 else ''}
        - Java Integration: {list(set(java_integration))[:10]} {'...' if len(java_integration) > 10 else ''}
        
        Web File Structure:
        {json.dumps([{
            'path': f['path'], 
            'language': f['language'], 
            'lines': f['lines'],
            'includes': len(f.get('jsp_includes', [])) if f['language'] == 'jsp' else 0
        } for f in web_files[:15]], indent=2)}
        
        Create detailed web documentation that includes:
        1. **Web Application Structure**: Overall web architecture (JSP-based web application)
        2. **User Interface Components**:
           - JSP pages and their purposes
           - HTML templates and layouts
           - CSS styling and themes
           - JavaScript functionality
        3. **Navigation Flow and Routing**:
           - Page-to-page navigation
           - JSP forwards and includes
           - URL mapping and routing patterns
        4. **JSP Application Patterns**:
           - Model-View-Controller implementation
           - JSP tag libraries and custom tags
           - JavaBean integration
           - Session management
        5. **REST API Endpoints** (if identified):
           - Servlet mappings
           - Request/Response patterns
           - API documentation
        6. **Frontend-Backend Integration**:
           - How JSP pages connect to Java backend
           - Data binding and form handling
           - Ajax and dynamic content
        7. **User Experience Flow**:
           - User journey through the application
           - Form workflows
           - Error handling and validation
        8. **Security and Session Management**:
           - Authentication patterns
           - Session handling
           - Input validation
        9. **Performance Considerations**:
           - Caching strategies
           - Static resource management
           - Optimization techniques
        10. **Deployment and Configuration**:
            - Web server requirements
            - Deployment descriptor (web.xml) patterns
            - Configuration management
        
        Explain web concepts clearly for both developers and business stakeholders.
        Provide specific examples from the JSP pages and navigation flows identified.
        Include both technical implementation details and user-facing functionality descriptions.
        """
        
        return self._call_llm(prompt)
    
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