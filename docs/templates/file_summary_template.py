FILE_SUMMARY_TEMPLATE = """
Analyze and summarize this {language} file:

File: {path}
Language: {language}
Lines of code: {lines}

Functions: {functions}
Classes: {classes}
Imports: {imports}

Provide a concise summary covering:
1. File purpose and main functionality
2. Key components (functions/classes) and their roles
3. Dependencies and how it fits in the project
4. Notable patterns, techniques, or design decisions
5. Potential issues or areas for improvement

Keep the summary focused and under 150 words.
"""

CODEBASE_SUMMARY_TEMPLATE = """
Analyze this entire codebase and provide a comprehensive overview:

Project Statistics:
- Total Files: {total_files}
- Total Lines of Code: {total_lines}
- Languages: {languages}

Language Breakdown:
{language_stats}

Main File Types and Their Distribution:
{file_distribution}

Provide a summary covering:
1. Project purpose and domain (web app, library, tool, etc.)
2. Technology stack and architecture pattern
3. Main components and their responsibilities
4. Code organization and structure quality
5. Notable features, patterns, or architectural decisions
6. Potential areas for improvement or refactoring
7. Overall complexity and maintainability assessment

Keep the analysis comprehensive but concise (under 300 words).
"""

ARCHITECTURAL_INSIGHTS_TEMPLATE = """
Based on the codebase analysis, provide architectural insights:

Project Overview:
- Total Files: {total_files}
- Total Lines: {total_lines}
- Languages Used: {languages}

Language Statistics:
{language_stats}

Dependency Graph Metrics:
- Total Modules: {total_nodes}
- Dependencies: {total_edges}
- Graph Density: {density}
- Connectivity: {is_connected}
- Average Connections: {avg_degree}

Analyze and provide insights on:
1. **Architecture Pattern**: What architectural pattern(s) does this codebase follow?
2. **Modularity**: How well is the code organized into modules/components?
3. **Coupling & Cohesion**: Assessment of dependencies and module relationships
4. **Scalability**: How well would this codebase scale with growth?
5. **Maintainability**: Ease of maintenance and modification
6. **Technology Choices**: Assessment of the technology stack
7. **Code Quality Indicators**: Based on structure and organization
8. **Potential Issues**: Areas that might need attention
9. **Recommendations**: Suggestions for improvement

Provide specific, actionable insights based on the data provided.
"""

CODE_QUALITY_TEMPLATE = """
Assess the code quality based on the following metrics:

File Statistics:
{file_stats}

Complexity Indicators:
- Average file size: {avg_file_size} lines
- Largest file: {largest_file} lines
- Files with high complexity: {complex_files}

Dependency Analysis:
- Highly coupled files: {coupled_files}
- Circular dependencies: {circular_deps}

Provide assessment on:
1. Code organization and structure
2. File size distribution and potential issues
3. Dependency management
4. Potential technical debt indicators
5. Maintainability score (1-10)
6. Specific recommendations for improvement
"""
