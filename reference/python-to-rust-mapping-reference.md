# Python-to-Rust Mapping Reference

Exhaustive mapping table for Python-to-Rust constructs. Organized by category with
code examples for each mapping. Use this as a lookup reference during porting.

**Related:** [Python-to-Rust Porting Guide](python-to-rust-porting-guide.md) |
`tbd guidelines python-to-rust-porting-rules`

**Last update:** 2026-02-07

## Types

### Primitives

| Python | Rust | Example |
| --- | --- | --- |
| `str` | `&str` (borrow) / `String` (owned) | Accept `&str`, return `String` |
| `int` | `i32` / `i64` / `usize` | Match semantic range |
| `float` | `f64` / `f32` | `f64` for double precision |
| `bool` | `bool` | Same |
| `None` | `Option::None` | Use `Option<T>` |
| `bytes` | `&[u8]` / `Vec<u8>` | |
| `complex` | (no built-in) | Use `num-complex` crate |

### Collections

| Python | Rust | Notes |
| --- | --- | --- |
| `list[T]` | `Vec<T>` | |
| `tuple[A, B, C]` | `(A, B, C)` | Named struct if >3 fields |
| `dict[K, V]` | `HashMap<K, V>` | `BTreeMap` for sorted |
| `set[T]` | `HashSet<T>` | `BTreeSet` for sorted |
| `frozenset` | `HashSet<T>` (immutable by default) | |
| `deque` | `VecDeque<T>` | |
| `defaultdict(list)` | `HashMap<K, Vec<V>>` + `.entry().or_default()` | |
| `Counter` | `HashMap<T, usize>` | |
| `OrderedDict` | `IndexMap<K, V>` (indexmap crate) | |
| `namedtuple` | Struct with named fields | |

### Type Hints to Rust Types

| Python | Rust | Notes |
| --- | --- | --- |
| `Optional[T]` | `Option<T>` | |
| `Union[A, B]` | `enum { A(A), B(B) }` | |
| `Any` | Generics or `Box<dyn Trait>` | Avoid if possible |
| `TypeVar('T')` | `<T>` generics | |
| `Protocol` | `trait` | |
| `TypedDict` | Struct with `serde::Deserialize` | |
| `Literal["a", "b"]` | `enum { A, B }` | |
| `Callable[[A], B]` | `Fn(A) -> B` | With trait bounds |

## Control Flow

### Conditionals

```python
# Python
if x > 0:
    result = "positive"
elif x == 0:
    result = "zero"
else:
    result = "negative"
```

```rust
// Rust
let result = if x > 0 {
    "positive"
} else if x == 0 {
    "zero"
} else {
    "negative"
};
```

### Pattern Matching

```python
# Python (3.10+)
match command:
    case "quit":
        exit()
    case "hello":
        greet()
    case _:
        unknown()
```

```rust
// Rust
match command {
    "quit" => exit(),
    "hello" => greet(),
    _ => unknown(),
}
```

### Loops

| Python | Rust |
| --- | --- |
| `for x in items:` | `for x in &items {` |
| `for i, x in enumerate(items):` | `for (i, x) in items.iter().enumerate() {` |
| `for x in range(10):` | `for x in 0..10 {` |
| `while condition:` | `while condition {` |
| `break` / `continue` | `break` / `continue` |
| `for/else` | No direct equivalent -- use flag variable |

### Comprehensions to Iterators

```python
# Python
result = [x * 2 for x in items if x > 0]
```

```rust
// Rust
let result: Vec<_> = items.iter()
    .filter(|&&x| x > 0)
    .map(|&x| x * 2)
    .collect();
```

```python
# Dict comprehension
d = {k: v for k, v in pairs if v > 0}
```

```rust
// Rust
let d: HashMap<_, _> = pairs.iter()
    .filter(|(_, v)| *v > 0)
    .cloned()
    .collect();
```

## Error Handling

| Python | Rust | Notes |
| --- | --- | --- |
| `try: / except:` | `match result { Ok(v) => ..., Err(e) => ... }` | Or use `?` |
| `raise ValueError(msg)` | `return Err(Error::Validation(msg))` | |
| `raise` (re-raise) | `return Err(e)` or just `?` | |
| `finally:` | `Drop` trait / scope guards | |
| `with context_manager:` | Scope + `Drop` / closure patterns | |
| `assert x == y` | `debug_assert_eq!(x, y)` | Not for production checks |

