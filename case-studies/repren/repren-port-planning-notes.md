# RepRen Case Study: Planning Notes

Planning notes for the second major case study of the Rust Porting Playbook: porting
[repren](https://github.com/jlevy/repren) (a bulk search/replace and file-rename CLI
tool) from Python to Rust.

**Date:** 2026-02-27

---

## 1. RepRen: What It Is

RepRen is a powerful CLI tool for bulk string replacement and file/directory renaming.
It's more sophisticated than `sed` or `perl -pie`:

- **Multi-pattern simultaneous replacement** — applies multiple patterns at once without
  interference between them
- **File and directory renaming** — apply patterns to file paths, creating directories as
  needed
- **Full regex support** — including capturing groups and backreferences (`\1`, `\2`)
- **Case-preserving "magic"** — transform all case variants simultaneously
  (lowerCamel, UpperCamel, lower_underscore, UPPER_UNDERSCORE)
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
| **Total app code** | **~1,980** | |

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

---

## 2. Current Test Coverage

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

`tests/golden-tests.sh` (381 lines) with `tests/run.sh` harness:

- Text replacements (no renames)
- File renames only
- Full replacements + renames
- Pattern files with multiple patterns
- Case preservation with rotations
- Word-break mode
- Include/exclude patterns
- File moving across directories
- Undo/restore functionality
- Clean-backups mode
- Custom backup suffixes
- JSON output format
- Regex with capturing groups
- Literal mode (non-regex)
- At-once mode (multiline patterns)
- Parse-only mode
- Stdin/stdout mode
- Quiet mode
- Error cases with invalid regex
- Skill installation (global and project-local)
- File collision handling with numeric suffixes

**Expected baseline:** `golden-tests-expected.log` (901 lines)

### What's Good About Current Tests

- Two-tier approach (unit + golden integration) is solid
- Golden tests cover the full CLI surface area
- Unicode support is tested in unit tests
- The golden test harness with output normalization (perl-based) handles timestamps,
  line numbers, paths

### Identified Test Gaps

1. **Permission/access edge cases** — read-only files, read-only directories, symlinks
2. **Encoding edge cases** — mixed encodings, invalid UTF-8, binary files
3. **Large-scale stress** — very large files, thousands of files, deep directory nesting
4. **Regex edge cases** — catastrophic backtracking, deeply nested groups
5. **Filesystem edge cases** — race conditions, concurrent runs, circular symlinks
6. **Empty/degenerate inputs** — empty patterns, patterns matching empty string
7. **CLI argument conflicts** — more invalid combinations
8. **Special characters in paths** — spaces, quotes, control characters
9. **Platform-specific** — line endings (\r\n vs \n), case-insensitive filesystems
10. **Backup/undo edge cases** — multiple backups for same file, partial undo

---

## 3. Testing Enhancement Strategy: Phase 1

### 3.1 The Key Insight: RepRen Already Has "Proto-Tryscript" Golden Tests

RepRen's `golden-tests.sh` is essentially a hand-written bash predecessor to tryscript.
It captures CLI commands and their output, normalizes non-deterministic elements, and
compares against a committed baseline. This is exactly what tryscript formalizes.

**The migration path is clear:**
1. Each test scenario in `golden-tests.sh` maps directly to a tryscript test section
2. The output normalization (timestamps, paths, line numbers) maps to tryscript's
   `patterns:` frontmatter
3. The test fixtures (`tests/work-dir/original/`) can be set up in tryscript's `before:`
   block
4. Error-case testing (`expect_error`) maps to tryscript's `? N` exit code syntax

### 3.2 Tryscript Format Reference (from Flowmark)

Flowmark's `cli-golden.tryscript.md` demonstrates the canonical pattern:

