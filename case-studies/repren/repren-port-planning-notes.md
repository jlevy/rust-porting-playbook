# repren Case Study: Planning Notes

Planning notes for the second major case study of the Rust Porting Playbook: porting
[repren](https://github.com/jlevy/repren) (a bulk search/replace and file-rename CLI
tool) from Python to Rust.

**Date:** 2026-02-27

* * *

# Part 1: Generic Playbook Improvements

These improvements apply to **any** Python-to-Rust porting effort.
They should be implemented in the playbook before beginning the repren port itself.

## 1. Playbook Gap Summary

| Topic | Already in playbook | Gap size | Priority |
| --- | --- | --- | --- |
| **Regex: anchoring pitfall** | Good (3 files cover it) | None | — |
| **Regex: LazyLock compilation** | Good | None | — |
| **Regex: fancy-regex mention** | Adequate (3 places) | Small | Low |
| **Regex: flag mapping** | Not covered at all | **Large** | High |
| **Regex: replacement syntax (`\1` → `$1`)** | Not covered at all | **Large** | **Critical** |
| **Regex: Unicode behavior diffs** | Not covered at all | **Large** | High |
| **Regex: feature availability matrix** | Partial (look-arounds mentioned) | Medium | Medium |
| **Regex: perf model (NFA vs backtracking)** | Not covered | Medium | Medium |
| **Filesystem: basic I/O mapping** | 5 operations in mapping ref | Medium | Medium |
| **Filesystem: exhaustive operation mapping** | ~20 operations missing | **Large** | High |
| **Filesystem: atomic write pattern** | One minimal example | Medium | High |
| **Filesystem: backup/undo/collision patterns** | Not covered | **Large** | High |
| **Filesystem: directory walking patterns** | `walkdir` mentioned, no patterns | **Large** | High |
| **Filesystem: path manipulation patterns** | 3 operations, no ownership guidance | **Large** | High |
| **Filesystem: testing mutations** | Not covered | **Large** | High |
| **Pre-port test enhancement phase** | Implied but not formalized | **Large** | High |
| **Main playbook phase gates** | No test-sufficiency gate in Phase 1; no fast-path for Phase 2 | Medium | Medium |

* * *

## 2. Regex Behavior Mapping: Detailed Gap Analysis

### What the playbook already has

The playbook has decent but shallow regex coverage spread across three files:

- `references/python-to-rust-mapping-reference.md` lines 261-278: A function mapping
  table (`re.compile` → `Regex::new`, `re.match` → anchored `Regex`, etc.)
  with seven entries, plus the critical `re.match()` anchoring warning.
  Also mentions `fancy-regex` for look-ahead/behind.
- `guidelines/python-to-rust-porting-rules.md` lines 197-219: Repeats the anchoring
  pitfall with code examples for `re.match`, `re.search`, `re.fullmatch`.
- `guidelines/rust-general-rules.md` lines 141-160: `LazyLock` for compiled regex,
  anchoring warning, and “use `fancy-regex` only when needed.”
- `playbooks/python-to-rust-porting-guide.md` lines 592-596: Two sentences noting
  look-around and backreference differences.

### What’s missing

The playbook covers the “top 3 pitfalls” (anchoring, look-arounds, static compilation)
but is missing the full behavioral mapping that any regex-heavy port needs:

**a) Flag mapping (comprehensive)**

| Python | Rust (`regex` crate) | Notes |
| --- | --- | --- |
| `re.IGNORECASE` / `re.I` | `(?i)` inline or `RegexBuilder::case_insensitive(true)` | Equivalent |
| `re.DOTALL` / `re.S` | `(?s)` inline or `RegexBuilder::dot_matches_new_line(true)` | Equivalent |
| `re.MULTILINE` / `re.M` | `(?m)` inline or `RegexBuilder::multi_line(true)` | Equivalent — `^`/`$` match line boundaries |
| `re.VERBOSE` / `re.X` | `(?x)` inline or `RegexBuilder::ignore_whitespace(true)` | Equivalent |
| `re.ASCII` / `re.A` | `(?-u)` to disable Unicode | Rust `regex` is Unicode-aware by default |
| `re.UNICODE` / `re.U` | Default behavior | `regex` crate is Unicode by default |
| Combined flags `re.I \| re.S` | `(?is)` inline or chain builder methods |  |

