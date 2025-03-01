from setuptools import setup, find_packages

setup(
    name="aipitboss",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",  # Common for API communication
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "flake8>=3.8.0",
            "black>=20.8b1",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.5.0",
        ],
    },
    author="Avi Salmon",
    author_email="avi.salmon@gmail.com",
    description="A simplified AI package with a unified interface for various AI services",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/avisalmon/aipitboss",
    project_urls={
        "Bug Tracker": "https://github.com/avisalmon/aipitboss/issues",
        "Documentation": "https://github.com/avisalmon/aipitboss",
        "Source Code": "https://github.com/avisalmon/aipitboss",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
    include_package_data=True,  # Include files from MANIFEST.in
) 