### Error Propagation

```python
# Python
def process(path):
    try:
        data = read_file(path)
        return transform(data)
    except FileNotFoundError:
        return default_data()
    except ValueError as e:
        raise RuntimeError(f"transform failed: {e}")
```

```rust
// Rust
fn process(path: &Path) -> Result<Data> {
    let data = match read_file(path) {
        Ok(d) => d,
        Err(Error::NotFound(_)) => return Ok(default_data()),
        Err(e) => return Err(e),
    };
    transform(&data).map_err(|e| Error::Runtime(format!("transform failed: {e}")))
}
```

## I/O

| Python | Rust | Notes |
| --- | --- | --- |
| `open(path).read()` | `std::fs::read_to_string(path)?` | |
| `open(path, 'w').write(data)` | `std::fs::write(path, data)?` | |
| `Path(path).exists()` | `Path::new(path).exists()` | |
| `Path(path).parent` | `path.parent()` | Returns `Option<&Path>` |
| `os.path.join(a, b)` | `path.join(b)` | |
| `sys.stdin.read()` | `std::io::stdin().read_to_string(&mut buf)?` | |
| `print(x)` | `println!("{x}")` | |
| `print(x, file=sys.stderr)` | `eprintln!("{x}")` | |
| `glob.glob("*.md")` | `glob::glob("*.md")?` (glob crate) | |

## String Operations

| Python | Rust | Notes |
| --- | --- | --- |
| `s.strip()` | `s.trim()` | |
| `s.lstrip()` / `s.rstrip()` | `s.trim_start()` / `s.trim_end()` | |
| `s.split(sep)` | `s.split(sep)` | Returns iterator |
| `s.splitlines()` | `s.lines()` | |
| `sep.join(items)` | `items.join(sep)` | On slices |
| `s.replace(old, new)` | `s.replace(old, new)` | Returns new String |
| `s.startswith(p)` | `s.starts_with(p)` | |
| `s.endswith(p)` | `s.ends_with(p)` | |
| `s.upper()` / `s.lower()` | `s.to_uppercase()` / `s.to_lowercase()` | |
| `s.find(sub)` | `s.find(sub)` | Returns `Option<usize>` |
| `s[start:end]` | `&s[start..end]` | **Panics if not char boundary!** |
| `len(s)` | `s.len()` (bytes) / `s.chars().count()` (chars) | Different! |
| `f"hello {name}"` | `format!("hello {name}")` | |
| `s.encode('utf-8')` | `s.as_bytes()` | Rust strings are always UTF-8 |

## Regex

| Python | Rust | Notes |
| --- | --- | --- |
| `re.compile(pattern)` | `Regex::new(pattern)?` | Use `LazyLock` for statics |
| `re.match(pattern, s)` | `regex.is_match(s)` | **Add `^` anchor!** |
| `re.search(pattern, s)` | `regex.find(s)` | |
| `re.sub(pattern, repl, s)` | `regex.replace_all(s, repl)` | |
| `re.findall(pattern, s)` | `regex.find_iter(s).collect()` | |
| `match.group(0)` | `m.as_str()` | |
| `match.group(1)` | `caps.get(1).map(\|m\| m.as_str())` | |
| Look-ahead/behind | Use `fancy-regex` crate | Not in standard `regex` |

**Critical difference:** Python `re.match()` anchors to string start. Rust `is_match()`
matches anywhere. Always add `^` for patterns that were used with `re.match()`.

## Classes to Structs

```python
# Python
class Config:
    def __init__(self, width: int = 80, verbose: bool = False):
        self.width = width
        self.verbose = verbose

    def with_width(self, width: int) -> 'Config':
        return Config(width=width, verbose=self.verbose)
```

```rust
// Rust
#[derive(Debug, Clone)]
pub struct Config {
    pub width: usize,
    pub verbose: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self { width: 80, verbose: false }
    }
}

impl Config {
    pub fn with_width(mut self, width: usize) -> Self {
        self.width = width;
        self
    }
}
```

### Inheritance to Composition/Traits

```python
# Python
class Animal:
    def speak(self) -> str: ...

class Dog(Animal):
    def speak(self) -> str:
        return "woof"
```

```rust
// Rust
trait Animal {
    fn speak(&self) -> &str;
}

struct Dog;

impl Animal for Dog {
    fn speak(&self) -> &str { "woof" }
}
```

