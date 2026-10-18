"""Parse command-line arguments and report the pin update."""

import argparse
import os
from pathlib import Path

import httpx

from .models import SourcePin
from .updater import fetch_next_pin, write_pin


def main() -> None:
    """Validate a release, optionally write its pin, and report failures."""
    parser = argparse.ArgumentParser(description="Update Zen's source pin.")
    parser.add_argument(
        "--sources",
        type=Path,
        default=Path("nix/packages/zen-browser/sources.json"),
        help="Pin file to update, relative to the current directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the next release without changing the pin",
    )
    arguments = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    try:
        current = SourcePin.model_validate_json(arguments.sources.read_bytes())
        with httpx.Client(
            timeout=httpx.Timeout(60, connect=10),
            follow_redirects=True,
            headers={"User-Agent": "update-zen"},
        ) as client:
            updated = fetch_next_pin(client, current, token)
        if updated == current:
            print(f"Zen {current.version} is current")
        elif arguments.check:
            print(updated.model_dump_json(by_alias=True, indent=2))
        else:
            write_pin(arguments.sources, updated)
            print(
                f"Updated Zen {current.version} -> {updated.version}, "
                f"Firefox {updated.firefox_version}"
            )
    except (OSError, ValueError, httpx.HTTPError) as error:
        message = str(error) or type(error).__name__
        parser.exit(1, f"update-zen: {message}\n")
