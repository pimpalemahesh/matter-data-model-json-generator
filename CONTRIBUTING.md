# Contributing to Matter Data Model JSON Generator

Thank you for your interest in contributing to the Matter Data Model JSON Generator! We welcome contributions from the community and are grateful for your support.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## 🤝 Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior through GitHub issues.

## 🚀 How to Contribute

There are many ways to contribute to this project:

- **Bug Reports**: Report bugs through GitHub Issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve documentation, examples, or tutorials
- **Testing**: Help test new features or find edge cases

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

1. **Fork the repository**

   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone your fork**

   ```bash
   git clone https://github.com/your-username/matter-data-model-json-generator.git
   cd matter-data-model-json-generator
   ```

3. **Set up upstream remote**

   ```bash
   git remote add upstream https://github.com/pimpalemahesh/matter-data-model-json-generator.git
   ```

4. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**

   ```bash
   pip install -e .[dev]
   ```

6. **Verify installation**
   ```bash
   python -m pytest tests/
   ```

## 🔧 Making Changes

### Branch Strategy

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Keep your branch updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Development Workflow

1. **Make your changes**
   - Write clean, well-documented code
   - Follow the coding standards (see below)
   - Add tests for new functionality

2. **Test your changes**

   ```bash
   python -m pytest tests/
   python -m flake8 .
   python -m black --check .
   python -m mypy .
   ```

3. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new XML parsing feature"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `style:` for formatting changes

## 📤 Pull Request Process

1. **Push your branch**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template

3. **PR Requirements**
   - [ ] Clear description of changes
   - [ ] Tests pass
   - [ ] Code follows style guidelines
   - [ ] Documentation updated if needed
   - [ ] No breaking changes (or clearly documented)

4. **Review Process**
   - Maintainers will review your PR
   - Address any requested changes
   - Once approved, your PR will be merged

## 📝 Coding Standards

### Python Style

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Black**: Use Black for code formatting
- **Type Hints**: Add type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Quality

```python
def parse_cluster_file(
    file_path: str,
    yaml_file_path: str,
    base_clusters: Optional[List[Cluster]] = None
) -> List[Cluster]:
    """Parse a cluster XML file and return cluster objects.

    Args:
        file_path: Path to the XML file to parse
        yaml_file_path: Path to the YAML configuration file
        base_clusters: Optional list of base clusters for inheritance

    Returns:
        List of parsed Cluster objects

    Raises:
        FileNotFoundError: If the XML file doesn't exist
        ET.ParseError: If the XML is malformed
    """
    # Implementation here
    pass
```

### File Organization

- Keep files focused and modular
- Use clear, descriptive names
- Group related functionality
- Separate concerns appropriately

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=source_parser --cov=core --cov=utils

# Run specific test file
python -m pytest tests/test_cluster_parser.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies

```python
def test_parse_cluster_file_with_valid_xml():
    """Test that valid XML files are parsed correctly."""
    # Arrange
    test_file = "test_data/valid_cluster.xml"
    parser = ClusterParser()

    # Act
    result = parser.parse_cluster_file(test_file)

    # Assert
    assert len(result) == 1
    assert result[0].name == "OnOff"
    assert result[0].id == "0x0006"
```

## 📚 Documentation

### Code Documentation

- Use clear, concise docstrings
- Document all public functions and classes
- Include examples in docstrings when helpful
- Keep documentation up to date with code changes

### User Documentation

- Update README.md for user-facing changes
- Add examples for new features
- Update API documentation
- Consider adding tutorials for complex features

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, package versions
- **Sample Data**: Minimal XML files that reproduce the issue

### Feature Requests

For feature requests, please include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions you've considered
- **Additional Context**: Any other relevant information

## 📋 Issue Templates

We provide issue templates for:

- Bug reports
- Feature requests
- Documentation improvements
- Performance issues

## 🏷️ Labels

We use labels to categorize issues and PRs:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: High priority items
- `priority-low`: Low priority items

## 🔄 Release Process

1. Version bumping follows semantic versioning
2. Changelog is updated for each release
3. Releases are tagged and published to PyPI
4. GitHub releases include release notes

## 🙋‍♀️ Getting Help

If you need help:

- Check existing issues and documentation
- Join our [Discussions](https://github.com/pimpalemahesh/matter-data-model-json-generator/discussions)
- Create an issue for questions or support

## 🙏 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to the Matter Data Model JSON Generator! 🎉
