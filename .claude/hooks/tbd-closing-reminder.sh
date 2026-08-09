#!/bin/bash
# Remind about close protocol after git push
# Installed by: tbd setup --auto

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Match a git command at the start of a shell segment, allowing documented global
# options such as `-C <path>` before the push subcommand. This inspects text only; it
# never evaluates it.
readonly shell_word="(\"[^\"]*\"|'[^']*'|[^;&|[:space:]]+)"
readonly git_value_option="((-C|-c)[[:space:]]+$shell_word|--(exec-path|git-dir|work-tree|namespace|config-env)=$shell_word)"
readonly git_flag_option='(-p|-P|--paginate|--no-pager|--no-replace-objects|--no-lazy-fetch|--no-optional-locks|--no-advice|--bare|--literal-pathspecs|--glob-pathspecs|--noglob-pathspecs|--icase-pathspecs)'
readonly git_push_pattern="(^|[;&|][[:space:]]*)git([[:space:]]+($git_value_option|$git_flag_option))*[[:space:]]+push([[:space:];&|]|$)"
if [[ "$command" =~ $git_push_pattern ]]; then
  # Anchor repository discovery to this script, not the hook runner's cwd.
  script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  repo_root=$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null) && cd "$repo_root"
  if [ -d ".tbd" ]; then
    # Same version-matched, pinned fallback as tbd-session.sh, so the
    # reminder still fires when tbd is not on the hook's PATH.
    readonly TBD_VERSION="0.4.2"
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
    closing_completed=false
    if command -v tbd &> /dev/null && [[ "$(tbd --version 2>/dev/null || true)" == "$TBD_VERSION" ]]; then
      if tbd closing; then
        closing_completed=true
      fi
    elif command -v npx &> /dev/null; then
      if NPM_CONFIG_IGNORE_SCRIPTS=true npx --yes "get-tbd@$TBD_VERSION" closing; then
        closing_completed=true
      fi
    fi
    if [[ "$closing_completed" != true ]]; then
      echo "[tbd] Closing reminder skipped: tbd $TBD_VERSION and its pinned npx fallback were unavailable or failed." >&2
      echo "[tbd] Install it with: npm install -g get-tbd@$TBD_VERSION" >&2
    fi
  fi
fi

exit 0
