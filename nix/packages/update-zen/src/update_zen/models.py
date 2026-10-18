"""Zen release metadata and source pins."""

import base64
import re
from typing import Annotated, Literal

from pydantic import AliasPath, BaseModel, ConfigDict, Field, HttpUrl, StringConstraints

ZEN_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)(?:\.(\d+))?b$")
ZenVersion = Annotated[str, StringConstraints(pattern=ZEN_VERSION_PATTERN.pattern)]
FirefoxVersion = Annotated[str, StringConstraints(pattern=r"^\d+\.\d+(?:\.\d+)?$")]


def sha256_sri(digest: bytes) -> str:
    """Encode a SHA-256 digest in the SRI format used by Nix."""
    return "sha256-" + base64.b64encode(digest).decode("ascii")


def parse_release_version(version: str) -> tuple[int, int, int]:
    """Return numeric components for comparing numbered Zen releases."""
    match = ZEN_VERSION_PATTERN.fullmatch(version)
    if match is None:
        raise ValueError(f"Unrecognized Zen release version: {version}")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch or 0)


class ReleaseAsset(BaseModel):
    """An archive attached to a GitHub release."""

    name: str
    state: str
    size: int = Field(ge=0)
    browser_download_url: HttpUrl
    digest: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")

    @property
    def published_hash(self) -> str | None:
        """Return GitHub's asset digest in SRI format, when supplied."""
        if self.digest is None:
            return None
        return sha256_sri(bytes.fromhex(self.digest.removeprefix("sha256:")))


class Release(BaseModel):
    """A GitHub release and its assets."""

    tag_name: ZenVersion
    draft: Literal[False]
    prerelease: Literal[False]
    assets: list[ReleaseAsset]

    def linux_archive(self) -> ReleaseAsset:
        """Require one uploaded x86-64 archive at the expected release URL."""
        asset_name = "zen.linux-x86_64.tar.xz"
        matches = [asset for asset in self.assets if asset.name == asset_name]
        if len(matches) != 1:
            raise ValueError(
                f"Release {self.tag_name} must have exactly one {asset_name} asset"
            )
        asset = matches[0]
        expected_url = f"https://github.com/zen-browser/desktop/releases/download/{self.tag_name}/{asset_name}"
        if (
            asset.state != "uploaded"
            or asset.size == 0
            or str(asset.browser_download_url) != expected_url
        ):
            raise ValueError(
                f"Release {self.tag_name} has an incomplete or unexpected archive"
            )
        return asset


class BrowserVersions(BaseModel):
    """Zen and Firefox versions read from a tagged surfer.json file."""

    firefox_version: FirefoxVersion = Field(
        validation_alias=AliasPath("version", "version")
    )
    zen_version: ZenVersion = Field(
        validation_alias=AliasPath("brands", "release", "release", "displayVersion")
    )


class ArchiveSource(BaseModel):
    """Archive URL and SRI hash recorded in the Nix source pin."""

    model_config = ConfigDict(extra="forbid")

    url: HttpUrl
    hash: str = Field(pattern=r"^sha256-[A-Za-z0-9+/]{43}=$")


class SourcePin(BaseModel):
    """The source manifest consumed by the Zen browser derivation."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    version: ZenVersion
    firefox_version: FirefoxVersion = Field(
        validation_alias="firefoxVersion", serialization_alias="firefoxVersion"
    )
    linux_archive: ArchiveSource = Field(
        validation_alias="x86_64-linux", serialization_alias="x86_64-linux"
    )
