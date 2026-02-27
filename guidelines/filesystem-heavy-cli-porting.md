---
title: Filesystem-Heavy CLI Porting
description: Patterns for porting Python CLIs that heavily mutate the filesystem — atomic writes, backups, renames, directory walking, and testing
---
# Filesystem-Heavy CLI Porting

Patterns for porting Python CLIs that perform significant filesystem mutations:
file renames, backups, undo, atomic writes, directory walking with filtering.
These patterns go beyond the simple read-transform-write cycle covered in the general
CLI patterns guide.

See also: [Rust CLI App Patterns](rust-cli-app-patterns.md),
[Python-to-Rust Mapping Reference](../playbooks/python-to-rust-mapping-reference.md)
(I/O section).

## Atomic File Writes

Always write to a temp file and atomically rename, never write in-place.
Use `tempfile::NamedTempFile` — the temp file MUST be on the same filesystem as the
target (`persist()` uses the OS `rename` syscall, which fails across mount points).

```rust
use std::io::Write;
use std::path::Path;
use tempfile::NamedTempFile;

fn atomic_write(path: &Path, content: &[u8]) -> anyhow::Result<()> {
    let dir = path.parent().unwrap_or(Path::new("."));
    let mut tmp = NamedTempFile::new_in(dir)?;
    tmp.write_all(content)?;
    tmp.as_file().sync_all()?;  // crash-safe: flush to disk before rename
    tmp.persist(path)?;
    Ok(())
}
```

To preserve permissions from the original file:

```rust
use std::fs;

fn atomic_write_preserving_permissions(
    path: &Path, content: &[u8]
) -> anyhow::Result<()> {
    let perms = fs::metadata(path).ok().map(|m| m.permissions());
    let dir = path.parent().unwrap_or(Path::new("."));
    let mut tmp = NamedTempFile::new_in(dir)?;
    tmp.write_all(content)?;
    if let Some(perms) = perms {
        tmp.as_file().set_permissions(perms)?;
    }
    tmp.as_file().sync_all()?;
    tmp.persist(path)?;
    Ok(())
}
```

## Backup Management

### Create Backup Before Modification

Python pattern: `shutil.copy2(path, path + ".orig")`.
Rust pattern: copy then atomic-write the new content.

```rust
fn write_with_backup(
    path: &Path, content: &[u8], backup_suffix: &str,
) -> anyhow::Result<()> {
    if path.exists() {
        // Append suffix (don't use with_extension — it replaces the last extension)
        let backup = PathBuf::from(format!("{}{}", path.display(), backup_suffix));
        fs::copy(path, &backup)
            .with_context(|| format!("failed to create backup {}", backup.display()))?;
    }
    atomic_write(path, content)
}
```

### Find Backup Files

Walk a directory and collect files matching the backup suffix:

```rust
fn find_backup_files(root: &Path, suffix: &str) -> Vec<PathBuf> {
    walkdir::WalkDir::new(root)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .filter(|e| e.path().to_string_lossy().ends_with(suffix))
        .map(|e| e.into_path())
        .collect()
}
```

### Undo: Restore From Backup

Undo means: for each backup file, restore it to its original path by removing the suffix.

```rust
fn undo_backup(backup_path: &Path, suffix: &str) -> anyhow::Result<()> {
    let path_str = backup_path.to_string_lossy();
    let original = PathBuf::from(path_str.strip_suffix(suffix)
        .ok_or_else(|| anyhow::anyhow!("not a backup file: {}", backup_path.display()))?);
    fs::rename(backup_path, &original)?;
    Ok(())
}
```

### Clean: Remove Backup Files

```rust
fn clean_backups(root: &Path, suffix: &str) -> anyhow::Result<usize> {
    let backups = find_backup_files(root, suffix);
    let count = backups.len();
    for path in &backups {
        fs::remove_file(path)
            .with_context(|| format!("failed to remove {}", path.display()))?;
    }
    Ok(count)
}
```

## Rename With Collision Handling

When renaming files, a target may already exist. Common strategies:
1. Error out (strictest)
2. Add numeric suffix (`file.txt` → `file.txt.1`, `file.txt.2`)
3. Overwrite (dangerous)

Numeric suffix approach:

```rust
fn rename_no_clobber(src: &Path, dst: &Path) -> anyhow::Result<PathBuf> {
    if !dst.exists() {
        fs::rename(src, dst)?;
        return Ok(dst.to_path_buf());
    }
    // Find next available numeric suffix
    for i in 1u32.. {
        let candidate = PathBuf::from(format!("{}.{}", dst.display(), i));
        if !candidate.exists() {
            fs::rename(src, &candidate)?;
            return Ok(candidate);
        }
    }
    unreachable!()
}
```

When renames involve directory changes (moving files), create parent directories first:

```rust
if let Some(parent) = dst.parent() {
    fs::create_dir_all(parent)?;
}
fs::rename(src, dst)?;
```

## Directory Walking With Filtering

### Exclude Patterns

Python `os.walk` allows modifying `dirnames` in-place to skip directories.
In Rust, use `filter_entry()` on `walkdir::IntoIter` — this prunes the traversal tree:

