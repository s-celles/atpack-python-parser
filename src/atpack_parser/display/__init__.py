"""Shared display utilities for CLI and interactive mode."""

from .memory import display_flat_memory, display_hierarchical_memory
from .registers import display_registers

__all__ = [
    "display_flat_memory",
    "display_hierarchical_memory",
    "display_registers",
]