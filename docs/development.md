# Development

This page provides information for developers who want to contribute to AtPack Parser.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- A text editor or IDE

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/s-celles/atpack-python-parser.git
cd atpack-python-parser

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Development Dependencies

The development setup includes:

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **ruff** - Fast linting
- **mypy** - Type checking

## Project Structure

```
atpack-python-parser/
├── src/
│   └── atpack_parser/
│       ├── __init__.py          # Package initialization
│       ├── parser.py            # Main parser class
│       ├── atdf_parser.py       # ATMEL format parser
│       ├── pic_parser.py        # Microchip PIC parser
│       ├── pdsc_parser.py       # Pack description parser
│       ├── models.py            # Data models
│       ├── exceptions.py        # Custom exceptions
│       ├── xml_utils.py         # XML utilities
│       └── cli.py               # Command line interface
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Test configuration
│   ├── test_parser.py           # Parser tests
│   ├── test_enhanced_atmel.py   # ATMEL parser tests
│   └── test_enhanced_pic.py     # PIC parser tests
├── docs/                        # Documentation
├── examples/                    # Usage examples
├── atpacks/                     # Test AtPack files
├── pyproject.toml               # Project configuration
└── README.md                    # Project README
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=atpack_parser --cov-report=html
```

### Run Specific Tests

```bash
# Test specific file
pytest tests/test_parser.py

# Test specific function
pytest tests/test_parser.py::test_parse_device_info

# Test with verbose output
pytest -v
```

## Code Quality

### Formatting

Format code with Black:

```bash
black src/ tests/ examples/
```

### Linting

Lint code with Ruff:

```bash
ruff check src/ tests/ examples/
```

### Type Checking

Check types with MyPy:

```bash
mypy src/atpack_parser/
```

### Pre-commit Hooks

Install pre-commit hooks to run checks automatically:

```bash
pip install pre-commit
pre-commit install
```

## Documentation

### Building Documentation

The documentation is built with MkDocs:

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Writing Documentation

- Documentation files are in `docs/`
- Use Markdown format
- Include code examples
- Document all public APIs
- Keep examples up to date

## Contributing Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use Black for formatting
- Write clear, descriptive docstrings
- Add type hints to all functions
- Keep functions focused and small

### Adding New Features

1. **Create an issue** describing the feature
2. **Fork the repository** and create a feature branch
3. **Write tests** for your feature first (TDD)
4. **Implement the feature**
5. **Update documentation**
6. **Submit a pull request**

### Example: Adding a New Parser

```python
# src/atpack_parser/new_format_parser.py
from typing import List, Dict, Any
from .models import Device
from .exceptions import AtPackParseError

class NewFormatParser:
    """Parser for new AtPack format."""
    
    def __init__(self, file_content: bytes):
        self.content = file_content
    
    def parse_devices(self) -> List[Device]:
        """Parse devices from the new format."""
        try:
            # Implementation here
            pass
        except Exception as e:
            raise AtPackParseError(f"Failed to parse new format: {e}")
```

### Testing New Features

```python
# tests/test_new_format_parser.py
import pytest
from atpack_parser.new_format_parser import NewFormatParser
from atpack_parser.exceptions import AtPackParseError

def test_parse_devices():
    """Test parsing devices from new format."""
    # Test data
    test_content = b"..."
    
    # Test
    parser = NewFormatParser(test_content)
    devices = parser.parse_devices()
    
    # Assertions
    assert len(devices) > 0
    assert devices[0].name == "ExpectedDevice"

def test_parse_invalid_content():
    """Test error handling for invalid content."""
    with pytest.raises(AtPackParseError):
        parser = NewFormatParser(b"invalid")
        parser.parse_devices()
```

## Debugging

### Debug Mode

Enable debug mode for verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from atpack_parser import AtPackParser
parser = AtPackParser("test.atpack")
```

### Common Issues

#### XML Parsing Errors

```python
# Check XML structure
from lxml import etree
try:
    tree = etree.parse("test.atpack")
except etree.XMLSyntaxError as e:
    print(f"XML parsing error: {e}")
```

#### Memory Issues with Large Files

```python
# Use streaming for large files
def parse_large_atpack(file_path):
    with open(file_path, 'rb') as f:
        # Process in chunks
        chunk_size = 1024 * 1024  # 1MB chunks
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            # Process chunk
```

## Release Process

### Version Bumping

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`

### Publishing to PyPI

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

def profile_parser():
    pr = cProfile.Profile()
    pr.enable()
    
    # Your code here
    from atpack_parser import AtPackParser
    parser = AtPackParser("large.atpack")
    devices = parser.get_devices()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

profile_parser()
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run with memory profiling
python -m memory_profiler example_script.py
```

## Architecture Notes

### Parser Design

The parser uses a modular design:

- **AtPackParser** - Main interface, delegates to format-specific parsers
- **ATDFParser** - Handles ATMEL Device Files
- **PICParser** - Handles Microchip PIC format
- **Models** - Pydantic models for data validation
- **XML Utils** - Common XML processing functions

### Data Flow

```
AtPack File → Unzip → XML Files → Format Parser → Models → API
```

### Extension Points

To add support for new formats:

1. Create a new parser class
2. Implement required methods
3. Register in main parser
4. Add tests and documentation

## Troubleshooting Development

### Import Errors

```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Test Failures