**b) Replacement string syntax differences**

| Feature | Python `re.sub` | Rust `regex` `replace` |
| --- | --- | --- |
| Numbered backreference | `\1`, `\2` | `$1`, `$2` |
| Named backreference | `\g<name>` | `$name` or `${name}` |
| Literal `$` in replacement | N/A | `$$` |
| Literal `\` in replacement | `\\` | `\` (no special meaning) |
| Whole match | `\g<0>` | `$0` |

**c) Unicode behavior differences**

- Python `\w` matches Unicode by default in Python 3 (`re.UNICODE` is the default).
  Rust `regex` `\w` also matches Unicode by default.
  Same default — but ASCII-only mode differs: Python uses `re.ASCII`, Rust uses `(?-u)`.
- Python `\b` is Unicode-aware by default.
  Rust `\b` is also Unicode-aware by default.
- `\d` — Python: `[0-9]` with `re.ASCII`, Unicode digits otherwise.
  Rust: Unicode digits by default, `(?-u)\d` for ASCII-only.

**d) Feature availability differences**

| Feature | Python `re` | Rust `regex` | Rust `fancy-regex` |
| --- | --- | --- | --- |
| Positive lookahead `(?=...)` | Yes | No | Yes |
| Negative lookahead `(?!...)` | Yes | No | Yes |
| Positive lookbehind `(?<=...)` | Yes (fixed-width) | No | Yes |
| Negative lookbehind `(?<!...)` | Yes (fixed-width) | No | Yes |
| Backreferences `\1` in pattern | Yes | No | Yes |
| Atomic groups `(?>...)` | Yes (3.11+) | No | Yes |
| Possessive quantifiers `a++` | Yes (3.11+) | Yes | Yes |
| Conditional patterns `(?(id)yes\|no)` | Yes | No | Partial (group-based only) |

**e) Performance and compilation differences**

- Python: backtracking engine (can have catastrophic backtracking).
  Rust `regex`: Thompson NFA (guaranteed linear time, but some patterns like
  backreferences are unsupported).
  Rust `fancy-regex`: backtracking engine (like Python).
- Rust `regex` has a default compilation size limit (`RegexBuilder::size_limit()`).
  Complex patterns may hit this — increase with `size_limit()` if needed.

* * *

## 3. Filesystem Operations Mapping: Detailed Gap Analysis

### What the playbook already has

- `references/rust-cli-app-patterns.md` lines 148-173: A minimal `atomic_write()`
  example using `tempfile::NamedTempFile` + `persist()`, and a `write_with_backup()`
  snippet using `std::fs::copy` + `path.with_extension()`. Only covers the simplest
  scenario.
- `references/python-to-rust-mapping-reference.md` lines 225-238: Basic I/O mapping
  table (`open(path).read()` → `std::fs::read_to_string()`, `os.path.join` →
  `path.join()`, etc.). Five operations total.
- `references/rust-cli-best-practices.md` line 230: mentions `walkdir` and `tempfile` in
  a dependency list, no usage patterns.

### What’s missing

**a) Python → Rust filesystem operation mapping (exhaustive)**

| Python | Rust | Pitfalls |
| --- | --- | --- |
| `os.walk(dir)` | `walkdir::WalkDir::new(dir)` | Ordering differs; Python yields `(dirpath, dirnames, filenames)`, walkdir yields `DirEntry`; filtering differs |
| `os.rename(src, dst)` | `std::fs::rename(src, dst)?` | Cross-device moves fail; need manual copy+delete fallback |
| `shutil.copy2(src, dst)` | `std::fs::copy(src, dst)?` | Rust only copies content + permissions, not timestamps; need `filetime` crate |
| `shutil.rmtree(path)` | `std::fs::remove_dir_all(path)?` | Direct equivalent |
| `os.makedirs(path, exist_ok=True)` | `std::fs::create_dir_all(path)?` | Direct equivalent |
| `os.path.exists(path)` | `path.exists()` | Race condition in both; prefer `try` operations |
| `os.path.isfile(path)` | `path.is_file()` | Follows symlinks |
| `os.path.isdir(path)` | `path.is_dir()` | Follows symlinks |
| `os.path.islink(path)` | `path.is_symlink()` | Does NOT follow symlinks |
| `os.listdir(path)` | `std::fs::read_dir(path)?` | Returns `Result<DirEntry>` iterator |
| `os.path.getsize(path)` | `path.metadata()?.len()` | Use `symlink_metadata()` for symlinks |
| `os.stat(path)` | `std::fs::metadata(path)?` | Platform-specific field access |
| `os.chmod(path, mode)` | `std::fs::set_permissions(path, perms)?` | Unix-only; need `PermissionsExt` |
| `tempfile.NamedTemporaryFile()` | `tempfile::NamedTempFile::new()?` | Doesn’t auto-delete on drop |
| `os.path.abspath(path)` | `std::path::absolute(path)?` | Stable since Rust 1.79; does NOT resolve symlinks (unlike `canonicalize`) |
| `os.path.relpath(path, base)` | `pathdiff::diff_paths(path, base)` | Need `pathdiff` crate |
| `os.path.expanduser("~")` | `dirs::home_dir()` | Need `dirs` crate |
| `glob.glob("*.md")` | `glob::glob("*.md")?` | Need `glob` crate |

**b) Atomic file operation patterns beyond the basics**

- Atomic write-to-temp-then-rename with permission preservation
- Atomic rename with collision detection and numeric suffix generation
- Backup-then-modify with configurable suffix
- Undo: restore from backup with reverse rename
- Clean: find and remove backup files matching a suffix pattern
- Directory creation as side-effect of rename (creating parent dirs)

**c) Path manipulation patterns**

- `Path` vs `PathBuf` ownership (when to use which, borrowing patterns)
- Component-level path manipulation (replacing directory prefixes)
- Extension manipulation (`.with_extension()` only replaces the last extension; `.orig`
  appended to `foo.tar.gz` needs manual handling)
- Path comparison and canonicalization gotchas

**d) Directory walking patterns**

- Filtering during walk (vs filtering after collecting) — `walkdir` `filter_entry`
- Excluding patterns (dotfiles, backup files, specific directories)
- Preserving walk order for deterministic output
- Handling symlinks during walk (follow vs skip)

**e) Testing filesystem mutations**

- `tempfile::TempDir` for test isolation (auto-cleanup)
- Asserting file contents, permissions, and existence after operations
- Testing atomic write behavior (verify no partial writes on error)
- Testing rename collision behavior
- Testing backup/undo round-trips
- Snapshot-testing directory trees (listing + contents)

* * *

## 4. Pre-Port Test Enhancement Phase: Gap Analysis

The Flowmark case study assumed the Python project already had sufficient test coverage.
The current playbook’s Phase 1 says “measure test coverage” and Phase 5 says “port tests
first,” but there’s no explicit guidance for the scenario where the Python test suite
itself needs significant enhancement before porting can begin.

The playbook should formalize this as either a “Phase 0” or expand Phase 1 to include:

1. Measure current coverage quantitatively (pytest-cov)
2. Identify test gaps systematically
3. Enhance Python tests before porting (not during)
4. Migrate to tryscript format if applicable
5. Establish the golden test baseline that the Rust port must match

## 5. Main Playbook Phase Updates: Gap Analysis

**Phase 1 (Assess)** should include an explicit test-sufficiency gate: “Is the Python
test coverage sufficient to serve as a specification for the port?
If not, enhance before proceeding to Phase 2.”

**Phase 2 (Research)** should include a “fast-path” for low-dependency projects where
library evaluation is minimal (zero runtime deps means no library risk to evaluate).

* * *

## 6. Proposed Changes to Playbook Files

| Change | Target file | Type |
| --- | --- | --- |
| Expand regex section with flags, replacement syntax, Unicode, features, perf | `references/python-to-rust-mapping-reference.md` | Expand |
| Expand I/O section with exhaustive filesystem operation mapping | `references/python-to-rust-mapping-reference.md` | Expand |
| New guideline for filesystem-heavy CLI porting patterns | `guidelines/filesystem-heavy-cli-porting.md` | New file |
| Add pre-port test enhancement section | `playbooks/python-to-rust-test-coverage-playbook.md` | Expand |
| Add test-sufficiency gate to Phase 1 and fast-path to Phase 2 | `playbooks/python-to-rust-playbook.md` | Expand |

* * *

# Part 2: repren-Specific Case Study Material

## 7. repren: What It Is

repren is a powerful CLI tool for bulk string replacement and file/directory renaming.
It’s more sophisticated than `sed` or `perl -pie`:

- **Multi-pattern simultaneous replacement** — applies multiple patterns at once without
  interference between them
- **File and directory renaming** — apply patterns to file paths, creating directories
  as needed
- **Full regex support** — including capturing groups and backreferences (`\1`, `\2`)
- **Case-preserving “magic”** — transform all case variants simultaneously (lowerCamel,
  UpperCamel, lower_underscore, UPPER_UNDERSCORE)
- **Simultaneous swaps** — rename foo↔bar in a single pass
- **Atomic file operations** — temp file + rename, preventing corruption on interruption
- **Backup management** — automatic `.orig` backups with `--undo` and `--clean-backups`
- **JSON output** — machine-parseable output for agent/script integration
- **Zero runtime dependencies** — pure Python 3.10-3.14, stdlib only

### Source Code Structure

| File | Lines | Purpose |
| --- | --- | --- |
| `repren/repren.py` | ~1,637 | Monolithic main module: all core logic |
| `repren/claude_skill.py` | ~150 | Claude Code skill installation |
| `repren/markdown_renderer.py` | ~180 | Terminal ANSI markdown rendering |
| `repren/__init__.py` | ~15 | Package exports |
| **Total app code** | **~1,980** |  |

### Complexity Assessment

**High-complexity areas (will need careful testing):**
- `_sort_drop_overlaps()` — bisect-based algorithm for detecting/filtering overlapping
  pattern matches across simultaneous patterns
- `multi_replace()` — collect all matches across all patterns, apply simultaneously
  without conflicts
- `_split_name()` — detect naming conventions (CamelCase vs snake_case) and split into
  words, with Unicode support
- Case transformation pipeline — `_to_lower_camel`, `_to_upper_camel`,
  `_to_lower_underscore`, `_to_upper_underscore`
- Atomic file operations — temp file creation, backup management, rename collision
  handling with numeric suffixes
- Pattern parsing — comments, escape sequences, case variants, word breaks

**Moderate-complexity areas:**
- Regex compilation with flags (IGNORECASE, DOTALL, literal mode, word breaks)
- Stream vs at-once processing modes
- Undo logic — reverse renames using patterns, validate timestamps
- CLI argument parsing with custom error handling and early-exit modes

* * *

## 8. Current Test Coverage

### Unit Tests (pytest): ~50 test functions

`tests/pytests.py` (847 lines) covers:

- **Case transformation:** `test_split_name`, `test_to_lower_camel`,
  `test_to_upper_camel`, `test_to_lower_underscore`, `test_to_upper_underscore` —
  including Unicode (German, Cyrillic, Greek, Chinese, Japanese)
- **Backup file filtering:** `TestWalkFilesBackupSuffix` class
- **Backup suffix validation:** `TestBackupSuffixValidation`
- **Backup management:** `TestFindBackupFiles`, `TestUndoBackups`, `TestCleanBackups`
- **Multi-replace core logic:** `TestMultiReplace` — overlapping patterns, capturing
  groups, empty input, Unicode
- **Overlap detection:** `TestSortDropOverlaps` — nested and overlapping matches
- **Claude Skill integration:** `TestClaudeSkillContent`, `TestClaudeSkillInstallation`,
  `TestClaudeSkillCLI`
- **CLI invocation tests** via subprocess

### Golden Tests (bash): ~40 test scenarios

`tests/golden-tests.sh` (381 lines) with `tests/run.sh` harness covers text
replacements, file renames, full mode, pattern files, case preservation, word-break
mode, include/exclude, file moves, undo/restore, clean-backups, custom suffixes, JSON
output, regex capturing groups, literal mode, at-once mode, parse-only, stdin/stdout,
quiet mode, error cases, skill installation, and file collision handling.

### Identified Test Gaps

1. Permission/access edge cases — read-only files, read-only directories, symlinks
2. Encoding edge cases — mixed encodings, invalid UTF-8, binary files
3. Large-scale stress — very large files, thousands of files, deep directory nesting
4. Regex edge cases — catastrophic backtracking, deeply nested groups
5. Filesystem edge cases — race conditions, concurrent runs, circular symlinks
6. Empty/degenerate inputs — empty patterns, patterns matching empty string
7. CLI argument conflicts — more invalid combinations
8. Special characters in paths — spaces, quotes, control characters
9. Platform-specific — line endings (\r\n vs \n), case-insensitive filesystems
10. Backup/undo edge cases — multiple backups for same file, partial undo

* * *

## 9. Comparison with Flowmark Case Study

| Aspect | Flowmark | repren |
| --- | --- | --- |
| **Type** | CLI tool | CLI tool |
| **Python LOC** | ~4,250 app code | ~1,980 app code |
| **Runtime deps** | Several (markdown parser) | Zero (stdlib only) |
| **Library risk** | HIGH — parser differences dominated effort | LOW — no external parser |
| **Filesystem complexity** | Simple (read → write) | Complex (write + rename + backup + undo) |
| **State management** | Stateless | Stateful (backup tracking, collision numbering) |
| **Mode count** | ~3 modes | ~8 modes |

**Implications:** Library risk is low (inverting Flowmark’s risk profile); filesystem
complexity is the main risk area.
Regex behavior differences will need careful testing but are more tractable than parser
differences.

* * *

## 10. repren Phased Implementation Plan

### Phase 0: Test Enhancement

Measure baseline coverage, migrate golden tests to tryscript, expand pytest suite,
target 90%+ line coverage.

### Phase 1-2: Assess and Research (abbreviated)

Codebase metrics, zero-dependency analysis, `regex` + `clap` + `tempfile` + `walkdir`
evaluation. Proof-of-concept: verify regex behavior equivalence.

### Phase 3-7: Plan → Port → Fix → Finalize

Standard playbook phases.
Key risk area is filesystem operations (Phase 5-6).

### Phase 8: Sync

Will apply once Python codebase is updated post-port.

* * *

## 11. Case Study Artifact Plan

```
case-studies/repren/
├── README.md
├── repren-port-planning-notes.md         ← This document
├── repren-port-observations.md           ← (during porting)
├── repren-port-analysis.md               ← (post-port)
├── repren-port-library-choices.md        ← (likely brief)
├── repren-port-decision-log.md           ← (post-port)
├── repren-port-metrics.md                ← (post-port)
└── repren-port-cross-validation.md       ← (post-port)
```
