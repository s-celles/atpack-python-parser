"""Common types and utilities for CLI commands."""

from pathlib import Path
from typing import Annotated, List

import typer
from rapidfuzz import fuzz
from rich.console import Console

from ..exceptions import AtPackError, DeviceNotFoundError

# Create console for rich output
console = Console()

# Common types
AtPackPath = Annotated[Path, typer.Argument(help="Path to AtPack file or directory")]
DeviceName = Annotated[
    str, typer.Argument(help="Device name (e.g., ATmega16, PIC16F876A)")
]
OutputFormat = Annotated[str, typer.Option("--format", "-f", help="Output format")]


def _get_device_suggestions(
    target_device: str, parser, max_suggestions: int = 5
) -> List[str]:
    """Get the closest device name suggestions using fuzzy string matching."""
    try:
        all_devices = parser.get_devices()

        device_scores = []
        target_upper = target_device.upper()

        for device in all_devices:
            device_upper = device.upper()

            # Calculate multiple scores for better ranking

            # 1. Exact case-insensitive match gets highest priority
            if target_upper == device_upper:
                final_score = 0  # Perfect match
            else:
                # 2. Use multiple fuzzy matching algorithms
                ratio_score = fuzz.ratio(target_upper, device_upper)
                partial_ratio_score = fuzz.partial_ratio(target_upper, device_upper)
                token_sort_ratio_score = fuzz.token_sort_ratio(
                    target_upper, device_upper
                )
                token_set_ratio_score = fuzz.token_set_ratio(target_upper, device_upper)

                # 3. Weighted combination of scores (higher is better)
                # Give more weight to ratio and partial_ratio for exact character matching
                combined_score = (
                    ratio_score * 0.4
                    + partial_ratio_score * 0.3
                    + token_sort_ratio_score * 0.2
                    + token_set_ratio_score * 0.1
                )

                # Convert to distance-like score (lower is better) for consistency
                final_score = 100 - combined_score

            device_scores.append((device, final_score))

        # Sort by final score (lower is better)
        device_scores.sort(key=lambda x: x[1])
        suggestions = [device for device, _ in device_scores[:max_suggestions]]

        return suggestions
    except Exception:
        # If we can't get suggestions for any reason, return empty list
        return []


def handle_device_not_found_error(
    e: DeviceNotFoundError, parser=None, no_color: bool = False
) -> None:
    """Handle DeviceNotFoundError consistently across all CLI commands with device suggestions."""
    error_msg = (
        f"[red]Device not found: {e}[/red]"
        if not no_color
        else f"Device not found: {e}"
    )
    console.print(error_msg)

    # Try to provide helpful suggestions if parser is available
    if parser is not None:
        # Extract device name from the exception message
        device_name = (
            str(e)
            .replace("Device not found: ", "")
            .replace("Device ", "")
            .replace(" not found", "")
        )

        suggestions = _get_device_suggestions(device_name, parser, max_suggestions=15)
        if suggestions:
            suggestion_msg = (
                "[yellow]Did you mean one of these devices?[/yellow]"
                if not no_color
                else "Did you mean one of these devices?"
            )
            console.print(f"\n{suggestion_msg}")

            for i, suggestion in enumerate(suggestions, 1):
                suggestion_text = (
                    f"[dim]{i}.[/dim] [cyan]{suggestion}[/cyan]"
                    if not no_color
                    else f"{i}. {suggestion}"
                )
                console.print(f"  {suggestion_text}")

    raise typer.Exit(1)


def handle_atpack_error(e: AtPackError, no_color: bool = False) -> None:
    """Handle AtPackError consistently across all CLI commands."""
    error_msg = f"[red]Error: {e}[/red]" if not no_color else f"Error: {e}"
    console.print(error_msg)
    raise typer.Exit(1)