```markdown
---
sandbox: true
env:
  NO_COLOR: "1"
path:
  - $TRYSCRIPT_GIT_ROOT/.venv/bin
patterns:
  VERSION: 'v\d+\.\d+\.\S+'
before: |
  mkdir -p some/dir
  printf '...' > file.txt
---

# Test Suite Name

## Test Section Name

\`\`\`console
$ command --flag argument
expected output here
\`\`\`

## Error Cases

\`\`\`console
$ command --bad-flag 2>&1
Error: expected error message
? 1
\`\`\`
```

### 3.3 Migration Plan: golden-tests.sh → tryscript

**Proposed tryscript files for RepRen:**

| File | Coverage |
| --- | --- |
| `tests/golden/basic-replacements.tryscript.md` | Text replacements (no renames), dry-run, case sensitivity |
| `tests/golden/file-renames.tryscript.md` | File/directory renaming, collision handling |
| `tests/golden/full-mode.tryscript.md` | Combined replacements + renames |
| `tests/golden/pattern-files.tryscript.md` | Multi-pattern files, swaps, aliases |
| `tests/golden/case-preservation.tryscript.md` | Case-preserving mode, rotations |
| `tests/golden/regex-features.tryscript.md` | Capturing groups, literal mode, word breaks, at-once, dotall |
| `tests/golden/file-discovery.tryscript.md` | Include/exclude patterns, walk-only |
| `tests/golden/backup-management.tryscript.md` | Undo, clean-backups, custom suffixes |
| `tests/golden/json-output.tryscript.md` | JSON output format for all operations |
| `tests/golden/stdin-stdout.tryscript.md` | Pipe/stdin/stdout mode |
| `tests/golden/error-handling.tryscript.md` | Invalid regex, missing args, bad options |
| `tests/golden/edge-cases.tryscript.md` | Unicode, special chars, empty files, large inputs |

**New fixtures to add (beyond current `work-dir/original/`):**

- Unicode text files (CJK, Cyrillic, emoji, mixed scripts)
- Files with special characters in names (spaces, brackets)
- Binary files (to test skip behavior)
- Deeply nested directory structures
- Files with different line endings
- Large files (for at-once mode stress)
- Pattern files with edge cases (empty lines, comment-only, unicode patterns)

### 3.4 Tryscript Frontmatter for RepRen

```yaml
---
sandbox: true
env:
  NO_COLOR: "1"
path:
  - $TRYSCRIPT_GIT_ROOT/.venv/bin
patterns:
  TIMESTAMP: '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
  PATH_PREFIX: '__TESTDIR__'
before: |
  # Set up test fixtures
  mkdir -p original/stuff/trees original/stuff/words
  printf 'Humpty Dumpty smiled ...' > original/humpty-dumpty.txt
  # ... (recreate the full fixture set)
---
```

### 3.5 Enhanced Unit Tests to Add (pytest)

Beyond the tryscript migration, we should expand the pytest suite:

**Core algorithm tests:**
- More overlap detection scenarios (adjacent matches, zero-width matches)
- Multi-replace with patterns that produce output matching other patterns
- Case transformation with more Unicode edge cases (Turkish İ/i, German ß)
- Pattern parsing with malformed input (tabs in wrong places, unicode escapes)

**File operation tests:**
- Atomic write verification (interrupt simulation)
- Backup collision handling (multiple `.orig` files)
- Directory creation for nested renames
- Permission preservation after rewrite

**CLI argument validation:**
- All mutually exclusive option combinations
- Long paths, special characters in arguments
- Mixed stdin and file arguments

**Estimated new tests: ~30-50 additional pytest functions**

---

## 4. Comparison with Flowmark Case Study

### Similarities

| Aspect | Flowmark | RepRen |
| --- | --- | --- |
| **Type** | CLI tool | CLI tool |
| **Domain** | Markdown formatting | Bulk search/replace & rename |
| **Python LOC** | ~4,400 app code | ~1,980 app code |
| **Runtime deps** | Several (markdown parser) | Zero (stdlib only) |
| **Test approach** | pytest + golden tests | pytest + bash golden tests |
| **CLI complexity** | Moderate | Moderate-high (more modes) |
| **File I/O** | Read → transform → write | Read → transform → write (+ rename) |

