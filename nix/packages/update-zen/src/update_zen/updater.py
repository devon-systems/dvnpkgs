"""Validate releases and replace the source pin atomically."""

import tempfile
from pathlib import Path

import httpx

from .models import ArchiveSource, SourcePin, parse_release_version
from .upstream import (
    download_archive_hash,
    fetch_browser_versions,
    fetch_latest_release,
)


def fetch_next_pin(
    client: httpx.Client, current: SourcePin, token: str | None
) -> SourcePin:
    """Validate the latest release and return its pin without changing files."""
    release = fetch_latest_release(client, token)
    version = release.tag_name
    if parse_release_version(version) < parse_release_version(current.version):
        raise ValueError(f"Refusing to downgrade Zen {current.version} to {version}")
    asset = release.linux_archive()
    versions = fetch_browser_versions(client, version)
    archive_hash = asset.published_hash
    if version != current.version or archive_hash is None:
        archive_hash = download_archive_hash(client, asset)
    updated = SourcePin(
        version=version,
        firefox_version=versions.firefox_version,
        linux_archive=ArchiveSource(url=asset.browser_download_url, hash=archive_hash),
    )
    if updated.version == current.version and updated != current:
        raise ValueError(
            f"Pinned release {updated.version} changed upstream; review its archive and metadata manually"
        )
    return updated


def write_pin(path: Path, pin: SourcePin) -> None:
    """Replace the pin atomically using a temporary file on the same filesystem."""
    with tempfile.TemporaryDirectory(dir=path.parent) as directory:
        temporary_path = Path(directory) / "sources.json"
        temporary_path.write_text(
            pin.model_dump_json(by_alias=True, indent=2) + "\n", encoding="utf-8"
        )
        temporary_path.replace(path)