```bash
# Run tests with verbose output
pytest -vv

# Debug specific test
pytest --pdb tests/test_parser.py::test_specific_function
```

### Documentation Issues

```bash
# Check for broken links
mkdocs serve --strict

# Rebuild API docs
rm -rf docs/api/
mkdocs build
```

## Getting Help

- Create an issue on GitHub
- Join discussions in the repository
- Check existing issues and pull requests
- Review the documentation

## Error Handling Architecture

The AtPack Parser implements a DRY (Don't Repeat Yourself) error handling system with intelligent device name suggestions.

### Core Components

#### Central Error Handlers (`src/atpack_parser/cli/common.py`)

```python
def handle_device_not_found_error(e: DeviceNotFoundError, parser=None, no_color: bool = False):
    """Centralized handling of device not found errors with fuzzy suggestions."""
    
def handle_atpack_error(e: AtPackError, no_color: bool = False):
    """Centralized handling of general AtPack errors."""
```

#### Fuzzy Matching Engine

The suggestion system uses **rapidfuzz** (MIT licensed) with multiple algorithms:

- **Exact matching**: Case-insensitive perfect matches get priority 0
- **Ratio scoring**: Character-by-character similarity
- **Partial ratio**: Handles substring matches
- **Token sort**: Handles reordered tokens  
- **Token set**: Handles partial token matches
- **Weighted combination**: Optimized scoring for device names

### Implementation Details

#### Multi-Algorithm Scoring

```python
def _get_device_suggestions(target_device: str, parser, max_suggestions: int = 5):
    # 1. Exact case-insensitive match gets highest priority
    if target_upper == device_upper:
        final_score = 0  # Perfect match
    else:
        # 2. Multiple fuzzy algorithms
        ratio_score = fuzz.ratio(target_upper, device_upper)
        partial_ratio_score = fuzz.partial_ratio(target_upper, device_upper)
        token_sort_ratio_score = fuzz.token_sort_ratio(target_upper, device_upper)
        token_set_ratio_score = fuzz.token_set_ratio(target_upper, device_upper)
        
        # 3. Weighted combination (optimized for device names)
        combined_score = (
            ratio_score * 0.4 +           # Character similarity
            partial_ratio_score * 0.3 +   # Substring matches
            token_sort_ratio_score * 0.2 + # Reordered tokens  
            token_set_ratio_score * 0.1    # Partial tokens
        )
```

#### DRY Pattern Usage

All CLI commands use the centralized error handlers:

```python
# Before (repetitive code in each command)
try:
    device = parser.get_device(device_name)
except DeviceNotFoundError as e:
    console.print(f"[red]Device not found: {e}[/red]")
    raise typer.Exit(1)

# After (DRY pattern)
try:
    device = parser.get_device(device_name)  
except DeviceNotFoundError as e:
    handle_device_not_found_error(e, parser, no_color)
```

### Performance Characteristics

- **Scalability**: Optimized for 1000+ device lists
- **Memory efficiency**: Processes device lists on-demand
- **Speed**: Sub-second suggestion generation for typical AtPack files
- **Fallback safety**: Graceful handling when suggestions can't be generated

### Testing the Error Handling

#### Unit Testing

```python
def test_fuzzy_device_suggestions():
    """Test that device suggestions are properly ranked."""
    suggestions = _get_device_suggestions("PIC16f877", parser)
    assert suggestions[0] == "PIC16F877"  # Exact match first
    assert "PIC16F877A" in suggestions    # Similar devices included
```

#### Integration Testing

```bash
# Test actual CLI behavior
atpack memory show PIC16f877 test.atpack  # Should suggest PIC16F877
atpack devices info atmega16 test.atpack  # Should suggest ATmega16
```

### Extending the Error Handling

#### Adding New Error Types

1. Define the error handler in `common.py`:
```python
def handle_new_error(e: NewErrorType, context=None, no_color: bool = False):
    # Implementation
    pass
```

2. Use it consistently across CLI commands:
```python
try:
    # Operation
except NewErrorType as e:
    handle_new_error(e, context, no_color)
```

#### Customizing Suggestion Algorithms

The fuzzy matching weights can be tuned for specific use cases:

```python
# Device name focused (current)
combined_score = (
    ratio_score * 0.4 +           # High weight on character similarity
    partial_ratio_score * 0.3 +   
    token_sort_ratio_score * 0.2 + 
    token_set_ratio_score * 0.1    
)

# Register name focused (hypothetical)
combined_score = (
    ratio_score * 0.3 +           
    partial_ratio_score * 0.4 +   # Higher weight on substrings
    token_sort_ratio_score * 0.2 + 
    token_set_ratio_score * 0.1    
)
```

### Dependencies

- **rapidfuzz>=3.0.0**: MIT licensed fuzzy string matching
- **rich**: Terminal formatting and colors
- **typer**: CLI framework integration

The system has **no GPL dependencies** and uses only MIT-compatible libraries.

## Contributing Checklist

Before submitting a pull request:

- [ ] Tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Tests are added for new features
- [ ] All public functions have docstrings
