# Documentation

This directory contains the MkDocs documentation for AtPack Parser.

## Building Documentation

### Install Dependencies

```bash
pip install -e ".[docs]"
```

### Build Documentation

```bash
mkdocs build
```

### Serve Documentation Locally

```bash
mkdocs serve
```

The documentation will be available at http://127.0.0.1:8000/

## Documentation Structure

- `index.md` - Home page with overview
- `installation.md` - Installation instructions  
- `cli-usage.md` - Command-line interface documentation
- `tui-usage.md` - Terminal user interface documentation
- `api-usage.md` - Python API usage examples
- `examples.md` - Practical examples and code snippets
- `api-reference.md` - Complete API reference
- `development.md` - Development and contribution guide

## Deployment

The documentation is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch. The live documentation is available at:

**https://s-celles.github.io/atpack-python-parser/**

## Configuration

The documentation configuration is in `mkdocs.yml` in the project root. This includes:

- Site metadata
- Navigation structure  
- Theme configuration (Material Design)
- Plugin configuration (search, mkdocstrings)
- Markdown extensions

## Writing Documentation

- Use Markdown format
- Include code examples with syntax highlighting
- Use admonitions for tips, warnings, etc.
- Keep content up to date with code changes
- Test documentation builds locally before committing