## Testing

| Python | Rust | Notes |
| --- | --- | --- |
| `def test_foo():` | `#[test] fn test_foo() {` | |
| `assert x == y` | `assert_eq!(x, y)` | |
| `assert x != y` | `assert_ne!(x, y)` | |
| `assert x` | `assert!(x)` | |
| `with pytest.raises(E):` | `#[should_panic]` or `assert!(result.is_err())` | |
| `@pytest.mark.skip` | `#[ignore]` | |
| `@pytest.fixture` | Setup in test function or `once_cell` | |
| `@pytest.mark.parametrize` | `rstest` crate or macro-generated tests | |
| `pytest.approx(x)` | `(x - y).abs() < epsilon` | |

## Packaging

| Python | Rust | Notes |
| --- | --- | --- |
| `pyproject.toml` | `Cargo.toml` | |
| `pip install` | `cargo install` / `cargo add` | |
| `requirements.txt` | `Cargo.toml [dependencies]` | |
| `setup.py` | `Cargo.toml` | |
| `__init__.py` | `lib.rs` | |
| `__main__.py` | `main.rs` | |
| PyPI | crates.io | |
| `pip install -e .` | `cargo build` (automatic) | |
| Virtual environments | Cargo handles isolation via `target/` dir | |

## Project Setup Mapping

This section maps the full Python project infrastructure to Rust equivalents.
Not for education -- for agents and engineers who know both languages but need
the specific equivalences and pitfalls.

### Manifest Structure: pyproject.toml vs Cargo.toml

| Python (`pyproject.toml`) | Rust (`Cargo.toml`) | Notes |
| --- | --- | --- |
| `[project]` name, version, description | `[package]` name, version, description | Same fields, different table name |
| `[project]` authors, license | `[package]` authors, license | Rust uses SPDX expressions: `"MIT OR Apache-2.0"` |
| `requires-python = ">=3.11"` | `rust-version = "1.85"` | MSRV. Enforced by `cargo` and CI |
| `[project]` readme, urls | `[package]` readme, repository, homepage | Rust separates homepage from repository |
| `[project]` keywords, classifiers | `[package]` keywords, categories | Rust categories are from a fixed list on crates.io |
| `[project.dependencies]` | `[dependencies]` | See version constraints below |
| `[project.optional-dependencies]` | `[features]` + optional deps | See feature flags below |
| `[dependency-groups]` (PEP 735) | `[dev-dependencies]`, `[build-dependencies]` | Rust separates dev and build deps explicitly |
| `[build-system]` | N/A (cargo is the only build system) | No equivalent of setuptools/hatch/flit/maturin |
| `[tool.ruff]`, `[tool.mypy]`, etc. | Separate files: `rustfmt.toml`, `deny.toml`, etc. | Python centralizes; Rust distributes config |

### Version Constraint Syntax

| Python | Rust (Cargo) | Semantics |
| --- | --- | --- |
| `>=1.0,<2.0` | `">=1.0, <2.0"` | Exact range (same) |
| `~=1.4` | `"~1.4"` | Compatible release (roughly the same) |
| `==1.4.*` | `"1.4"` | Cargo's default `^` is "compatible with" |
| `>=1.4` | `">=1.4"` | Minimum version (same) |
| `==1.4.0` | `"=1.4.0"` | Exact pin (note single `=` in Cargo) |
| No default | `"1.4"` means `^1.4` (>=1.4.0, <2.0.0) | Cargo's default is permissive semver-compatible |

**Pitfall:** Python `~=1.4.2` means `>=1.4.2, <1.5.0`. Cargo `~1.4.2` means the same.
But Cargo's default `^1.4.2` means `>=1.4.2, <2.0.0` -- much more permissive.
When porting, `~=` maps to `~`, not to the bare version.

### Lock Files

| Python | Rust | Notes |
| --- | --- | --- |
| `uv.lock` / `poetry.lock` | `Cargo.lock` | Same purpose: reproducible builds |
| Commit lock for apps | Commit `Cargo.lock` for binaries | Same rule: commit for apps, don't for libraries |
| Don't commit for libraries | Don't commit for libraries | Cargo docs say the same as Python community convention |
| `pip freeze > requirements.txt` | `Cargo.lock` (automatic) | No manual freeze step in Rust |
| `uv pip compile` (lock without install) | `cargo generate-lockfile` | Rarely needed; cargo auto-generates |

