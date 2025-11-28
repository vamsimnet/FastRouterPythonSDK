"""Setup configuration for FastRouter Python SDK"""

from setuptools import setup, find_packages

# Read README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "FastRouter Python SDK - A Python client library for the FastRouter API"

# Read requirements
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = ["requests>=2.25.0"]

setup(
    name="fastrouter",
    version="0.1.2",
    author="FastRouter Team",
    author_email="support@fastrouter.ai",
    description="Python client library for the FastRouter API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastrouter/fastrouter-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="fastrouter api client sdk ai llm chat completions",
    project_urls={
        "Bug Reports": "https://github.com/fastrouter/fastrouter-python/issues",
        "Documentation": "https://docs.fastrouter.ai/",
        "Source": "https://github.com/fastrouter/fastrouter-python",
    },
)
