"""Update source and npm pins for a Raycast extension packaged for Vicinae."""

import argparse
import json
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

REPOSITORY = "raycast/extensions"
EXTENSIONS = Path("nix/packages/vicinae-extensions")


def run(*command: str) -> str:
    """Return stdout and leave stderr visible."""
    return subprocess.run(
        command, check=True, text=True, stdout=subprocess.PIPE, timeout=1200
    ).stdout.strip()


def github_sha(endpoint: str, query: str = ".sha") -> str:
    """Read a commit or tree SHA from the GitHub API."""
    sha = run("gh", "api", f"repos/{REPOSITORY}/{endpoint}", "--jq", query)
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError(f"Invalid upstream SHA: {sha!r}")
    return sha


def validate_pin(pin: dict[str, str]) -> None:
    """Reject incomplete pins, invalid revisions, and malformed SHA-256 hashes."""
    if set(pin) != {"rev", "hash", "npmDepsHash"}:
        raise ValueError("Expected rev, hash, and npmDepsHash")
    if not re.fullmatch(r"[0-9a-f]{40}", pin["rev"]):
        raise ValueError("Expected a full commit SHA")
    for key in ("hash", "npmDepsHash"):
        if not re.fullmatch(r"sha256-[A-Za-z0-9+/]{43}=", pin[key]):
            raise ValueError(f"Invalid {key}: {pin[key]!r}")


def fetch_next_pin(name: str, current: dict[str, str]) -> dict[str, str]:
    """Prefetch both hashes when the upstream extension directory changes."""
    directory = f"extensions/{name}"
    revision = github_sha(f"commits?path={directory}&per_page=1", ".[0].sha")
    if revision == current["rev"]:
        return current
    current_tree = github_sha(f"git/trees/{current['rev']}:{directory}")
    latest_tree = github_sha(f"git/trees/{revision}:{directory}")
    if current_tree == latest_tree:
        return current
    status = run(
        "gh",
        "api",
        f"repos/{REPOSITORY}/compare/{current['rev']}...{revision}",
        "--jq",
        ".status",
    )
    if status != "ahead":
        raise ValueError(f"Upstream history is {status}; review the revision manually")

    source = json.loads(
        run(
            "nix-prefetch-git",
            "--quiet",
            "--url",
            f"https://github.com/{REPOSITORY}",
            "--rev",
            revision,
            "--sparse-checkout",
            f"/{directory}",
        )
    )
    if source["rev"] != revision:
        raise ValueError("Prefetched revision does not match the upstream commit")
    lockfile = Path(source["path"]) / directory / "package-lock.json"
    pin = {
        "rev": revision,
        "hash": source["hash"],
        "npmDepsHash": run("prefetch-npm-deps", str(lockfile)),
    }
    validate_pin(pin)
    return pin


def report(
    name: str, current: dict[str, str], updated: dict[str, str]
) -> dict[str, object]:
    """Provide extension pin changes and the upstream comparison for the PR."""
    return {
        "package": f"vicinae-extensions-{name}",
        "changes": [
            {"name": label, "before": current[key], "after": updated[key]}
            for key, label in (
                ("rev", "Revision"),
                ("hash", "Source SHA-256"),
                ("npmDepsHash", "npm dependencies SHA-256"),
            )
        ],
        "upstream": f"https://github.com/{REPOSITORY}/compare/{current['rev']}...{updated['rev']}",
    }


def main() -> None:
    """Preview or apply an extension update and optionally write PR metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "extension",
        choices=sorted(path.parent.name for path in EXTENSIONS.glob("*/sources.json")),
        help="Extension to update",
    )
    parser.add_argument(
        "--check", action="store_true", help="Print pins without writing"
    )
    parser.add_argument(
        "--report", type=Path, help="Write pin changes and upstream URL as JSON"
    )
    arguments = parser.parse_args()
    sources = EXTENSIONS / arguments.extension / "sources.json"

    try:
        current = json.loads(sources.read_text())
        if not isinstance(current, dict) or any(
            not isinstance(value, str) for value in current.values()
        ):
            raise ValueError("Expected a JSON object containing string pins")
        validate_pin(current)
        updated = fetch_next_pin(arguments.extension, current)
        if arguments.check:
            print(json.dumps(updated, indent=2))
            return
        if updated != current:
            with TemporaryDirectory(dir=sources.parent) as directory:
                temporary = Path(directory) / sources.name
                temporary.write_text(json.dumps(updated, indent=2) + "\n")
                temporary.replace(sources)
            print(
                f"Updated Vicinae {arguments.extension} extension to {updated['rev']}"
            )
        else:
            print(f"Vicinae {arguments.extension} extension is current")
        if arguments.report:
            arguments.report.write_text(
                json.dumps(report(arguments.extension, current, updated)) + "\n"
            )
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"update-vicinae-extension: {error}\n")


if __name__ == "__main__":
    main()
