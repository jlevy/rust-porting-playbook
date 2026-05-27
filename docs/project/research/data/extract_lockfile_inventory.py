#!/usr/bin/env python3
"""Derive lockfile transitive-dependency inventories from a pnpm v9 lockfile.

Reproduces the package-inventory TSV, summary JSON, and top-owners JSON used by the
tbd/qmd dependency port plans. Deterministic: same lockfile in, same data out.

Usage:
    extract_lockfile_inventory.py <pnpm-lock.yaml> <tbd|qmd> <out_prefix>

Owner attribution: every direct dependency ("root") owns its own lock entry plus every
entry reachable through the snapshot graph (`dependencies` + `optionalDependencies`).
Each entry's `owner_groups` is the set of importer-section groups of its owner roots.

Action classification:
- covered-in-direct-plan      : the entry's *name* is itself a direct dependency
- split-runtime-and-tooling   : owned by both runtime-side and tooling-side roots
- replace-through-runtime-owner: owned only by runtime-side roots
- removed-with-js-toolchain   : owned only by tooling-side roots
"""
import json
import sys
from collections import deque

import yaml

# Per-project mapping of (importer_path, manifest_section) -> owner-group label,
# plus which groups count as "runtime-side" for action classification.
PROJECTS = {
    "tbd": {
        "groups": {
            (".", "devDependencies"): "workspace-dev",
            ("packages/tbd", "dependencies"): "runtime",
            ("packages/tbd", "devDependencies"): "package-dev",
        },
        "runtime_side": {"runtime"},
    },
    "qmd": {
        "groups": {
            (".", "dependencies"): "runtime",
            (".", "devDependencies"): "dev",
            (".", "optionalDependencies"): "optional",
            (".", "peerDependencies"): "peer",
        },
        "runtime_side": {"runtime", "optional", "peer"},
    },
}


def split_name_version(key):
    """Split a snapshot key 'name@version(peers)' into (name, version-with-peers)."""
    base = key.split("(", 1)[0]  # strip peer suffix to find the name/version '@'
    at = base.rindex("@")
    name = key[:at]
    version = key[at + 1 :]
    return name, version


def main():
    lock_path, project, out_prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    cfg = PROJECTS[project]
    group_map = cfg["groups"]
    runtime_side = cfg["runtime_side"]

    lock = yaml.safe_load(open(lock_path))
    importers = lock.get("importers", {})
    snapshots = lock.get("snapshots", {})

    # Roots: (root_name, root_key, group) from importer sections.
    roots = []
    direct_names = set()
    direct_entries = 0
    for imp_path, sections in importers.items():
        for section, entries in sections.items():
            group = group_map.get((imp_path, section))
            if group is None or not isinstance(entries, dict):
                continue
            for name, info in entries.items():
                direct_entries += 1
                direct_names.add(name)
                version = info["version"] if isinstance(info, dict) else info
                roots.append((name, f"{name}@{version}", group))

    # Edge map: snapshot key -> list of child snapshot keys.
    edges = {}
    missing_edges = 0
    all_keys = set(snapshots.keys())
    for key, body in snapshots.items():
        children = []
        if isinstance(body, dict):
            for dep_section in ("dependencies", "optionalDependencies"):
                for dname, dver in (body.get(dep_section) or {}).items():
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
    owners = {k: set() for k in snapshots}
    owner_groups = {k: set() for k in snapshots}
    owned_count = {}  # root_name -> number of entries owned
    for root_name, root_key, group in roots:
        if root_key not in snapshots:
            owned_count.setdefault(root_name, owned_count.get(root_name, 0))
            continue
        seen = set()
        q = deque([root_key])
        while q:
            cur = q.popleft()
            if cur in seen or cur not in snapshots:
                continue
            seen.add(cur)
            owners[cur].add(root_name)
            owner_groups[cur].add(group)
            for child in edges.get(cur, []):
                if child not in seen:
                    q.append(child)
        owned_count[root_name] = owned_count.get(root_name, 0) + len(seen)

    # Rows + tallies.
    rows = []
    action_counts = {}
    group_mix_counts = {}
    transitive_entries = 0
    transitive_unique = set()
    unique_names = set()
    unreachable = 0
    for key in sorted(snapshots.keys()):
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
    with open(f"{out_prefix}-package-inventory.tsv", "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    # Top owners (entries owned, descending), excluding roots that own only themselves.
    top = {
        n: c
        for n, c in sorted(owned_count.items(), key=lambda kv: (-kv[1], kv[0]))
        if c > 1
    }
    with open(f"{out_prefix}-top-owners.json", "w") as f:
        json.dump(top, f, indent=2)
        f.write("\n")

    summary = {
        "lock_entries": len(snapshots),
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
    with open(f"{out_prefix}-summary.json", "w") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
