from setuptools import setup, find_packages

setup(
    name="ai-code-docs-agent",
    version="1.0.0",
    description="AI-powered code documentation agent",
    author="AI Code Documentation Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "gitpython>=3.1.40",
        "openai>=1.3.0",
        "markdown>=3.5.1",
        "weasyprint>=61.0",
        "pygments>=2.16.1",
        "networkx>=3.2.1",
        "plotly>=5.17.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'ai-docs=agent:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8+",
    ],
)