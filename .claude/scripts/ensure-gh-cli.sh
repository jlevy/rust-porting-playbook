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
readonly GH_VERSION="2.96.0"
readonly DIRECT_PROBE_TIMEOUT_SECONDS=20
readonly DIRECT_CONNECT_TIMEOUT_SECONDS=15

# GitHub hosts to exempt from a session HTTPS proxy when that proxy intercepts
# GitHub (proxied remote sessions, e.g. Claude Code cloud). Scoped and additive:
# HTTPS_PROXY stays set for all other traffic. release-assets.githubusercontent.com
# is the current release-binary host; objects.githubusercontent.com is its
# predecessor and kept for compatibility.
readonly GITHUB_DIRECT_HOSTS="api.github.com,github.com,\
release-assets.githubusercontent.com,objects.githubusercontent.com,codeload.github.com,\
raw.githubusercontent.com,uploads.github.com"

github_no_proxy() {
    local existing_no_proxy="${NO_PROXY:-${no_proxy:-}}"
    printf '%s\n' "${GITHUB_DIRECT_HOSTS}${existing_no_proxy:+,$existing_no_proxy}"
}

# Direct-egress probes can hang when the network policy blocks direct
# connections; bound them where timeout(1) exists (absent on stock macOS).
run_bounded() {
    if command -v timeout &> /dev/null; then
        timeout "$DIRECT_PROBE_TIMEOUT_SECONDS" "$@"
    else
        "$@"
    fi
}

# SHA-256 checksums from gh_2.96.0_checksums.txt, keyed by asset suffix.
checksum_for() {
    case "$1" in
        linux_amd64.tar.gz) echo "83d5c2ccad5498f58bf6368acb1ab32588cf43ab3a4b1c301bf36328b1c8bd60" ;;
        linux_arm64.tar.gz) echo "06f86ec7103d41993b76cd78072f43595c34aaa56506d971d9860e67140bf909" ;;
        macOS_amd64.zip)    echo "4bd449df9ad639391bc62b8032546f0fe9edcd8526e06682a4f88abd8c5d163c" ;;
        macOS_arm64.zip)    echo "f23a0c37d963aacc3bed703ccbd59b41c5ca22101fab7f00eb2b7cad23aba463" ;;
        *) echo "" ;;
    esac
}

