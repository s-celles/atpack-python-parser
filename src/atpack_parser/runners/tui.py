#!/usr/bin/env python3
"""Standalone TUI launcher for AtPack Parser."""

if __name__ == "__main__":
    try:
        from atpack_parser.tui.main import run_tui

        run_tui()
    except ImportError:
        print("❌ TUI requires textual package. Install with:")
        print("   pip install atpack-parser[tui]")
        print("   # or")
        print("   pip install textual")
        exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        exit(0)
