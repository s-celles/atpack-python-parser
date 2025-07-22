#!/usr/bin/env python3
"""Standalone Interactive mode launcher for AtPack Parser."""

if __name__ == "__main__":
    try:
        from atpack_parser.cli.interactive import interactive_mode

        interactive_mode()
    except ImportError as e:
        print(f"❌ Interactive mode import error: {e}")
        print("Please ensure atpack-parser is properly installed.")
        exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        exit(0)