### Key Differences

| Aspect | Flowmark | RepRen |
| --- | --- | --- |
| **Parsing** | Depends on markdown parser (comrak) | Self-contained regex engine |
| **Library risk** | HIGH — parser behavior differences dominated effort | LOW — no external parser |
| **File mutations** | Writes formatted output | Writes + renames + backs up + undoes |
| **Filesystem complexity** | Simple (read file, write file) | Complex (atomic ops, renames, directory creation, backups, undo) |
| **State management** | Stateless (each file independent) | Stateful (backup tracking, collision numbering) |
| **Mode count** | ~3 modes (stdin, auto, list-files) | ~8 modes (replace, rename, full, undo, clean, parse-only, walk-only, stdin) |

### Implications for the Port

1. **Library risk is LOW** — RepRen doesn't depend on an external parser whose behavior
   might differ between Python and Rust. The `regex` crate in Rust is mature and
   well-documented. This means Phase 2 (Research & Library Evaluation) will be simpler
   than Flowmark's.

2. **Filesystem complexity is HIGH** — The backup management, undo, atomic writes, and
   file renaming logic is the main complexity center. This is where most Rust-specific
   challenges will emerge (ownership, error handling for I/O, path manipulation).

3. **Regex behavior differences** — Python's `re` module and Rust's `regex` crate have
   subtle differences (Unicode handling, lookahead support, flag syntax). This will need
   careful testing but is more tractable than parser differences.

4. **Testing is more critical** — Because RepRen modifies the filesystem (renames,
   backups, directory creation), testing needs to be more comprehensive than Flowmark's.
   The filesystem operations are the primary risk area for behavioral divergence.

---

## 5. How This Adapts the Playbook

### What Applies Directly (No Changes Needed)

- **8-phase methodology** — The phases (assess, research, plan, setup, port, fix,
  finalize, sync) apply cleanly
- **Tests-as-specification** — The golden test suite IS the specification for RepRen
- **Cross-validation approach** — Run both Python and Rust against same inputs, diff
  outputs
- **Workaround tracking** — Structured labels for any behavioral differences
- **Test mapping** — YAML-based cross-language test mapping applies directly
- **Guidelines** — `rust-general-rules`, `rust-cli-app-patterns`, `rust-project-setup`
  all apply

### What Needs Adaptation or Addition

#### 5.1 Pre-Port Test Enhancement Phase (NEW)

The Flowmark case study assumed the Python project already had sufficient test coverage.
RepRen has decent coverage but needs enhancement before porting. The playbook should
formalize a **Phase 0: Test Enhancement** or expand Phase 1 (Assess) to include:

1. Measure current coverage quantitatively (pytest-cov)
2. Identify test gaps systematically
3. Enhance Python tests before porting (not during)
4. Migrate to tryscript format if applicable
5. Establish the golden test baseline that the Rust port must match

**This is the most significant playbook addition this case study reveals.**

The current playbook's Phase 1 says "measure test coverage" and Phase 5 says
"port tests first," but there's no explicit guidance for the scenario where the Python
test suite itself needs significant enhancement before porting can begin.

#### 5.2 Tryscript Migration Guidance (ADD)

The playbook references tryscript but doesn't provide a migration path from existing
bash-based golden tests. A new section should cover:

- When to migrate (existing bash golden tests → tryscript)
- How to structure tryscript files for a CLI tool
- Frontmatter patterns for output normalization
- Fixture management in tryscript `before:` blocks vs external files
- Running tryscript in CI

This is directly informed by RepRen's migration from `golden-tests.sh` to tryscript.

#### 5.3 Filesystem-Heavy CLI Patterns (ADD)

The Flowmark case study was "read → transform → write." RepRen is
"read → transform → write + rename + backup + undo." The playbook needs significantly
more guidance for porting filesystem-mutation-heavy CLIs.

**What the playbook already has:**

