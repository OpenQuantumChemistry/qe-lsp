# Development Guide

This guide provides detailed information for developers who want to contribute to QE-LSP.

## Architecture Overview

QE-LSP consists of three main components:

1. **Parser** (`src/qe_lsp/parser.py`)
   - Parses Quantum ESPRESSO input files
   - Tracks positions for LSP features
   - Validates structure and required parameters

2. **Data** (`src/qe_lsp/data.py`)
   - Parameter documentation
   - Valid values and defaults
   - Formatting functions for hover

3. **Server** (`src/qe_lsp/server.py`)
   - LSP protocol implementation
   - Handles editor requests
   - Manages diagnostics

## Parser Architecture

### AST Classes

The parser builds an Abstract Syntax Tree (AST) with these classes:

- `Position` - Line and column (0-indexed)
- `Range` - Start and end positions
- `NamelistParam` - Single parameter with value
- `Namelist` - Collection of parameters
- `Card` - Card with data lines
- `QEInputFile` - Complete parsed file

### Parsing Flow

```
Input String
    ↓
Split into lines
    ↓
Iterate lines
    ↓
Detect namelist start (&name)
    ↓
Parse namelist until /
    ↓
Detect card (UPPERCASE)
    ↓
Parse card until next section
    ↓
Validate required parameters
    ↓
Return QEInputFile
```

## LSP Features Implementation

### Hover

1. Get word at cursor position
2. Check if inside namelist
3. Look up parameter documentation
4. Return markdown-formatted hover

### Completion

Three contexts:

1. **Namelist/Card level** - Suggest namelists and cards
2. **Parameter level** - Suggest parameters for current namelist
3. **Value level** - Suggest valid values for parameter

### Diagnostics

Two types:

1. **Errors** - Invalid syntax, unknown namelists/cards, missing required params
2. **Warnings** - Unknown parameters

### Document Symbols

Returns hierarchical symbols:

```
&control (Namespace)
├── calculation (Property)
├── prefix (Property)
└── ...
ATOMIC_SPECIES (Array)
```

## Testing Strategy

### Test Organization

- `test_parser.py` - Parser unit tests
- `test_data.py` - Data module tests
- `test_server.py` - LSP server tests

### Coverage Requirements

100% code coverage is required. Use `# pragma: no cover` sparingly for:

- `__repr__` methods
- Abstract method stubs
- Unreachable code

### Test Fixtures

Common test data is in `conftest.py`:

- `sample_qe_input` - Full example
- `minimal_qe_input` - Minimal valid input
- `invalid_qe_input` - Contains errors
- `empty_qe_input` - Edge case
- `comment_only_input` - Edge case

### Writing Tests

Follow these patterns:

```python
def test_feature_description(self):
    """Test that feature does X."""
    # Arrange
    input_data = "..."
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected
```

## Adding New Features

### Adding a New LSP Feature

1. Add handler function in `server.py`:

```python
@server.feature(TEXT_DOCUMENT_NEW_FEATURE)
def new_feature(params: NewFeatureParams) -> Result:
    """Handle new feature request."""
    document = server.workspace.get_text_document(params.text_document.uri)
    # ... implementation
    return result
```

2. Add tests in `test_server.py`

3. Update documentation

### Adding New Parameters

1. Edit `src/qe_lsp/data.py`
2. Add to appropriate namelist dictionary
3. Include:
   - `description` - Human-readable description
   - `type` - Parameter type
   - `default` - Default value (if any)
   - `values` - Valid options for enums
   - `required` - Whether parameter is required

4. Add test in `test_data.py`

## Debugging

### Enable Verbose Logging

Set environment variable:

```bash
export PYGLS_DEBUG=1
qe-lsp
```

### Test Against Real Input

Create a test file:

```python
from qe_lsp.parser import QEParser

parser = QEParser()
with open("test.in") as f:
    result = parser.parse(f.read())

for namelist in result.namelists:
    print(f"Namelist: {namelist.name}")
    for param in namelist.params:
        print(f"  {param.name} = {param.value}")
```

## Release Process

1. Update version in `src/qe_lsp/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag
5. Build and publish to PyPI

## Common Issues

### Import Errors

Make sure to install in editable mode:

```bash
pip install -e ".[dev]"
```

### Type Errors

Run mypy to check types:

```bash
mypy src
```

### Test Failures

Run with verbose output:

```bash
pytest -v --tb=short
```

## Code Style

- Line length: 100 characters
- Use black for formatting
- Use isort for import sorting
- Add type hints to all functions
- Write docstrings for all public functions
