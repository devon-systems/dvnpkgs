"""Select native CI builds by comparing Nix derivations with a base commit."""

import argparse
import json
import subprocess
from pathlib import Path

RUNNERS = {
    "x86_64-linux": "ubuntu-latest",
    "aarch64-darwin": "macos-latest",
}
DERIVATION_PATHS = (
    "builtins.mapAttrs (_: builtins.mapAttrs (_: derivation: derivation.drvPath))"
)


def evaluate_derivations(flake: str) -> dict[str, dict[str, dict[str, str]]]:
    """Evaluate package and check derivation paths for every exported system."""
    outputs: dict[str, dict[str, dict[str, str]]] = {}
    for kind in ("packages", "checks"):
        result = subprocess.run(
            [
                "nix",
                "eval",
                "--json",
                "--no-update-lock-file",
                f"{flake}#{kind}",
                "--apply",
                DERIVATION_PATHS,
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        outputs[kind] = json.loads(result.stdout)
    return outputs


def plan_builds(base: str | None) -> list[dict[str, str]]:
    """Select changed builds, or all builds after flake or CI edits."""
    previous: dict[str, dict[str, dict[str, str]]] = {}
    if base is not None:
        changed_files = subprocess.run(
            ["git", "diff", "--name-only", base, "--"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.splitlines()
        shared_inputs_changed = any(
            path.startswith(".github/workflows/")
            or path in {"flake.nix", "flake.lock", "scripts/ci-plan.py"}
            for path in changed_files
        )
        if not shared_inputs_changed:
            flake = f"git+{Path.cwd().as_uri()}?rev={base}&shallow=1"
            previous = evaluate_derivations(flake)

    builds = []
    for kind, systems in evaluate_derivations(".").items():
        for system, derivations in systems.items():
            for name, derivation in derivations.items():
                if kind == "checks" and name == "treefmt":
                    continue
                previous_derivation = previous.get(kind, {}).get(system, {}).get(name)
                if previous_derivation == derivation:
                    continue
                label = "Build" if kind == "packages" else "Check"
                builds.append(
                    {
                        "name": f"{label} {name} ({system})",
                        "runner": RUNNERS[system],
                        "installable": f"{kind}.{system}.{name}",
                    }
                )
    return builds


def main() -> None:
    """Write the selected GitHub Actions matrix to standard output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Base commit SHA for a pull request")
    arguments = parser.parse_args()
    print(json.dumps({"include": plan_builds(arguments.base)}))


if __name__ == "__main__":
    main()
