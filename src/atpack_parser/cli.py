"""Command Line Interface for AtPack Parser using Typer.

This module provides backward compatibility by importing the modular CLI app
from the cli package.
"""

# Import the modular CLI app
from .cli import app

# Re-export the app for backward compatibility
__all__ = ["app"]


if __name__ == "__main__":
    app()
