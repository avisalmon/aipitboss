from setuptools import setup, find_packages

setup(
    name="aipitboss",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List dependencies here
        "requests>=2.25.0",  # Common for API communication
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "flake8>=3.8.0",
            "black>=20.8b1",
        ],
        "openai": [
            "openai>=1.0.0",  # Optional for additional OpenAI functionality
        ],
        "anthropic": [
            "anthropic>=0.5.0",  # Optional for additional Anthropic functionality
        ],
        "huggingface": [
            "huggingface-hub>=0.16.0",  # Optional for additional HuggingFace functionality
        ],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.5.0",
            "huggingface-hub>=0.16.0",
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI pit boss package with API connectors for various AI services, including OpenAI, Anthropic, and Hugging Face with streaming support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aipitboss",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
) 