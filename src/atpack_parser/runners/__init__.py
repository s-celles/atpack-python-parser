"""Standalone runners for different AtPack Parser interfaces.

This package contains entry points for different modes:
- cli: Command Line Interface
- interactive: Interactive shell mode
- tui: Terminal User Interface

Use them directly via:
  python -m src.atpack_parser.runners.cli
  python -m src.atpack_parser.runners.interactive
  python -m src.atpack_parser.runners.tui
"""

# Don't import modules at package level to avoid module loading conflicts
# when using python -m execution

__all__ = ["cli", "interactive", "tui"]