### Dependency Management Commands

| Python | Rust | Notes |
| --- | --- | --- |
| `uv add requests` | `cargo add reqwest` | Adds to manifest |
| `uv remove requests` | `cargo remove reqwest` | |
| `uv sync` / `pip install -r` | `cargo build` (fetches automatically) | No separate install step |
| `uv lock` / `pip compile` | `cargo update` | Regenerate lock file |
| `uv tree` / `pipdeptree` | `cargo tree` | Dependency tree |
| `pip install -e .` | `cargo build` (always editable) | No concept of editable install |
| `uv run script.py` | `cargo run` | |
| `uv run pytest` | `cargo test` | |

### Environment and Toolchain Management

| Python | Rust | Notes |
| --- | --- | --- |
| `pyenv` / `uv python install` | `rustup install` | Install toolchain versions |
| `.python-version` | `rust-toolchain.toml` | Pin project toolchain version |
| `python -m venv .venv` | N/A | No virtualenvs; Cargo isolates via `target/` |
| `source .venv/bin/activate` | N/A | No activation step |
| `VIRTUAL_ENV` env var | `CARGO_HOME` (~/.cargo) | Where tools/caches live |
| `uv tool install ruff` | `cargo install ripgrep` | Install CLI tools globally |
| `pipx` | `cargo install` / `cargo binstall` | Install binaries from registry |

**Key difference:** Python requires creating and activating virtual environments per project.
Rust has no equivalent -- `cargo` builds into a project-local `target/` directory and
resolves dependencies per-project from the lock file. There is no global dependency state
to isolate from.

### Linting and Formatting

| Python | Rust | Notes |
| --- | --- | --- |
| `ruff check` | `cargo clippy` | Linter |
| `ruff format` / `black` | `cargo fmt` | Formatter |
| `mypy` / `pyright` | (compiler) | Rust's type checker is the compiler itself |
| `isort` | (rustfmt) | Import ordering is handled by rustfmt |
| `# noqa: E501` | `#[allow(clippy::too_many_lines)]` | Suppress specific lint |
| `# type: ignore` | N/A | No equivalent needed; compiler errors are real errors |
| `[tool.ruff]` in pyproject.toml | `[lints.clippy]` in Cargo.toml | Lint config location |
| `[tool.ruff.format]` in pyproject.toml | `rustfmt.toml` | Format config location |
| `ruff.toml` / `.flake8` | `clippy.toml` (rare; most use Cargo.toml) | |
| `.pre-commit-config.yaml` | `justfile` precommit recipe or git hooks | No standard pre-commit framework |

**Key difference:** Python needs 3+ tools (ruff/black + mypy + isort) to achieve what
Rust gets from 2 (rustfmt + clippy) plus the compiler. The compiler subsumes the role
of Python type checkers entirely. There is no "gradually typed" -- it's all checked.

### Testing

| Python | Rust | Notes |
| --- | --- | --- |
| `pytest` | `cargo test` (built-in) | No external test runner needed |
| `conftest.py` | `tests/common/mod.rs` | Shared test utilities |
| `tests/` directory | `tests/` (integration) + `#[cfg(test)]` (unit) | Rust has two test locations |
| `pytest.ini` / `[tool.pytest]` | `.config/nextest.toml` (if using nextest) | Minimal test config in Rust |
| `pytest-xdist` (parallel) | `cargo nextest run` | nextest for parallel execution |
| `pytest-cov` / `coverage.py` | `cargo-tarpaulin` / `cargo-llvm-cov` | |
| `pytest --cov --branch` | `cargo tarpaulin --branch` / `cargo llvm-cov --branch` | Branch coverage |
| `pytest.fixture` (function-scoped) | Setup code in test function | No fixture injection |
| `pytest.fixture` (module/session-scoped) | `LazyLock` / `once_cell` for shared state | |
| `@pytest.mark.parametrize` | `rstest` crate | |
| `@pytest.mark.skip` / `@pytest.mark.skipif` | `#[ignore]` | No conditional skip; use `#[cfg]` |
| `@pytest.mark.xfail` | No direct equivalent | Test expected failures manually |
| `doctest` module | `/// ``` ... ```` (doc-tests) | Rust doc-tests run via `cargo test` |
| Test discovery by `test_` prefix | `#[test]` attribute + `tests/*.rs` files | Explicit, not naming-convention |
| `tox` / `nox` (multi-env testing) | CI matrix (OS x toolchain) | No equivalent tool; CI handles it |

