"""Update the BenQ Display Pilot 2 Linux release pin."""

import argparse
import http.client
import json
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from urllib.request import Request, urlopen

SOURCES = Path("nix/packages/display-pilot-2/sources.json")
API = "https://www.benq.com/api/esupport-tm/getFiles/en_gb/Display%20Pilot%202/en_gb,ge_ge"
# The files API rejects requests that do not come from the download page.
REFERER = "https://www.benq.com/en-us/support/downloads-faq/products/monitor/display-pilot-2/software-driver.html"
DOWNLOAD_HOST = "https://esupportdownload.benq.com/"


def validate_pin(pin: dict[str, str]) -> None:
    """Reject incomplete pins, unexpected hosts, and malformed SHA-256 hashes."""
    if set(pin) != {"version", "url", "hash"}:
        raise ValueError("Expected version, url, and hash")
    if not re.fullmatch(r"\d+(\.\d+)+", pin["version"]):
        raise ValueError(f"Invalid version: {pin['version']!r}")
    if not pin["url"].startswith(DOWNLOAD_HOST):
        raise ValueError(f"Unexpected download host: {pin['url']!r}")
    if not re.fullmatch(r"sha256-[A-Za-z0-9+/]{43}=", pin["hash"]):
        raise ValueError(f"Invalid hash: {pin['hash']!r}")


def version_key(version: str) -> tuple[int, ...]:
    """Split a dotted version into integers for ordering."""
    return tuple(int(part) for part in version.split("."))


def latest_release() -> tuple[str, str]:
    """Return the version and encoded download URL of the Linux release."""
    request = Request(API, headers={"Referer": REFERER, "User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=60) as response:
        files = json.load(response)["response"]["list"]["detail"]
    if not isinstance(files, list):
        raise TypeError("Expected a list of files from the BenQ API")
    releases = [
        entry
        for entry in files
        if isinstance(entry, dict)
        and entry.get("OS") == "Linux"
        and entry.get("Description") == "Display Pilot 2 for Linux"
    ]
    if len(releases) != 1:
        raise ValueError(f"Expected one Linux release, found {len(releases)}")
    version, download = releases[0].get("Version"), releases[0].get("Download")
    if not isinstance(version, str) or not isinstance(download, str):
        raise TypeError("Linux release lacks a version or download URL")
    version = version.removeprefix("V").removeprefix("v")
    if not re.fullmatch(r"\d+(\.\d+)+", version):
        raise ValueError(f"Invalid upstream version: {version!r}")
    return version, quote(download, safe=":/")


def fetch_next_pin(current: dict[str, str]) -> dict[str, str]:
    """Prefetch the archive when BenQ publishes a new Linux release."""
    version, url = latest_release()
    if version == current["version"]:
        if url == current["url"]:
            return current
        raise ValueError(f"BenQ changed the {version} download URL; review manually")
    if version_key(version) < version_key(current["version"]):
        raise ValueError(
            f"BenQ offers {version}, older than {current['version']}; review manually"
        )
    prefetched = json.loads(
        subprocess.run(
            [
                "nix",
                "store",
                "prefetch-file",
                "--json",
                "--name",
                f"display-pilot-2-{version}.zip",
                url,
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            timeout=1200,
        ).stdout
    )
    pin = {"version": version, "url": url, "hash": prefetched["hash"]}
    validate_pin(pin)
    return pin


def report(current: dict[str, str], updated: dict[str, str]) -> dict[str, object]:
    """Provide release pin changes and the download page for the PR."""
    return {
        "package": "display-pilot-2",
        "changes": [
            {"name": label, "before": current[key], "after": updated[key]}
            for key, label in (
                ("version", "Display Pilot 2"),
                ("hash", "x86_64-linux SHA-256"),
            )
        ],
        "upstream": REFERER,
    }


def main() -> None:
    """Preview or apply a release update and optionally write PR metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Print the pin without writing"
    )
    parser.add_argument(
        "--report", type=Path, help="Write pin changes and upstream URL as JSON"
    )
    arguments = parser.parse_args()

    try:
        current = json.loads(SOURCES.read_text())
        if not isinstance(current, dict) or any(
            not isinstance(value, str) for value in current.values()
        ):
            raise ValueError("Expected a JSON object containing string pins")
        validate_pin(current)
        updated = fetch_next_pin(current)
        if arguments.check:
            print(json.dumps(updated, indent=2))
            return
        if updated != current:
            with TemporaryDirectory(dir=SOURCES.parent) as directory:
                temporary = Path(directory) / SOURCES.name
                temporary.write_text(json.dumps(updated, indent=2) + "\n")
                temporary.replace(SOURCES)
            print(f"Updated Display Pilot 2 to {updated['version']}")
        else:
            print("Display Pilot 2 is current")
        if arguments.report:
            arguments.report.write_text(json.dumps(report(current, updated)) + "\n")
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        http.client.HTTPException,
        subprocess.SubprocessError,
    ) as error:
        parser.exit(1, f"update-display-pilot-2: {error}\n")


if __name__ == "__main__":
    main()
