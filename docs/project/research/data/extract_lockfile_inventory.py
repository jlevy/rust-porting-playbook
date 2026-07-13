#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML==6.0.3",
# ]
# ///
"""Derive lockfile transitive-dependency inventories from a pnpm v9 lockfile.

Reproduces the package-inventory TSV, summary JSON, and top-owners JSON used by the
tbd/qmd dependency port plans. Deterministic: same lockfile in, same data out.

Usage:
    uv --no-config run --locked --script extract_lockfile_inventory.py \
        <pnpm-lock.yaml> <tbd|qmd> <out_prefix>

Owner attribution: every direct dependency ("root") owns its own lock entry plus every
entry reachable through the snapshot graph (`dependencies` + `optionalDependencies`).
Each entry's `owner_groups` is the set of importer-section groups of its owner roots.

Action classification:
- covered-in-direct-plan      : the entry's *name* is itself a direct dependency
- split-runtime-and-tooling   : owned by both runtime-side and tooling-side roots
- replace-through-runtime-owner: owned only by runtime-side roots
- removed-with-js-toolchain   : owned only by tooling-side roots
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    """Importer groups and runtime-side groups for one source project."""

    groups: Mapping[tuple[str, str], str]
    runtime_side: frozenset[str]


# Per-project mapping of (importer_path, manifest_section) -> owner-group label,
# plus which groups count as "runtime-side" for action classification.
PROJECTS = {
    "tbd": ProjectConfig(
        groups={
            (".", "devDependencies"): "workspace-dev",
            ("packages/tbd", "dependencies"): "runtime",
            ("packages/tbd", "devDependencies"): "package-dev",
        },
        runtime_side=frozenset({"runtime"}),
    ),
    "qmd": ProjectConfig(
        groups={
            (".", "dependencies"): "runtime",
            (".", "devDependencies"): "dev",
            (".", "optionalDependencies"): "optional",
            (".", "peerDependencies"): "peer",
        },
        runtime_side=frozenset({"runtime", "optional", "peer"}),
    ),
}


def split_name_version(key: str) -> tuple[str, str]:
    """Split a snapshot key 'name@version(peers)' into (name, version-with-peers)."""
    base = key.split("(", 1)[0]  # strip peer suffix to find the name/version '@'
    at = base.rindex("@")
    name = key[:at]
    version = key[at + 1 :]
    return name, version


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Derive deterministic transitive dependency inventories from a pnpm lockfile."
    )
    parser.add_argument("lockfile", type=Path, help="pnpm v9 lockfile to analyze")
    parser.add_argument("project", choices=sorted(PROJECTS))
    parser.add_argument(
        "output_prefix",
        type=Path,
        help="prefix for the generated TSV and JSON files",
    )
    return parser.parse_args()


def _mapping(value: object, context: str) -> Mapping[object, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Expected a mapping for {context}")
    return value


def main() -> int:
    args = _parse_args()
    lock_path = cast(Path, args.lockfile)
    project = cast(str, args.project)
    out_prefix = cast(Path, args.output_prefix)
    cfg = PROJECTS[project]
    group_map = cfg.groups
    runtime_side = cfg.runtime_side

    lock = _mapping(
        yaml.safe_load(lock_path.read_text(encoding="utf-8")), str(lock_path)
    )
    importers = _mapping(lock.get("importers", {}), "importers")
    snapshots = _mapping(lock.get("snapshots", {}), "snapshots")

    # Roots: (root_name, root_key, group) from importer sections.
    roots: list[tuple[str, str, str]] = []
    direct_names: set[str] = set()
    direct_entries = 0
    for imp_path_value, sections_value in importers.items():
        imp_path = str(imp_path_value)
        sections = _mapping(sections_value, f"importer {imp_path}")
        for section_value, entries in sections.items():
            section = str(section_value)
            group = group_map.get((imp_path, section))
            if group is None or not isinstance(entries, Mapping):
                continue
            for name_value, info in entries.items():
                name = str(name_value)
                direct_entries += 1
                direct_names.add(name)
                version = info["version"] if isinstance(info, Mapping) else info
                roots.append((name, f"{name}@{version}", group))

    # Edge map: snapshot key -> list of child snapshot keys.
    edges: dict[str, list[str]] = {}
    missing_edges = 0
    all_keys = {str(key) for key in snapshots}
    for key_value, body in snapshots.items():
        key = str(key_value)
        children: list[str] = []
        if isinstance(body, Mapping):
            for dep_section in ("dependencies", "optionalDependencies"):
                dependencies = _mapping(body.get(dep_section) or {}, dep_section)
                for dname_value, dver in dependencies.items():
                    dname = str(dname_value)
                    # Alias edges: when the value (ignoring any peer suffix) already
                    # contains '@', it is a direct snapshot key for a differently-named
                    # package (e.g. string-width-cjs -> string-width@4.2.3).
                    if "@" in str(dver).split("(", 1)[0]:
                        child = str(dver)
                    else:
                        child = f"{dname}@{dver}"
                    children.append(child)
                    if child not in all_keys:
                        missing_edges += 1
        edges[key] = children

    # Owner attribution: BFS from each root, accumulate owners/groups per entry.
    owners: dict[str, set[str]] = {key: set() for key in all_keys}
    owner_groups: dict[str, set[str]] = {key: set() for key in all_keys}
    owned_count: dict[str, int] = {}  # root_name -> number of entries owned
    for root_name, root_key, group in roots:
        if root_key not in all_keys:
            owned_count.setdefault(root_name, owned_count.get(root_name, 0))
            continue
        seen: set[str] = set()
        q = deque([root_key])
        while q:
            cur = q.popleft()
            if cur in seen or cur not in all_keys:
                continue
            seen.add(cur)
            owners[cur].add(root_name)
            owner_groups[cur].add(group)
            for child in edges.get(cur, []):
                if child not in seen:
                    q.append(child)
        owned_count[root_name] = owned_count.get(root_name, 0) + len(seen)

    # Rows + tallies.
    rows: list[list[str]] = []
    action_counts: dict[str, int] = {}
    group_mix_counts: dict[str, int] = {}
    transitive_entries = 0
    transitive_unique: set[str] = set()
    unique_names: set[str] = set()
    unreachable = 0
    for key in sorted(all_keys):
        name, version = split_name_version(key)
        unique_names.add(name)
        is_direct = name in direct_names
        ogroups = sorted(owner_groups[key])
        oroots = sorted(owners[key])
        if not oroots:
            unreachable += 1
        if is_direct:
            action = "covered-in-direct-plan"
        elif any(g in runtime_side for g in ogroups) and any(
            g not in runtime_side for g in ogroups
        ):
            action = "split-runtime-and-tooling"
        elif ogroups and all(g in runtime_side for g in ogroups):
            action = "replace-through-runtime-owner"
        else:
            action = "removed-with-js-toolchain"
        if not is_direct:
            transitive_entries += 1
            transitive_unique.add(name)
        action_counts[action] = action_counts.get(action, 0) + 1
        mix = "+".join(ogroups)
        if mix:
            group_mix_counts[mix] = group_mix_counts.get(mix, 0) + 1
        rows.append(
            [
                key,
                name,
                version,
                "true" if is_direct else "false",
                str(len(oroots)),
                ",".join(oroots),
                ",".join(ogroups),
                action,
            ]
        )

    # Write TSV.
    header = [
        "lock_key",
        "name",
        "version",
        "is_direct_name",
        "owner_count",
        "owners",
        "owner_groups",
        "action",
    ]
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    inventory_lines = ["\t".join(header), *("\t".join(row) for row in rows)]
    Path(f"{out_prefix}-package-inventory.tsv").write_text(
        "\n".join(inventory_lines) + "\n", encoding="utf-8"
    )

    # Top owners (entries owned, descending), excluding roots that own only themselves.
    top = {
        n: c
        for n, c in sorted(owned_count.items(), key=lambda kv: (-kv[1], kv[0]))
        if c > 1
    }
    Path(f"{out_prefix}-top-owners.json").write_text(
        json.dumps(top, indent=2) + "\n", encoding="utf-8"
    )

    summary = {
        "lock_entries": len(all_keys),
        "lock_unique_names": len(unique_names),
        "direct_manifest_entries": direct_entries,
        "direct_manifest_unique_names": len(direct_names),
        "transitive_entries": transitive_entries,
        "transitive_unique_names": len(transitive_unique),
        "action_counts": action_counts,
        "owner_group_mix_counts": group_mix_counts,
        "missing_edges": missing_edges,
        "unreachable_entries": unreachable,
    }
    Path(f"{out_prefix}-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