### Documentation

| Python | Rust | Notes |
| --- | --- | --- |
| `"""Docstring"""` inside function | `/// Doc comment` before function | Position differs |
| Google/NumPy/reST docstring styles | Markdown with `# Examples`, `# Errors`, `# Panics` | Standardized sections |
| Sphinx (RST-based) | `cargo doc` / docs.rs | Auto-generated API docs |
| MkDocs (Markdown-based) | `mdbook` | Book-style documentation |
| ReadTheDocs hosting | docs.rs (automatic for crates.io) | Hosting is free for published crates |
| `help()` / `pydoc` | `cargo doc --open` | |
| `autodoc` extracts from source | `cargo doc` extracts from `///` comments | Same concept |
| `__doc__` attribute | `#[doc = "..."]` attribute | Rarely used directly |

### Security Auditing

| Python | Rust | Notes |
| --- | --- | --- |
| `pip-audit` | `cargo audit` | Vulnerability scanning |
| `safety` (legacy) | `cargo audit` | |
| `bandit` (SAST) | `cargo-deny` + `cargo-geiger` | Static security analysis |
| `pip-licenses` / `liccheck` | `cargo deny check licenses` | License compliance |
| PyPI advisory database (OSV) | RustSec advisory database | |
| Dependabot / Renovate | Dependabot / Renovate (same tools) | Both ecosystems supported |

### Task Runners

| Python | Rust | Notes |
| --- | --- | --- |
| `Makefile` | `justfile` (recommended) or `Makefile` | `just` is the modern Rust convention |
| `tox` | N/A (CI matrix) | No Rust equivalent |
| `nox` | `just` / `cargo-xtask` | |
| `hatch scripts` / `pdm scripts` | `just` recipes | |
| `invoke` / `fabric` | `just` / `cargo-make` | |
| `pre-commit` framework | Git hooks + `just precommit` | No standard framework; `just` is common |

### CI/CD Patterns

| Python CI step | Rust CI step | Notes |
| --- | --- | --- |
| `actions/setup-python@v5` | `dtolnay/rust-toolchain@stable` | Toolchain setup |
| `astral-sh/setup-uv@v4` | `Swatinem/rust-cache@v2` | Dependency caching |
| Cache pip/uv cache dir | Cache `target/` via rust-cache | Different cache strategies |
| `uv sync` / `pip install -r requirements.txt` | (automatic on first `cargo` command) | No explicit install step |
| `ruff check .` | `cargo clippy --all-targets --all-features -- -D warnings` | Lint step |
| `ruff format --check .` | `cargo fmt --all -- --check` | Format check step |
| `mypy .` | N/A (compiler checks types) | |
| `pytest` | `cargo test --all-features --locked` | `--locked` ensures Cargo.lock is used |
| `pytest -n auto` (parallel) | `cargo nextest run` | |
| Matrix across Python versions (3.11, 3.12) | Matrix across OS (ubuntu, macos, windows) | Different matrix axes |
| MSRV: test with oldest Python | MSRV: `dtolnay/rust-toolchain@1.85` (pin to MSRV) | |
| `pip-audit` | `rustsec/audit-check@v2` | |
| | `EmbarkStudios/cargo-deny-action@v2` | No Python equivalent |

**Pitfall: CI build time.** Python CI is fast (no compilation). Rust CI is slow (compilation
from scratch takes minutes). Mitigate with `Swatinem/rust-cache@v2`, separate CI jobs
(fmt and clippy are fast, test is slow), and `cargo check` before `cargo test` where possible.

### Feature Flags vs Optional Dependencies

| Python | Rust | Notes |
| --- | --- | --- |
| `[project.optional-dependencies]` extras | `[features]` in Cargo.toml | Define named feature groups |
| `pip install package[dev,test]` | `cargo build --features dev,test` | Activate features |
| `try: import X; except ImportError:` | `#[cfg(feature = "cli")]` | Conditional compilation |
| No default extras | `default = ["cli"]` in `[features]` | Cargo supports default features |
| Runtime availability check | Compile-time conditional compilation | Fundamental difference |

