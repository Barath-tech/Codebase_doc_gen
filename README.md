# AI Code Documentation Agent

An intelligent agent that automatically analyzes codebases and generates comprehensive documentation.

## Features
- Multi-language support (Python, JavaScript, Java, HTML, CSS)
- GitHub repository integration
- Automatic language detection and classification
- Intelligent file filtering (ignores node_modules, __pycache__, etc.)
- Dependency graph generation
- LLM-powered code summarization
- HTML/PDF output formats

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set your OpenAI API key in `.env` file
3. Run: `python agent.py <github_url>`

## Usage
```bash
python agent.py https://github.com/username/repository
```