- `guidelines/rust-cli-app-patterns.md` lines 148-173: A minimal `atomic_write()` example
  using `tempfile::NamedTempFile` + `persist()`, and a `write_with_backup()` snippet
  using `std::fs::copy` + `path.with_extension()`. These are the right primitives but
  cover only the simplest scenario (one file, one backup extension).
- `playbooks/python-to-rust-mapping-reference.md` lines 225-238: Basic I/O mapping table
  (`open(path).read()` → `std::fs::read_to_string()`, `os.path.join` → `path.join()`,
  etc.). Only covers read/write/exists/parent/join — five operations total.
- `playbooks/rust-cli-best-practices.md` line 230: mentions `walkdir` and `tempfile` in a
  dependency list, no usage patterns.

**What's missing — the gap is large:**

A comprehensive filesystem operations mapping reference should cover all of the following.
Very little of this is in the playbook today:

**a) Python → Rust filesystem operation mapping (exhaustive)**

| Python | Rust | Pitfalls |
| --- | --- | --- |
| `os.walk(dir)` | `walkdir::WalkDir::new(dir)` | Ordering differs; Python yields `(dirpath, dirnames, filenames)`, walkdir yields `DirEntry`; filtering must happen differently |
| `os.rename(src, dst)` | `std::fs::rename(src, dst)?` | Cross-device moves fail in both; Python's `shutil.move()` handles this, Rust needs manual copy+delete fallback |
| `shutil.copy2(src, dst)` | `std::fs::copy(src, dst)?` | Rust `copy` only copies content + permissions, not timestamps; need `filetime` crate for full metadata preservation |
| `shutil.rmtree(path)` | `std::fs::remove_dir_all(path)?` | Direct equivalent but no trash/recycle bin support |
| `os.makedirs(path, exist_ok=True)` | `std::fs::create_dir_all(path)?` | Direct equivalent |
| `os.path.exists(path)` | `path.exists()` | Race condition in both; prefer `try` operations |
| `os.path.isfile(path)` | `path.is_file()` | Follows symlinks in both |
| `os.path.isdir(path)` | `path.is_dir()` | Follows symlinks in both |
| `os.path.islink(path)` | `path.is_symlink()` | Does NOT follow symlinks |
| `os.listdir(path)` | `std::fs::read_dir(path)?` | Rust returns `Result<DirEntry>` iterator |
| `os.path.getsize(path)` | `path.metadata()?.len()` | Follows symlinks; use `symlink_metadata()` for symlinks |
| `os.stat(path)` | `std::fs::metadata(path)?` | Different field names, platform-specific extensions |
| `os.chmod(path, mode)` | `std::fs::set_permissions(path, perms)?` | Unix-only for mode bits; need `std::os::unix::fs::PermissionsExt` |
| `tempfile.NamedTemporaryFile()` | `tempfile::NamedTempFile::new()?` | Rust version doesn't auto-delete on drop by default (use `tempfile()` for that) |
| `os.path.abspath(path)` | `std::fs::canonicalize(path)?` | Rust resolves symlinks too! Use `std::path::absolute()` (nightly) or manual resolution for no-symlink-resolve |
| `os.path.relpath(path, base)` | `pathdiff::diff_paths(path, base)` | Not in stdlib; need `pathdiff` crate |
| `os.path.expanduser("~")` | `dirs::home_dir()` | Need `dirs` crate |
| `glob.glob("*.md")` | `glob::glob("*.md")?` | Need `glob` crate |

**b) Atomic file operation patterns beyond the basics**

- Atomic write-to-temp-then-rename with permission preservation
- Atomic rename with collision detection and numeric suffix generation
  (RepRen's `_rename_file()` does `foo.txt` → `foo.txt.1` → `foo.txt.2`)
- Backup-then-modify with configurable suffix
- Undo: restore from backup with reverse rename
- Clean: find and remove backup files matching a suffix pattern
- Directory creation as side-effect of rename (creating parent dirs)

**c) Path manipulation patterns**

