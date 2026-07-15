#!/bin/bash
# Automated GitHub CLI setup for Claude Code sessions
# This script runs on SessionStart to ensure gh CLI is available and authenticated
#
# Supply-chain policy (see SUPPLY-CHAIN-SECURITY.md): the gh version is PINNED to
# a release at least 14 days old, and every download is verified against a pinned
# SHA-256 checksum. Do NOT change this to fetch "latest" from the API at runtime;
# that bypasses the cool-off window. To bump the pin, pick a release that is >=14
# days old and copy its checksums from:
#   https://github.com/cli/cli/releases/download/v<VERSION>/gh_<VERSION>_checksums.txt

set -euo pipefail

continue_without_gh() {
    echo "[gh] WARNING: $1" >&2
    echo "[gh] Continuing without gh; local tbd workflows remain available." >&2
    exit 0
}

# Add common binary locations to PATH
export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:$PATH"

# Pinned gh release (>=14 days old per supply-chain cool-off) and its checksums.
GH_VERSION="2.92.0"

# SHA-256 checksums from gh_2.92.0_checksums.txt, keyed by asset suffix.
checksum_for() {
    case "$1" in
        linux_amd64.tar.gz) echo "b57848131bdf0c229cd35e1f2a51aa718199858b2e728410b37e89a428943ec4" ;;
        linux_arm64.tar.gz) echo "c2248526dd0160c08d3fccca2332c3c1a07c15a78b23978e77735f1b5a18cfee" ;;
        macOS_amd64.zip)    echo "ae9bb327ab0d91071bdada79f8f14034a2a0f19b0e001835a782eafa519d2af0" ;;
        macOS_arm64.zip)    echo "b11c54f6bd7d15ed6590475079e5b2fcf36f45d3991a80041b29c9d0cc1f1d07" ;;
        *) echo "" ;;
    esac
}

# Check if gh is already installed
if command -v gh &> /dev/null; then
    echo "[gh] CLI found at $(which gh)"
else
    echo "[gh] CLI not found, installing pinned v${GH_VERSION}..."

    # Detect platform
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    [ "$ARCH" = "x86_64" ] && ARCH="amd64"
    [ "$ARCH" = "aarch64" ] && ARCH="arm64"

    # Build the asset suffix and archive type per platform.
    if [ "$OS" = "darwin" ]; then
        PLATFORM="macOS_${ARCH}.zip"
        ARCHIVE_EXT="zip"
        EXTRACT_DIR="/tmp/gh_${GH_VERSION}_macOS_${ARCH}"
    else
        PLATFORM="${OS}_${ARCH}.tar.gz"
        ARCHIVE_EXT="tar.gz"
        EXTRACT_DIR="/tmp/gh_${GH_VERSION}_${OS}_${ARCH}"
    fi

    echo "[gh] Detected platform: ${PLATFORM}"

    EXPECTED=$(checksum_for "$PLATFORM")
    if [ -z "$EXPECTED" ]; then
        continue_without_gh "No pinned checksum for ${PLATFORM}; refusing to install an unverified binary."
    fi

    ASSET="gh_${GH_VERSION}_${PLATFORM}"
    DOWNLOAD_URL="https://github.com/cli/cli/releases/download/v${GH_VERSION}/${ASSET}"

    echo "[gh] Downloading from ${DOWNLOAD_URL}..."
    if ! curl -fsSL -o "/tmp/${ASSET}" "$DOWNLOAD_URL"; then
        rm -f "/tmp/${ASSET}"
        continue_without_gh "Download failed for ${ASSET}."
    fi

    # Verify the download against the pinned checksum before extracting.
    if command -v sha256sum &> /dev/null; then
        if ! ACTUAL=$(sha256sum "/tmp/${ASSET}" | awk '{print $1}'); then
            rm -f "/tmp/${ASSET}"
            continue_without_gh "Unable to calculate the SHA-256 digest for ${ASSET}."
        fi
    elif command -v shasum &> /dev/null; then
        if ! ACTUAL=$(shasum -a 256 "/tmp/${ASSET}" | awk '{print $1}'); then
            rm -f "/tmp/${ASSET}"
            continue_without_gh "Unable to calculate the SHA-256 digest for ${ASSET}."
        fi
    else
        rm -f "/tmp/${ASSET}"
        continue_without_gh "No SHA-256 utility is available to verify ${ASSET}."
    fi
    if [ "$ACTUAL" != "$EXPECTED" ]; then
        rm -f "/tmp/${ASSET}"
        continue_without_gh "Checksum mismatch for ${ASSET}; expected ${EXPECTED}, received ${ACTUAL}."
    fi
    echo "[gh] Checksum verified for ${ASSET}"

    # Extract based on archive type
    if [ "$ARCHIVE_EXT" = "zip" ]; then
        if ! unzip -q "/tmp/${ASSET}" -d /tmp; then
            rm -rf "${EXTRACT_DIR}" "/tmp/${ASSET}"
            continue_without_gh "Unable to extract ${ASSET}."
        fi
    else
        if ! tar -xzf "/tmp/${ASSET}" -C /tmp; then
            rm -rf "${EXTRACT_DIR}" "/tmp/${ASSET}"
            continue_without_gh "Unable to extract ${ASSET}."
        fi
    fi

    # Install to ~/.local/bin (works in cloud and local)
    if ! { mkdir -p ~/.local/bin && cp "${EXTRACT_DIR}/bin/gh" ~/.local/bin/gh && chmod +x ~/.local/bin/gh; }; then
        rm -rf "${EXTRACT_DIR}" "/tmp/${ASSET}"
        continue_without_gh "Unable to install gh under ~/.local/bin."
    fi

    # Clean up
    rm -rf "${EXTRACT_DIR}" "/tmp/${ASSET}"

    echo "[gh] Installed to ~/.local/bin/gh"
fi

# Verify gh is now in PATH
if ! command -v gh &> /dev/null; then
    continue_without_gh "gh is still not on PATH after installation."
fi

# Check authentication status
if [ -n "${GH_TOKEN:-}" ]; then
    # GH_TOKEN is set, verify it works
    if gh auth status &> /dev/null; then
        echo "[gh] Authenticated successfully"
    else
        echo "[gh] WARNING: GH_TOKEN is set but authentication check failed"
        echo "[gh] Token may be invalid or expired"
    fi
else
    echo "[gh] NOTE: GH_TOKEN not set - some operations may require authentication"
    echo "[gh] See: docs/general/agent-setup/github-cli-setup.md"
fi

exit 0