```rust
use regex::Regex;
use std::sync::LazyLock;
use walkdir::WalkDir;

static EXCLUDE: LazyLock<Regex> = LazyLock::new(||
    Regex::new(r"^\\.").unwrap()  // skip dotfiles/dotdirs
);

fn walk_filtered(root: &Path, exclude: &Regex) -> Vec<PathBuf> {
    WalkDir::new(root)
        .into_iter()
        .filter_entry(|e| {
            e.file_name().to_str()
                .map(|name| !exclude.is_match(name))
                .unwrap_or(false)
        })
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .map(|e| e.into_path())
        .collect()
}
```

**Key rule:** Use `filter_entry()` for directory exclusion (prunes subtrees).
Use `.filter()` only for file-level filtering after traversal.

### Skip Backup Files During Walk

```rust
.filter_entry(|e| {
    !e.file_name().to_string_lossy().ends_with(".orig")
})
```

### Deterministic Output

Use `.sort_by_file_name()` on the `WalkDir` builder for deterministic ordering:

```rust
WalkDir::new(root)
    .sort_by_file_name()
    .into_iter()
```

## Path Manipulation

### Replacing Directory Prefixes

Python: `path.replace("old/prefix", "new/prefix")` (string manipulation on path).
Rust: use `strip_prefix` + `join`:

```rust
fn repath(path: &Path, old_prefix: &Path, new_prefix: &Path) -> Option<PathBuf> {
    path.strip_prefix(old_prefix)
        .ok()
        .map(|relative| new_prefix.join(relative))
}
```

### Appending Extensions

`Path::with_extension()` replaces the last extension. To append:

```rust
// Append ".orig" to "foo.tar.gz" → "foo.tar.gz.orig"
let mut backup = path.as_os_str().to_owned();
backup.push(".orig");
let backup = PathBuf::from(backup);
```

### Cross-Device Rename Fallback

`std::fs::rename` fails across filesystems. Handle with copy + delete:

```rust
fn move_file(from: &Path, to: &Path) -> io::Result<()> {
    match fs::rename(from, to) {
        Ok(()) => Ok(()),
        Err(e) if e.raw_os_error() == Some(libc::EXDEV) => {
            fs::copy(from, to)?;
            fs::remove_file(from)?;
            Ok(())
        }
        Err(e) => Err(e),
    }
}
```

**Note:** The copy + delete fallback is NOT atomic. For guaranteed atomicity, ensure
temp files are created on the same filesystem as the target using
`NamedTempFile::new_in(target_dir)`.

## Testing Filesystem Mutations

### Test Isolation With TempDir

Every test that modifies the filesystem should use its own temporary directory:

```rust
use tempfile::TempDir;

#[test]
fn test_rename_creates_backup() -> anyhow::Result<()> {
    let dir = TempDir::new()?;
    let file = dir.path().join("test.txt");
    fs::write(&file, "original")?;

    write_with_backup(&file, b"modified", ".orig")?;

    assert_eq!(fs::read_to_string(&file)?, "modified");
    assert_eq!(fs::read_to_string(dir.path().join("test.txt.orig"))?, "original");
    Ok(())
    // dir is automatically cleaned up on drop
}
```

### Asserting Directory Structure

For tests that involve file renames across directories, assert the full tree state:

```rust
fn list_files(dir: &Path) -> Vec<String> {
    WalkDir::new(dir)
        .sort_by_file_name()
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .map(|e| e.path().strip_prefix(dir).unwrap().display().to_string())
        .collect()
}

#[test]
fn test_file_move() -> anyhow::Result<()> {
    let dir = TempDir::new()?;
    // ... set up and run operation ...
    assert_eq!(
        list_files(dir.path()),
        vec!["new_dir/moved.txt"]
    );
    Ok(())
}
```

### Testing Atomic Write Safety

Verify no partial writes by checking file content is either fully old or fully new:

```rust
#[test]
fn test_atomic_write_no_partial() -> anyhow::Result<()> {
    let dir = TempDir::new()?;
    let file = dir.path().join("test.txt");
    fs::write(&file, "original")?;

    atomic_write(&file, b"replacement")?;

    let content = fs::read_to_string(&file)?;
    assert!(
        content == "original" || content == "replacement",
        "file has unexpected content: {content}"
    );
    Ok(())
}
```

### Testing Collision Handling

```rust
#[test]
fn test_rename_collision_adds_suffix() -> anyhow::Result<()> {
    let dir = TempDir::new()?;
    let src = dir.path().join("source.txt");
    let dst = dir.path().join("target.txt");
    fs::write(&src, "from source")?;
    fs::write(&dst, "existing")?;

    let actual = rename_no_clobber(&src, &dst)?;

    assert_eq!(actual, dir.path().join("target.txt.1"));
    assert_eq!(fs::read_to_string(&dst)?, "existing");
    assert_eq!(fs::read_to_string(&actual)?, "from source");
    Ok(())
}
```

### Cross-Validation Script

When porting a filesystem-heavy CLI, run both implementations on the same inputs and
compare full directory state:

```bash
#!/usr/bin/env bash
set -euo pipefail

for fixture in test-fixtures/*/; do
    name="$(basename "$fixture")"
    echo "=== $name ==="

    # Run Python
    cp -a "$fixture" "/tmp/py-$name"
    python -m mytool "/tmp/py-$name"

    # Run Rust
    cp -a "$fixture" "/tmp/rs-$name"
    ./target/release/mytool "/tmp/rs-$name"

    # Compare full directory trees
    diff -r "/tmp/py-$name" "/tmp/rs-$name" && echo "PASS" || echo "FAIL"
done
```

Compare not just file contents but also: file names, directory structure, backup files
created, permissions preserved.
