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
| `dict[K, V]` | `HashMap<K, V>` | **No insertion order!** Use `indexmap::IndexMap` if order matters |
| `set[T]` | `HashSet<T>` | `BTreeSet` for sorted |
| `frozenset` | `HashSet<T>` | Immutability via `let` binding, not the type. For use as hash key, need newtype implementing Hash |
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
| `Protocol` | `trait` | Rust traits are nominal -- must write explicit `impl Trait for Type` |
| `TypedDict` | Struct with named fields | Add serde derives only if deserializing from data formats |
| `Literal["a", "b"]` | `enum { A, B }` | |
| `Callable[[A], B]` | `Fn(A) -> B` / `FnMut` / `FnOnce` | `Fn` -- no mutation of captures, callable repeatedly (most Python callbacks). `FnMut` -- mutates captures. `FnOnce` -- consumes captures, callable once |

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
match command.as_str() { // .as_str() needed for String; &str can match directly
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
| `for/else` | No direct equivalent -- use `if let Some(item) = iter.find(\|x\| cond(x)) { ... } else { ... }` |

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
| `assert x == y` | `assert_eq!(x, y)` | `debug_assert_eq!` only for hot-path invariants |

### Context Managers to RAII

Python's `with` statement maps to Rust's RAII (Resource Acquisition Is Initialization) pattern,
where resources are cleaned up when they go out of scope via the `Drop` trait.

| Python | Rust | Notes |
| --- | --- | --- |
| `with open(f) as fh:` | `let content = std::fs::read_to_string(path)?;` | For simple read-all; or use `{ let file = File::open(path)?; ... }` (RAII scope) |
| `with lock:` | `let _guard = mutex.lock().unwrap();` | Guard released on scope exit |
| `@contextmanager` generator | `impl Drop` for cleanup | Or closure-based API: `with_resource(\|r\| { ... })` |
| `__enter__` / `__exit__` | `impl Drop` | `Drop::drop()` called automatically at scope end |

```python
# Python
with open("data.txt") as f:
    content = f.read()
    process(content)
# file closed here
```

```rust
// Rust: simple case -- just read the file
let content = std::fs::read_to_string("data.txt")?;
process(&content);

// Rust: RAII scope when you need the file handle
{
    let mut file = File::open("data.txt")?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;
    process(&content);
} // file closed here (Drop called)
```

```python
# Python: lock
with lock:
    shared_data.append(item)
```

```rust
// Rust: Mutex guard
{
    let mut data = mutex.lock().unwrap();
    data.push(item);
} // lock released here (guard dropped)
```

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
| `s.find(sub)` | `s.find(sub)` | Returns `Option<usize>`. **Returns byte offset, not char index!** Different for non-ASCII |
| `s[start:end]` | `&s[start..end]` | **Panics if not char boundary!** |
| `len(s)` | `s.len()` (bytes) / `s.chars().count()` (chars) | Different! |
| `f"hello {name}"` | `format!("hello {name}")` | |
| `s.encode('utf-8')` | `s.as_bytes()` | Rust strings are always UTF-8 |

## Regex

| Python | Rust | Notes |
| --- | --- | --- |
| `re.compile(pattern)` | `Regex::new(pattern)?` | Use `LazyLock` for statics |
| `re.match(pattern, s)` | `regex.is_match(s)` / `regex.captures(s)` | **Add `^` anchor!** Use `captures()` when match groups are accessed |
| `re.search(pattern, s)` | `regex.find(s)` | |
| `re.sub(pattern, repl, s)` | `regex.replace_all(s, repl)` | |
| `re.findall(pattern, s)` | `regex.find_iter(s).map(\|m\| m.as_str()).collect::<Vec<_>>()` | `find_iter()` returns `Match` objects, not strings |
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

### Dunder Methods to Rust Traits

| Python Dunder | Rust Equivalent | Notes |
| --- | --- | --- |
| `__str__()` | `impl fmt::Display` | Used by `format!`, `println!` |
| `__repr__()` | `#[derive(Debug)]` | Used by `{:?}` format |
| `__eq__()`/`__ne__()` | `#[derive(PartialEq)]` | Add `Eq` if no floating-point fields |
| `__hash__()` | `#[derive(Hash)]` | Requires `PartialEq + Eq` |
| `__lt__()` etc. | `impl PartialOrd` / `#[derive(Ord)]` | `Ord` requires `Eq` |
| `__len__()` | `.len()` method | No standard trait; convention only |
| `__iter__()` + `__next__()` | `impl Iterator` | Must define `type Item` |
| `__getitem__()` | `impl Index<Idx>` | Returns reference, not owned value |
| `__add__()` etc. | `impl Add` from `std::ops` | One trait per operator |
| `__enter__()`/`__exit__()` | `impl Drop` + RAII scope | See context managers below |
| `__contains__()` | `.contains()` method | No standard trait; convention only |
| `__bool__()` | No standard trait | Use explicit `.is_empty()` or method |

### Generators to Iterators

Python generators map to Rust iterators, but require explicit state management.

**Simple generator (stateless):**

```python
# Python
def evens(n):
    for i in range(n):
        if i % 2 == 0:
            yield i
```

```rust
// Rust: using std::iter::from_fn for simple one-off cases
fn evens(n: usize) -> impl Iterator<Item = usize> {
    let mut i = 0;
    std::iter::from_fn(move || {
        while i < n {
            let current = i;
            i += 1;
            if current % 2 == 0 {
                return Some(current);
            }
        }
        None
    })
}
```

**Stateful generator -- struct implementing `Iterator`:**

```python
# Python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

```rust
// Rust
struct Fibonacci { a: u64, b: u64 }

impl Fibonacci {
    fn new() -> Self { Self { a: 0, b: 1 } }
}

impl Iterator for Fibonacci {
    type Item = u64;
    fn next(&mut self) -> Option<Self::Item> {
        let result = self.a;
        (self.a, self.b) = (self.b, self.a + self.b);
        Some(result)
    }
}
```

**Note:** `gen` blocks are a reserved keyword in Edition 2024 and an experimental feature.
When stabilized, they will allow Python-like `yield` syntax in Rust.

### Dataclasses to Structs with Derives

| Python `@dataclass` | Rust Equivalent | Notes |
| --- | --- | --- |
| `@dataclass` | `#[derive(Debug, Clone, PartialEq)]` | Closest equivalent derives |
| `frozen=True` | No `&mut self` methods | Immutability enforced by API design, not annotation |
| `order=True` | `#[derive(PartialOrd, Ord)]` | Requires `Eq` |
| `field(default=...)` | `impl Default` or `#[derive(Default)]` | |

```python
# Python
@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float
    label: str = "origin"
```

```rust
// Rust
#[derive(Debug, Clone, PartialEq, PartialOrd)]
pub struct Point {
    pub x: f64,
    pub y: f64,
    pub label: String,
}

impl Default for Point {
    fn default() -> Self {
        Self { x: 0.0, y: 0.0, label: "origin".to_string() }
    }
}
```

### Python Enums to Rust Enums

| Python | Rust | Notes |
| --- | --- | --- |
| `class Color(Enum):` | `enum Color { ... }` | |
| `Color.RED` | `Color::Red` | Rust uses CamelCase variants |
| `Color(1)` (by value) | Custom `from_value()` method | No built-in value lookup |
| `color.name` | Use `strum` crate `Display` derive | `#[derive(strum::Display)]` |
| `Color["RED"]` (by name) | Use `strum` crate `EnumString` derive | `#[derive(strum::EnumString)]` |
| `auto()` | Explicit variants | No auto-numbering |

```python
# Python
from enum import Enum

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
```

```rust
// Rust (with strum for Display/FromStr)
use strum::{Display, EnumString};

#[derive(Debug, Clone, Copy, PartialEq, Display, EnumString)]
pub enum Color {
    #[strum(serialize = "red")]
    Red,
    #[strum(serialize = "green")]
    Green,
    #[strum(serialize = "blue")]
    Blue,
}
```

### Async Patterns

| Python | Rust | Notes |
| --- | --- | --- |
| `async def foo()` | `async fn foo()` | |
| `await bar()` | `bar().await` | Postfix syntax in Rust |
| `asyncio.run(main())` | `#[tokio::main]` on `async fn main()` | Requires `tokio` runtime |
| `asyncio.gather(a, b)` | `tokio::join!(a, b)` | |
| `asyncio.create_task(coro)` | `tokio::spawn(future)` | Returns `JoinHandle` |
| `async for item in aiter:` | `while let Some(item) = stream.next().await {` | Requires `tokio-stream` or `futures` |
| `async with resource:` | Scope + `.await` on cleanup | No async Drop |

### Parallelism Patterns

| Python | Rust | Notes |
| --- | --- | --- |
| `multiprocessing.Pool.map(f, items)` | `items.par_iter().map(f).collect()` | `rayon` crate; data parallelism |
| `threading.Thread(target=f)` | `std::thread::spawn(f)` | OS-level threads |
| `concurrent.futures.ThreadPoolExecutor` | `rayon::ThreadPool` or `tokio::spawn` | `rayon` for CPU, `tokio` for I/O |
| `concurrent.futures.ProcessPoolExecutor` | `rayon::ThreadPool` | Rust threads share memory; no process isolation needed |
| `queue.Queue` | `std::sync::mpsc::channel()` | Or `crossbeam::channel` for multi-producer |
| `threading.Lock` | `std::sync::Mutex<T>` | Mutex wraps data in Rust, not code |

## Testing

| Python | Rust | Notes |
| --- | --- | --- |
| `def test_foo():` | `#[test] fn test_foo() {` | |
| `assert x == y` | `assert_eq!(x, y)` | |
| `assert x != y` | `assert_ne!(x, y)` | |
| `assert x` | `assert!(x)` | |
| `with pytest.raises(E):` | `#[should_panic]` or `assert!(result.is_err())` | |
| `@pytest.mark.skip` | `#[ignore]` | |
| `@pytest.fixture` | Setup in test function or `std::sync::LazyLock` | |
| `@pytest.mark.parametrize` | `rstest` crate or macro-generated tests | |
| `pytest.approx(x)` | `(x - y).abs() < epsilon` | Or use `approx` crate: `assert_relative_eq!`, `assert_abs_diff_eq!` |

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
| `~=1.4` | `"^1.4"` | Compatible release (>=1.4, <2.0); caret is Cargo default |
| `==1.4.*` | `"~1.4"` | Exact minor (>=1.4, <1.5); tilde in Cargo |
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
| `pytest.fixture` (module/session-scoped) | `std::sync::LazyLock` for shared state | |
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
| marko (Markdown) | comrak 0.50+ | Good with workarounds | 12/15 differences worked around; check for API changes in 0.50+ |
| argparse | clap 4.5 (derive) | Excellent | Perfect mapping |
| PyYAML | serde_yaml_ng 0.10+ | Good | serde_yaml is archived |
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