- `Path` vs `PathBuf` ownership (when to use which, borrowing patterns)
- Component-level path manipulation (replacing directory prefixes, which RepRen
  does for rename-based file moves)
- Cross-platform path separator handling
- Extension manipulation (`.with_extension()` only replaces the last extension;
  `.orig` appended to `foo.tar.gz` needs manual handling)
- Path comparison and canonicalization gotchas

**d) Directory walking patterns**

- Filtering during walk (vs filtering after collecting) — `walkdir` filter_entry
- Excluding patterns (dotfiles, backup files, specific directories)
- Preserving walk order for deterministic output
- Handling symlinks during walk (follow vs skip)
- Concurrency-safe walking (files may appear/disappear)

**e) Testing filesystem mutations**

- `tempfile::TempDir` for test isolation (auto-cleanup)
- Asserting file contents, permissions, and existence after operations
- Testing atomic write behavior (verify no partial writes on error)
- Testing rename collision behavior
- Testing backup/undo round-trips
- Snapshot-testing directory trees (listing + contents)

#### 5.4 Zero-Dependency Ports (CLARIFY)

The playbook's Phase 2 (Research & Library Evaluation) is heavily weighted toward library
selection because Flowmark's parser choice dominated effort. For RepRen, there are no
major library decisions — just `regex` + `clap` + `tempfile`. The playbook should
clarify:

- When Phase 2 can be abbreviated (zero/low dependency projects)
- Minimum library evaluation checklist even for simple cases
- Focus areas when library risk is low (shift effort to filesystem/edge-case testing)

#### 5.5 Case Study Observations Template Updates (MINOR)

The observations template should include:

- A section for "pre-port test enhancement observations" (what gaps were found, how
  they were filled)
- A field for "original test framework" → "target test framework" migration notes
- Space for documenting tryscript migration decisions

#### 5.6 Regex Behavior Mapping (ADD)

**What the playbook already has:**

The playbook has decent but shallow regex coverage spread across three files:

- `playbooks/python-to-rust-mapping-reference.md` lines 261-278: A function mapping
  table (`re.compile` → `Regex::new`, `re.match` → anchored `Regex`, etc.) with seven
  entries, plus the critical `re.match()` anchoring warning. Also mentions `fancy-regex`
  for look-ahead/behind.
- `guidelines/python-to-rust-porting-rules.md` lines 197-219: Repeats the anchoring
  pitfall with code examples for `re.match`, `re.search`, `re.fullmatch`.
- `guidelines/rust-general-rules.md` lines 141-160: `LazyLock` for compiled regex,
  anchoring warning, and "use `fancy-regex` only when needed."
- `playbooks/python-to-rust-porting-guide.md` lines 592-596: Two sentences noting
  look-around and backreference differences.

**What's missing — the gap is moderate but important for regex-heavy projects:**

The playbook covers the "top 3 pitfalls" (anchoring, look-arounds, static compilation)
but is missing the full behavioral mapping that a regex-centric port like RepRen needs.
The ideal reference would additionally cover:

**a) Flag mapping (comprehensive)**

| Python | Rust (`regex` crate) | Notes |
| --- | --- | --- |
| `re.IGNORECASE` / `re.I` | `(?i)` inline or `RegexBuilder::case_insensitive(true)` | Equivalent |
| `re.DOTALL` / `re.S` | `(?s)` inline or `RegexBuilder::dot_matches_new_line(true)` | Equivalent |
| `re.MULTILINE` / `re.M` | `(?m)` inline or `RegexBuilder::multi_line(true)` | Equivalent — `^`/`$` match line boundaries |
| `re.VERBOSE` / `re.X` | `(?x)` inline or `RegexBuilder::ignore_whitespace(true)` | Equivalent |
| `re.ASCII` / `re.A` | Default behavior in `regex` crate | Rust `regex` is Unicode-aware by default; use `(?-u)` to disable |
| `re.UNICODE` / `re.U` | Default behavior | `regex` crate is Unicode by default |
| Combined flags `re.I \| re.S` | `(?is)` inline or chain builder methods | |