# Check if gh is already installed
if command -v gh &> /dev/null; then
    echo "[gh] CLI found at $(command -v gh)"
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
        EXTRACT_NAME="gh_${GH_VERSION}_macOS_${ARCH}"
    else
        PLATFORM="${OS}_${ARCH}.tar.gz"
        ARCHIVE_EXT="tar.gz"
        EXTRACT_NAME="gh_${GH_VERSION}_${OS}_${ARCH}"
    fi

    echo "[gh] Detected platform: ${PLATFORM}"

    EXPECTED=$(checksum_for "$PLATFORM")
    if [ -z "$EXPECTED" ]; then
        continue_without_gh "No pinned checksum for ${PLATFORM}; refusing to install an unverified binary."
    fi

    if ! TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/gh-install.XXXXXX"); then
        continue_without_gh "Unable to create a private temporary directory."
    fi
    readonly TEMP_DIR
    cleanup_gh_temp() {
        rm -rf -- "$TEMP_DIR"
    }
    trap cleanup_gh_temp EXIT
    EXTRACT_ROOT="$TEMP_DIR/extracted"
    if ! mkdir -p "$EXTRACT_ROOT"; then
        continue_without_gh "Unable to prepare the private temporary directory."
    fi
    EXTRACT_DIR="${EXTRACT_ROOT}/${EXTRACT_NAME}"

    ASSET="gh_${GH_VERSION}_${PLATFORM}"
    ARCHIVE_PATH="${TEMP_DIR}/${ASSET}"
    DOWNLOAD_URL="https://github.com/cli/cli/releases/download/v${GH_VERSION}/${ASSET}"

    echo "[gh] Downloading from ${DOWNLOAD_URL}..."
    if ! curl -fsSL -o "$ARCHIVE_PATH" "$DOWNLOAD_URL"; then
        # Proxied remote sessions can intercept GitHub downloads with a proxy 403.
        # Retry once bypassing the proxy for GitHub hosts only; this succeeds when
        # the environment's egress policy allows direct GitHub connections.
        echo "[gh] Download failed (a session proxy may intercept GitHub); retrying with NO_PROXY for GitHub hosts..."
        NP="$(github_no_proxy)"
        if ! NO_PROXY="$NP" no_proxy="$NP" curl -fsSL \
            --connect-timeout "$DIRECT_CONNECT_TIMEOUT_SECONDS" \
            -o "$ARCHIVE_PATH" "$DOWNLOAD_URL"; then
            continue_without_gh "Download failed for ${ASSET} through both proxied and direct GitHub channels."
        fi
    fi

    # Verify the download against the pinned checksum before extracting.
    if command -v sha256sum &> /dev/null; then
        if ! ACTUAL=$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}'); then
            continue_without_gh "Unable to calculate the SHA-256 digest for ${ASSET}."
        fi
    elif command -v shasum &> /dev/null; then
        if ! ACTUAL=$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}'); then
            continue_without_gh "Unable to calculate the SHA-256 digest for ${ASSET}."
        fi
    else
        continue_without_gh "No SHA-256 utility is available to verify ${ASSET}."
    fi
    if [ "$ACTUAL" != "$EXPECTED" ]; then
        continue_without_gh "Checksum mismatch for ${ASSET}; expected ${EXPECTED}, received ${ACTUAL}."
    fi
    echo "[gh] Checksum verified for ${ASSET}"

    # Extract based on archive type
    if [ "$ARCHIVE_EXT" = "zip" ]; then
        if ! unzip -q "$ARCHIVE_PATH" -d "$EXTRACT_ROOT"; then
            continue_without_gh "Unable to extract ${ASSET}."
        fi
    else
        if ! tar -xzf "$ARCHIVE_PATH" -C "$EXTRACT_ROOT"; then
            continue_without_gh "Unable to extract ${ASSET}."
        fi
    fi

    # Install to ~/.local/bin (works in cloud and local)
    if ! { mkdir -p ~/.local/bin && cp "${EXTRACT_DIR}/bin/gh" ~/.local/bin/gh && chmod +x ~/.local/bin/gh; }; then
        continue_without_gh "Unable to install gh under ~/.local/bin."
    fi

    # Clean up
    cleanup_gh_temp
    trap - EXIT

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
        # A failed check does NOT prove the token is bad. In proxied remote
        # sessions (HTTPS_PROXY set, e.g. Claude Code cloud) the proxy can
        # intercept api.github.com, block the GraphQL query behind
        # `gh auth status`, and even swap Authorization headers; gh then
        # misreports a perfectly valid token as invalid. Retest on the direct
        # channel (proxy bypassed for GitHub hosts only) before concluding.
        NP="$(github_no_proxy)"
        if [ -n "${HTTPS_PROXY:-}${https_proxy:-}" ] \
            && NO_PROXY="$NP" no_proxy="$NP" run_bounded gh auth status &> /dev/null; then
            echo "[gh] GH_TOKEN is VALID, but this session's proxy intercepts GitHub API calls"
            echo "[gh] ('gh auth status' fails through the proxy and misreports the token as invalid)."
            echo "[gh] To use gh in this session, bypass the proxy for GitHub hosts only"
            echo "[gh] (keep HTTPS_PROXY set; never disable TLS verification):"
            echo '[gh]   export NO_PROXY="'"${GITHUB_DIRECT_HOSTS}"'${NO_PROXY:+,$NO_PROXY}"'
            echo '[gh]   export no_proxy="$NO_PROXY"'
            echo "[gh] Details: tbd shortcut setup-github-cli (Proxied Remote Sessions)"
        else
            echo "[gh] WARNING: GH_TOKEN is set but could not be verified on any channel"
            echo "[gh] Either the token is invalid/expired, or this session's network policy"
            echo "[gh] blocks GitHub API access (git push and GitHub MCP tools may still work)."
            echo "[gh] Diagnosis: tbd shortcut setup-github-cli (Proxied Remote Sessions)"
        fi
    fi
else
    echo "[gh] NOTE: GH_TOKEN not set - some operations may require authentication"
    echo "[gh] See: tbd shortcut setup-github-cli"
fi

exit 0
