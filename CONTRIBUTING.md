# Contributing to AutoScraper

Thank you for considering contributing to AutoScraper! This document outlines the rules and guidelines for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Code Quality Standards](#code-quality-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Git Workflow](#git-workflow)
- [Documentation Standards](#documentation-standards)

## Code of Conduct

- Be respectful and inclusive in all interactions
- Focus on constructive feedback and collaboration
- Help maintain a welcoming environment for all contributors

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/autoscraper.git
   cd autoscraper
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   ```

## Code Quality Standards

### 1. Type Hints (REQUIRED)

All new code MUST include comprehensive type hints:

```python
from typing import List, Dict, Optional, Any

def my_function(param: str, optional_param: Optional[int] = None) -> List[str]:
    """Function with proper type hints."""
    return [param]
```

**Rules:**
- ✅ Add type hints to all function parameters
- ✅ Add return type hints to all functions
- ✅ Use `Optional[T]` for nullable parameters
- ✅ Import types from `typing` module
- ✅ Use `Any` sparingly and document why

### 2. Documentation (REQUIRED)

All functions and classes MUST have Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input is provided
        TypeError: When wrong type is passed

    Examples:
        >>> example_function("test", 42)
        True
    """
    pass
```

**Rules:**
- ✅ Start with a brief one-line description
- ✅ Document all parameters in Args section
- ✅ Document return values in Returns section
- ✅ Document exceptions in Raises section
- ✅ Add usage examples when helpful
- ✅ Keep docstrings up-to-date with code changes

### 3. Code Style (REQUIRED)

Follow PEP 8 and these additional standards:

**Rules:**
- ✅ Use 4 spaces for indentation (no tabs)
- ✅ Maximum line length: 100 characters
- ✅ Use meaningful variable names (no single letters except loop counters)
- ✅ Use snake_case for functions and variables
- ✅ Use PascalCase for class names
- ✅ Use UPPER_CASE for constants
- ✅ Add blank lines between functions and classes
- ✅ Import order: stdlib, third-party, local (with blank lines between)

**Example:**
```python
import json
import sqlite3
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from autoscraper.utils import normalize
```

### 4. Error Handling (REQUIRED)

Always handle errors appropriately:

**Rules:**
- ✅ Use specific exception types (not bare `except:`)
- ✅ Provide descriptive error messages
- ✅ Clean up resources in `finally` blocks or use context managers
- ✅ Re-raise exceptions when you can't handle them
- ✅ Log errors when appropriate

**Example:**
```python
def load_from_file(file_path: str) -> Dict[str, Any]:
    """Load data from file with proper error handling."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
```

## Testing Requirements

### 1. Test Coverage (REQUIRED)

All new features and bug fixes MUST include tests:

**Rules:**
- ✅ Write tests BEFORE or WITH your code (TDD encouraged)
- ✅ Aim for 80%+ code coverage on new code
- ✅ Test both success cases and error cases
- ✅ Test edge cases and boundary conditions
- ✅ All tests must pass before submitting PR

### 2. Test Structure

Organize tests by type:

```
tests/
├── unit/                  # Unit tests for individual functions
│   ├── test_build.py
│   ├── test_utils.py
│   └── test_save_load.py
├── integration/           # Integration tests
│   ├── test_end_to_end.py
│   └── test_real_world.py
└── conftest.py           # Shared fixtures
```

### 3. Test Naming Convention

Use descriptive test names:

```python
def test_build_with_valid_url_returns_results():
    """Test that build() returns results with valid URL."""
    pass

def test_build_with_empty_wanted_list_raises_value_error():
    """Test that build() raises ValueError with empty wanted_list."""
    pass
```

**Rules:**
- ✅ Name format: `test_<what>_<condition>_<expected_result>`
- ✅ Use descriptive names that explain the test
- ✅ Include docstrings for complex tests
- ✅ Group related tests in classes when appropriate

### 4. Test Best Practices

**Rules:**
- ✅ Use pytest fixtures for reusable test components
- ✅ Mock external dependencies (HTTP requests, file I/O)
- ✅ Keep tests independent (no shared state)
- ✅ Use parametrized tests for multiple similar scenarios
- ✅ Assert specific values, not just truthiness
- ✅ Test one thing per test function

**Example:**
```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_html():
    return "<html><body><h1>Test</h1></body></html>"

def test_get_soup_with_html_returns_beautifulsoup(mock_html):
    """Test that _get_soup returns BeautifulSoup object."""
    scraper = AutoScraper()
    soup = scraper._get_soup(html=mock_html)
    assert soup.find('h1').text == 'Test'

@pytest.mark.parametrize("text,expected", [
    ("hello world", "hello world"),
    ("  spaces  ", "spaces"),
    ("", ""),
])
def test_normalize_various_inputs(text, expected):
    """Test normalize function with various inputs."""
    assert normalize(text) == expected
```

## Pull Request Guidelines

### 1. Before Submitting

**Checklist:**
- ✅ All tests pass locally (`pytest tests/`)
- ✅ Code follows style guidelines
- ✅ New code has type hints
- ✅ New code has documentation
- ✅ New features have tests
- ✅ Commit messages are clear and descriptive
- ✅ Branch is up-to-date with master

### 2. PR Description

Your PR description MUST include:

**Required sections:**
```markdown
## Summary
Brief description of changes

## Changes
- Bullet point list of changes made
- Be specific about what was modified

## Testing
- How you tested your changes
- What test cases were added

## Backward Compatibility
- State if this breaks existing functionality
- If yes, explain why and provide migration guide

## Related Issues
- Closes #123
- Fixes #456
```

### 3. PR Size

**Rules:**
- ✅ Keep PRs focused and small (< 500 lines changed when possible)
- ✅ One feature or fix per PR
- ✅ Break large changes into multiple PRs
- ✅ Don't mix refactoring with new features

### 4. Code Review

**Rules:**
- ✅ Address all review comments
- ✅ Be open to feedback and suggestions
- ✅ Explain your decisions if you disagree
- ✅ Update PR based on feedback
- ✅ Mark conversations as resolved when addressed

## Git Workflow

### 1. Branch Naming

Use descriptive branch names:

**Format:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `improvement/description` - Code improvements
- `docs/description` - Documentation updates
- `test/description` - Test additions

**Examples:**
- `feature/sql-database-storage`
- `fix/unicode-handling-bug`
- `improvement/code-quality`
- `docs/api-reference`
- `test/comprehensive-suite`

### 2. Commit Messages

Write clear, descriptive commit messages:

**Format:**
```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what and why, not how.

- Bullet points are fine
- Use present tense ("Add feature" not "Added feature")
- Reference issues with #issue_number

Co-Authored-By: Name <email@example.com>
```

**Rules:**
- ✅ First line: imperative mood ("Add", "Fix", "Update")
- ✅ Keep first line under 50 characters
- ✅ Add blank line before detailed description
- ✅ Explain WHY, not just WHAT
- ✅ Reference related issues

**Good examples:**
```
Add SQL database storage functionality

Implements save_to_db() and load_from_db() methods to store
scraping rules in SQLite database. This enables better integration
with database-backed applications.

- Add save_to_db() method
- Add load_from_db() method
- Maintain backward compatibility with JSON methods

Closes #42
```

### 3. Keeping Your Branch Updated

**Rules:**
- ✅ Regularly sync with master: `git pull origin master`
- ✅ Rebase instead of merge when possible
- ✅ Resolve conflicts promptly
- ✅ Push updated branch: `git push -f origin your-branch` (after rebase)

## Documentation Standards

### 1. README Updates

Update README.md when adding features:

**Rules:**
- ✅ Add usage examples for new features
- ✅ Update installation instructions if needed
- ✅ Keep examples simple and clear
- ✅ Test all code examples before committing

### 2. API Documentation

Document public APIs:

**Rules:**
- ✅ All public methods must have docstrings
- ✅ Include usage examples in docstrings
- ✅ Document parameters, return values, and exceptions
- ✅ Keep documentation up-to-date

## Backward Compatibility

**CRITICAL RULES:**
- ❌ NEVER break existing public APIs without major version bump
- ✅ Deprecate before removing (with warnings)
- ✅ Provide migration guides for breaking changes
- ✅ Maintain compatibility for at least 2 versions before removal
- ✅ Test that existing code still works

## Additional Guidelines

### Performance
- ✅ Profile code before optimizing
- ✅ Don't sacrifice readability for minor performance gains
- ✅ Use appropriate data structures
- ✅ Avoid premature optimization

### Security
- ✅ Validate all user input
- ✅ Never commit secrets or credentials
- ✅ Use parameterized queries for SQL
- ✅ Sanitize HTML content appropriately

### Dependencies
- ✅ Minimize external dependencies
- ✅ Pin dependency versions
- ✅ Justify new dependencies in PR description
- ✅ Keep dependencies up-to-date

## Questions?

If you have questions about contributing:
- Open an issue for discussion
- Check existing issues and PRs
- Reach out to maintainers

## Thank You!

Your contributions make AutoScraper better for everyone. We appreciate your time and effort! 🎉

---

**Remember:** Quality over quantity. Take time to write clean, tested, documented code.