```toml
# Rust: Cargo.toml features example (from flowmark-rs)
[features]
default = ["cli"]
cli = ["clap", "color-eyre", "tracing", "tempfile", "indicatif", "ctrlc"]

# Dependencies gated behind features
[dependencies]
clap = { version = "4.5", features = ["derive"], optional = true }
```

**Key difference:** Python optional dependencies exist at runtime -- you check if they're
importable. Rust features are compile-time -- code behind `#[cfg(feature = "...")]` is
not compiled at all. This means Rust features affect binary size and compilation time,
not just runtime behavior.

### Build and Release

| Python | Rust | Notes |
| --- | --- | --- |
| `python -m build` / `hatch build` | `cargo build --release` | Build step |
| `sdist` / `wheel` formats | `.crate` format (for crates.io) | |
| `twine upload` / `uv publish` | `cargo publish` | Publish to registry |
| `setuptools` / `hatch` / `flit` | `cargo` (only one build system) | No build backend fragmentation |
| `setup.py` (build-time code) | `build.rs` (build script) | Arbitrary build-time logic |
| `MANIFEST.in` / `include`/`exclude` | `include`/`exclude` in Cargo.toml `[package]` | Control what goes in the package |
| `__version__` / `importlib.metadata` | `env!("CARGO_PKG_VERSION")` | Version at compile time |
| `setuptools-scm` (git-based versioning) | `cargo-release` (version bumping + tagging) | |

### Config File Locations

| Purpose | Python | Rust |
| --- | --- | --- |
| Package manifest | `pyproject.toml` | `Cargo.toml` |
| Lock file | `uv.lock` / `poetry.lock` | `Cargo.lock` |
| Formatter | `[tool.ruff.format]` or `[tool.black]` | `rustfmt.toml` |
| Linter | `[tool.ruff]` or `.flake8` | `[lints.clippy]` in Cargo.toml |
| Type checker | `[tool.mypy]` or `pyrightconfig.json` | N/A (compiler) |
| Test runner | `[tool.pytest.ini_options]` | `.config/nextest.toml` (optional) |
| Coverage | `[tool.coverage]` | (cargo-tarpaulin / cargo-llvm-cov flags) |
| Dependency policy | N/A | `deny.toml` |
| Release automation | N/A | `release.toml` |
| Build settings | `[build-system]` | `.cargo/config.toml` |
| Task runner | `Makefile` / `tox.ini` / `noxfile.py` | `justfile` |
| Toolchain pin | `.python-version` | `rust-toolchain.toml` |
| Editor settings | `.editorconfig` | `.editorconfig` (same) |
| Git ignores | `.gitignore` (add `.venv/`, `__pycache__/`) | `.gitignore` (add `target/`) |
| Environment vars | `PYTHONPATH`, `VIRTUAL_ENV` | `CARGO_HOME`, `RUSTFLAGS`, `RUST_LOG` |

**Key insight:** Python consolidates most tool config into `pyproject.toml` via `[tool.*]`
sections. Rust distributes config across separate files (`rustfmt.toml`, `deny.toml`,
`release.toml`, `.cargo/config.toml`). When setting up a Rust project, expect to create
4-6 config files where Python would have one.

## Dependency Mapping (Flowmark-Specific)

| Python Package | Rust Crate | Quality | Notes |
| --- | --- | --- | --- |
| marko (Markdown) | comrak 0.47 | Good with workarounds | 12/15 differences worked around |
| argparse | clap 4.5 (derive) | Excellent | Perfect mapping |
| PyYAML | serde_yaml 0.9 | Good | Used for config/frontmatter |
| re (regex) | regex 1.10 | Excellent | Different anchoring! |
| textwrap | textwrap (crate) | Good | Also rolled custom for special cases |
| pytest | cargo test (built-in) | Excellent | |
| (dataclasses) | serde Serialize/Deserialize | Excellent | |
| (type hints) | Rust type system | Built-in | |
| (none) | thiserror 2.0 | Excellent | Library error types |
| (none) | color-eyre 0.6 | Excellent | CLI error display |
| (none) | tracing 0.1 | Excellent | Structured logging |
| (none) | indicatif 0.18 | Good | Progress bars |
| (none) | tempfile 3.10 | Excellent | Atomic file writes |
| (none) | unicode-segmentation 1.11 | Excellent | Unicode-safe text ops |
| (none) | proptest 1.4 | Excellent | Property-based testing |
