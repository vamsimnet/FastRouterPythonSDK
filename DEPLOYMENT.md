# FastRouter Python SDK - Deployment Guide

This guide explains how to package and distribute the FastRouter Python SDK.

## Development Setup

1. **Clone/Setup the repository:**
   ```bash
   cd /path/to/fastrouter-python
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install build twine  # For packaging and uploading
   ```

4. **Install in development mode:**
   ```bash
   pip install -e .
   ```

## Testing

1. **Run unit tests:**
   ```bash
   python test_fastrouter.py
   ```

2. **Run examples:**
   ```bash
   export FASTROUTER_API_KEY="sk-v1-your-api-key-here"
   python examples.py
   ```

## Building the Package

1. **Build the distribution:**
   ```bash
   python -m build
   ```

   This creates:
   - `dist/fastrouter-0.1.0.tar.gz` (source distribution)
   - `dist/fastrouter-0.1.0-py3-none-any.whl` (wheel distribution)

2. **Check the build:**
   ```bash
   twine check dist/*
   ```

## Publishing to PyPI

### Test PyPI (Recommended first)

1. **Upload to Test PyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Test installation from Test PyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ fastrouter
   ```

### Production PyPI

1. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

2. **Test installation:**
   ```bash
   pip install fastrouter
   ```

## Version Management

To release a new version:

1. **Update version in:**
   - `fastrouter/__init__.py`
   - `setup.py`
   - `pyproject.toml`

2. **Build and upload:**
   ```bash
   python -m build
   twine upload dist/*
   ```

## Directory Structure

```
fastrouter-python/
├── fastrouter/               # Main package
│   ├── __init__.py          # Package initialization
│   ├── client.py            # Main FastRouter client
│   ├── chat.py              # Chat completions API
│   └── exceptions.py        # Custom exceptions
├── dist/                    # Built distributions (created by build)
├── examples.py              # Usage examples
├── test_fastrouter.py       # Unit tests
├── setup.py                 # Setup configuration (legacy)
├── pyproject.toml           # Modern Python packaging config
├── requirements.txt         # Dependencies
├── README.md                # Documentation
├── MANIFEST.in              # Files to include in distribution
└── DEPLOYMENT.md            # This file
```

## Environment Variables

- `FASTROUTER_API_KEY`: Your FastRouter API key

## PyPI Credentials

Store your PyPI credentials in `~/.pypirc`:

```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## Continuous Integration

For automated testing and deployment, consider setting up GitHub Actions or similar CI/CD pipeline with:

1. **Automated testing** on multiple Python versions
2. **Automated building** on tagged releases  
3. **Automated publishing** to PyPI on version tags

Example workflow triggers:
- Run tests on every pull request
- Build and publish on version tags (e.g., `v0.1.0`)

## Security Considerations

- Never commit API keys to the repository
- Use environment variables for sensitive data
- Consider using PyPI trusted publishing for CI/CD
- Regularly update dependencies for security patches
