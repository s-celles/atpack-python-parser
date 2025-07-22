#!/usr/bin/env python3
"""Standalone CLI launcher for AtPack Parser."""

if __name__ == "__main__":
    try:
        from atpack_parser.cli import app

        app()
    except ImportError as e:
        print(f"❌ CLI import error: {e}")
        print("Please ensure atpack-parser is properly installed.")
        exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        exit(0)
