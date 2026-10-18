"""Fetch Zen releases, browser metadata, and verified archive hashes."""

import hashlib

import httpx

from .models import BrowserVersions, Release, ReleaseAsset, sha256_sri


def fetch_latest_release(client: httpx.Client, token: str | None) -> Release:
    """Fetch the latest numbered release, authenticating only this API request."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.get(
        "https://api.github.com/repos/zen-browser/desktop/releases/latest",
        headers=headers,
    )
    response.raise_for_status()
    return Release.model_validate_json(response.content)


def fetch_browser_versions(client: httpx.Client, version: str) -> BrowserVersions:
    """Read tagged browser metadata and require a matching Zen version."""
    response = client.get(
        f"https://raw.githubusercontent.com/zen-browser/desktop/{version}/surfer.json"
    )
    response.raise_for_status()
    versions = BrowserVersions.model_validate_json(response.content)
    if versions.zen_version != version:
        raise ValueError(f"Release {version} has inconsistent version metadata")
    return versions


def download_archive_hash(client: httpx.Client, asset: ReleaseAsset) -> str:
    """Hash the archive and verify its size and published digest."""
    digest = hashlib.sha256()
    size_bytes = 0
    with client.stream("GET", str(asset.browser_download_url)) as response:
        response.raise_for_status()
        for chunk in response.iter_bytes():
            size_bytes += len(chunk)
            if size_bytes > asset.size:
                raise ValueError("Zen archive exceeds its declared size")
            digest.update(chunk)

    if size_bytes != asset.size:
        raise ValueError(
            f"Downloaded Zen archive has size {size_bytes}, expected {asset.size}"
        )
    archive_hash = sha256_sri(digest.digest())
    if asset.published_hash is not None and archive_hash != asset.published_hash:
        raise ValueError("Downloaded Zen archive does not match the published digest")
    return archive_hash