**Not in playbook at all today.**

**b) Unicode behavior differences**

- Python `\w` matches `[a-zA-Z0-9_]` by default (ASCII), or Unicode with `re.UNICODE`
  (default in Python 3). Rust `regex` `\w` matches Unicode by default. This is the same
  default, but the ASCII-only mode differs: Python uses `re.ASCII`, Rust uses `(?-u)`.
- Python `\b` is Unicode-aware by default. Rust `\b` is also Unicode-aware by default.
  But when porting patterns that were specifically ASCII-only (`re.ASCII`), need `(?-u)\b`.
- `\d` — Python: `[0-9]` with `re.ASCII`, Unicode digits otherwise. Rust: Unicode
  digits by default, `(?-u)\d` for ASCII-only.

**Not in playbook at all today.**

**c) Replacement string syntax differences**

| Feature | Python `re.sub` | Rust `regex` `replace` |
| --- | --- | --- |
| Numbered backreference | `\1`, `\2` | `$1`, `$2` |
| Named backreference | `\g<name>` | `$name` or `${name}` |
| Literal `$` in replacement | N/A | `$$` |
| Literal `\` in replacement | `\\` | `\` (no special meaning) |
| Whole match | `\g<0>` | `$0` |
| Empty capture fallback | Empty string | Empty string |

**This is critical for RepRen** since it uses `\1`, `\2` backreferences extensively.
The port must translate all replacement strings from `\N` to `$N` syntax.
**Not in playbook at all today.**

**d) Capturing group differences**

- Python: `(?P<name>...)` for named groups. Rust: `(?P<name>...)` (same!) or
  `(?<name>...)` (shorter form).
- Python: `match.group(0)` for whole match, `match.group(1)` for first capture.
  Rust: `caps.get(0)` / `caps.get(1)` returning `Option<Match>`.
- Python: `re.findall()` with groups returns list of group tuples.
  Rust: `regex.captures_iter()` returns `Captures` objects (different API shape).

**Partially in playbook** (mapping reference has `match.group(0)` → `m.as_str()`,
`match.group(1)` → `caps.get(1).map(|m| m.as_str())`), but missing the `findall`
with groups behavior difference and named group syntax.

**e) Feature availability differences**

| Feature | Python `re` | Rust `regex` | Rust `fancy-regex` |
| --- | --- | --- | --- |
| Positive lookahead `(?=...)` | Yes | No | Yes |
| Negative lookahead `(?!...)` | Yes | No | Yes |
| Positive lookbehind `(?<=...)` | Yes (fixed-width) | No | Yes |
| Negative lookbehind `(?<!...)` | Yes (fixed-width) | No | Yes |
| Backreferences `\1` in pattern | Yes | No | Yes |
| Atomic groups `(?>...)` | No | Yes | Yes |
| Possessive quantifiers `a++` | No | Yes | Yes |
| Conditional patterns `(?(id)yes\|no)` | Yes | No | No |

**Partially in playbook** (mentions look-arounds and `fancy-regex` but not the full
matrix or the availability of conditional patterns).

**f) Performance and compilation differences**

- Python: regex compilation is relatively slow; common to pre-compile with
  `re.compile()`. Rust `regex`: compilation is also expensive; use `LazyLock` for statics
  (covered in playbook).
- Python: no compilation size limits. Rust `regex`: has a default size limit
  (`RegexBuilder::size_limit()`). Complex patterns may hit this.
- Python: backtracking engine (can have catastrophic backtracking). Rust `regex`:
  Thompson NFA (guaranteed linear time, but some patterns are unsupported).
  Rust `fancy-regex`: backtracking (can have catastrophic backtracking, like Python).

**Partially in playbook** (`LazyLock` covered), but the size limit and
linear-time-vs-backtracking distinction is not mentioned anywhere.

---

## 6. Phased Implementation Plan

### Phase 0: Test Enhancement (CURRENT PRIORITY)

**Goal:** Make the Python test suite comprehensive enough to serve as the specification
for the Rust port.

**Step 0.1:** Measure baseline coverage
```bash
cd attic/repren
uv run pytest --cov=repren --cov-branch --cov-report=html tests/pytests.py
```

**Step 0.2:** Write tryscript golden tests
- Migrate all 40+ scenarios from `golden-tests.sh` into structured `.tryscript.md` files
- Add new scenarios for identified test gaps
- Target: 80+ tryscript test scenarios across 12 files

**Step 0.3:** Expand pytest unit tests
- Add ~30-50 new test functions for identified gaps
- Focus on: overlap detection edge cases, Unicode edge cases, filesystem operation
  correctness
- Target: 80+ total pytest functions

**Step 0.4:** Verify and document
- Run full test suite, ensure 100% pass
- Measure final coverage (target: 90%+ line, 80%+ branch)
- Document the test enhancement as part of the case study observations

### Phase 1: Assess (playbook Phase 1)

- Codebase metrics (LOC, complexity)
- Dependency analysis (trivial for RepRen — zero runtime deps)
- Test coverage report (from Phase 0)
- Go/no-go decision (should be straightforward go)

### Phase 2: Research (playbook Phase 2 — abbreviated)

Key decisions:
- `regex` crate (vs `fancy-regex` for lookahead if needed)
- `clap` for CLI parsing
- `tempfile` for atomic operations
- `walkdir` for directory traversal
- Proof-of-concept: verify regex behavior equivalence for RepRen's pattern set

### Phase 3-7: Plan → Port → Fix → Finalize

Standard playbook phases apply. The key risk area is filesystem operations (Phase 5-6),
not library behavior (which dominated Flowmark).

### Phase 8: Sync

Will apply once RepRen's Python codebase is updated post-port.

---

## 7. Playbook Gap Summary and Proposed Changes

### Current state of coverage, by topic

| Topic | Already in playbook | Gap size | Priority |
| --- | --- | --- | --- |
| **Regex: anchoring pitfall** | Good (3 files cover it) | None | — |
| **Regex: LazyLock compilation** | Good | None | — |
| **Regex: fancy-regex mention** | Adequate (mentioned in 3 places) | Small | Low |
| **Regex: flag mapping** | Not covered at all | **Large** | High |
| **Regex: replacement syntax (`\1` → `$1`)** | Not covered at all | **Large** | **Critical** for RepRen |
| **Regex: Unicode behavior diffs** | Not covered at all | **Large** | High |
| **Regex: feature availability matrix** | Partial (look-arounds mentioned) | Medium | Medium |
| **Regex: perf model (NFA vs backtracking)** | Not covered | Medium | Medium |
| **Filesystem: basic I/O mapping** | 5 operations in mapping ref | Medium | Medium |
| **Filesystem: exhaustive operation mapping** | Not covered (~20 operations missing) | **Large** | High |
| **Filesystem: atomic write pattern** | One minimal example | Medium | High |
| **Filesystem: backup/undo/collision patterns** | Not covered | **Large** | **Critical** for RepRen |
| **Filesystem: directory walking patterns** | `walkdir` mentioned, no patterns | **Large** | High |
| **Filesystem: path manipulation patterns** | 3 operations, no ownership guidance | **Large** | High |
| **Filesystem: testing mutations** | Not covered | **Large** | High |
| **Pre-port test enhancement phase** | Implied but not formalized | **Large** | High |
| **Tryscript migration from bash golden tests** | Not covered | Medium | Medium |

### Proposed additions to the playbook

**1. Expand existing: `playbooks/python-to-rust-mapping-reference.md`**

The Regex section (currently 15 lines) should be expanded to ~80 lines covering:
- Flag mapping table (6 flags)
- Replacement string syntax differences (critical: `\1` → `$1`)
- Unicode behavior differences (`\w`, `\b`, `\d` defaults)
- Feature availability matrix (which features need `fancy-regex`)
- Compilation/performance model differences

The I/O section (currently 10 lines) should be expanded to ~60 lines covering:
- Full filesystem operation mapping (~20 operations)
- Path manipulation patterns with ownership guidance
- Missing crate recommendations (`walkdir`, `pathdiff`, `dirs`, `filetime`)

**2. New guideline: `guidelines/filesystem-heavy-cli-porting.md`**

Compact (~2-3k tokens) guideline focused on patterns for porting CLIs that heavily
mutate the filesystem. Should cover:
- Atomic write patterns (beyond the single existing example)
- Backup management (create, find, restore, clean)
- Rename with collision handling
- Directory walking with filtering
- Testing filesystem mutations (tempdir isolation, assertions)
- Cross-platform considerations (permissions, symlinks, line endings)

**3. Expand existing: `playbooks/python-to-rust-test-coverage-playbook.md`**

Add a section on pre-port test enhancement (Phase 0 concept):
- When existing Python test coverage is insufficient
- How to identify and fill gaps before porting
- Tryscript migration from bash golden tests (when applicable)

**4. Expand existing: `playbooks/python-to-rust-playbook.md`**

Phase 1 (Assess) should include an explicit gate: "Is the Python test coverage sufficient
to serve as a specification? If not, enhance before proceeding."

Phase 2 (Research) should include a "fast-path" for low-dependency projects where library
evaluation is minimal.

**5. Case study: `case-studies/repren/`**

Full artifact set mirroring Flowmark's structure.

### Validation

The RepRen case study will validate:
- Whether the 8-phase methodology works for a filesystem-heavy, zero-dependency CLI
- Whether the pre-port test enhancement phase is worth formalizing
- Whether tryscript migration guidance is generalizable
- Whether the playbook's library-evaluation-heavy approach needs rebalancing for simple
  dependency profiles
- Whether the regex and filesystem mapping expansions are sufficient

---

## 8. Case Study Artifact Plan

Mirror Flowmark's structure:

```
case-studies/repren/
├── README.md
├── repren-port-planning-notes.md         ← This document
├── repren-port-observations.md           ← (Phase A.3: during porting)
├── repren-port-analysis.md               ← (Phase A.4: post-port)
├── repren-port-library-choices.md        ← (Phase A.4: likely brief)
├── repren-port-decision-log.md           ← (Phase A.4: post-port)
├── repren-port-metrics.md                ← (Phase A.5: post-port)
└── repren-port-cross-validation.md       ← (Phase A.4: post-port)
```

---

## 9. Summary of Key Insights

1. **RepRen is an excellent second case study** — it's a CLI tool (same domain as
   Flowmark) but with fundamentally different complexity profile: filesystem-heavy,
   zero-dependency, regex-centric. This will stress-test different parts of the playbook.

2. **Phase 1 should focus on test enhancement and tryscript migration** — the existing
   bash golden tests are a direct predecessor to tryscript. Migrating them provides both
   better tooling and more extensible test infrastructure for the port.

3. **The playbook needs a "Phase 0: Test Enhancement" concept** — this is the biggest
   structural addition. The current playbook assumes adequate Python tests exist.

4. **Library risk is low, filesystem risk is high** — this inverts Flowmark's risk
   profile. The playbook's heavy emphasis on library evaluation (Phase 2) needs a
   "fast-path" for simple dependency profiles.

5. **Regex behavior mapping is a gap** — the playbook doesn't currently cover Python
   `re` → Rust `regex` differences, which RepRen will surface directly.

6. **The golden test migration is a reusable pattern** — many Python CLIs have
   bash-based golden tests. A formalized migration guide to tryscript would benefit
   future case studies too.

7. **RepRen's monolithic structure simplifies porting** — the single 1,637-line file
   means there's no complex module dependency graph to navigate. The porting order is
   straightforward: core algorithms → file operations → CLI → integration.
