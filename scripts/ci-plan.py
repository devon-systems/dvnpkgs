"""Select native CI builds whose outputs no binary cache has yet.

An output in a cache already built successfully, either in an earlier CI run
that pushed it to Cachix or on Hydra. An output in neither cache needs a
build, whether its derivation changed or an earlier run never finished it.
"""

import http.client
import json
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from pathlib import PurePosixPath

RUNNERS = {
    "x86_64-linux": "ubuntu-latest",
    "aarch64-darwin": "macos-latest",
}
CACHES = (
    "https://alyraffauf.cachix.org",
    "https://cache.nixos.org",
)
OUTPUT_PATHS = (
    "builtins.mapAttrs (_: builtins.mapAttrs (_: derivation: derivation.outPath))"
)
LOOKUP_TIMEOUT = 10
LOOKUP_WORKERS = 16
# Cachix refuses urllib's default User-Agent.
USER_AGENT = "dvnpkgs-ci-plan"


def evaluate_outputs() -> dict[str, dict[str, dict[str, str]]]:
    """Evaluate package and check output paths for every exported system."""
    outputs: dict[str, dict[str, dict[str, str]]] = {}
    for kind in ("packages", "checks"):
        result = subprocess.run(
            [
                "nix",
                "eval",
                "--json",
                "--no-update-lock-file",
                f".#{kind}",
                "--apply",
                OUTPUT_PATHS,
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        outputs[kind] = json.loads(result.stdout)
    return outputs


def is_cached(output: str) -> bool:
    """Return whether any cache has the output.

    Lookup errors count as missing, so an outage means extra builds rather
    than skipped ones. Anything but a 404 is logged to explain them.
    """
    digest = PurePosixPath(output).name.split("-", 1)[0]
    for cache in CACHES:
        request = urllib.request.Request(
            f"{cache}/{digest}.narinfo",
            headers={"User-Agent": USER_AGENT},
            method="HEAD",
        )
        try:
            with urllib.request.urlopen(request, timeout=LOOKUP_TIMEOUT):
                return True
        except urllib.error.HTTPError as error:
            if error.code != HTTPStatus.NOT_FOUND:
                print(f"{cache}: HTTP {error.code} for {output}", file=sys.stderr)
        except (OSError, http.client.HTTPException) as error:
            print(f"{cache}: {error!r} for {output}", file=sys.stderr)
    return False


def plan_builds() -> list[dict[str, str]]:
    """Select every package and check whose output isn't cached."""
    candidates = [
        (kind, system, name, output)
        for kind, systems in evaluate_outputs().items()
        for system, outputs in systems.items()
        for name, output in outputs.items()
        if not (kind == "checks" and name == "treefmt")
    ]
    with ThreadPoolExecutor(LOOKUP_WORKERS) as pool:
        cached = list(pool.map(is_cached, (output for *_, output in candidates)))
    return [
        {
            "name": f"{'Build' if kind == 'packages' else 'Check'} {name} ({system})",
            "runner": RUNNERS[system],
            "installable": f"{kind}.{system}.{name}",
        }
        for (kind, system, name, _), hit in zip(candidates, cached, strict=True)
        if not hit
    ]


def main() -> None:
    """Write the selected GitHub Actions matrix to standard output."""
    print(json.dumps({"include": plan_builds()}))


if __name__ == "__main__":
    main()
