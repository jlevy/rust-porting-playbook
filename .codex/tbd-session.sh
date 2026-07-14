#!/bin/bash
# Ensure the tbd CLI is available and run `tbd prime`.
# Installed by: tbd setup --auto. Runs on SessionStart and PreCompact.
#
# Version-matched local binary first, then a pinned zero-install fallback. Pinning is a
# supply-chain control (an unpinned runner re-resolves to latest on every run
# and bypasses any cool-off) and a consistency control (every teammate and agent
# runs the same tbd version).

readonly TBD_VERSION="0.4.0"

# Anchor all repository operations to the worktree containing this hook.
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if ! repo_root=$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null); then
    echo "[tbd] Unable to locate the repository containing $script_dir." >&2
    exit 1
fi
if ! cd "$repo_root"; then
    echo "[tbd] Unable to enter repository root: $repo_root" >&2
    exit 1
fi

# Restore npm's global bin directory when it is outside the common locations.
export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:$PATH"
npm_global_bin=""
if command -v npm &> /dev/null; then
    npm_prefix=$(npm config get prefix 2>/dev/null || true)
    if [[ -n "$npm_prefix" && -d "$npm_prefix/bin" ]]; then
        npm_global_bin="$npm_prefix/bin"
    fi
fi
if [[ -n "$npm_global_bin" ]]; then
    export PATH="$npm_global_bin:$PATH"
fi

# Use a local binary only when it matches the repository-required version.
if command -v tbd &> /dev/null; then
    installed_version=$(tbd --version 2>/dev/null || true)
    if [[ "$installed_version" == "$TBD_VERSION" ]]; then
        tbd prime "$@"
        exit $?
    fi
    echo "[tbd] Ignoring tbd $installed_version; this repository requires $TBD_VERSION." >&2
fi

# Pinned zero-install fallback with package lifecycle scripts disabled.
if command -v npx &> /dev/null; then
    NPM_CONFIG_IGNORE_SCRIPTS=true npx --yes "get-tbd@$TBD_VERSION" prime "$@"
    exit $?
fi

echo "[tbd] tbd $TBD_VERSION is unavailable and npx is unavailable."
echo "[tbd] Install it with: npm install -g get-tbd@$TBD_VERSION"
exit 1
