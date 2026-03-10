# Extracting `sovereign_debt_py` into its own repository

`sovereign_debt_py` is a pure-Python library (no PyXLL / Excel dependency) that
lives at the root of the `sovereign_debt_xl` repository.  It currently provides
a `plotting` subpackage for Matplotlib-based sovereign debt charts.

---

## Current layout inside `sovereign_debt_xl`

```
sovereign_debt_xl/              ← repo root
├── sovereign_debt_py/          ← importable pure-Python package
│   ├── __init__.py
│   └── plotting/
│       ├── __init__.py
│       ├── core.py             ← validation helpers + fig_to_png_bytes
│       ├── yield_curve.py      ← plot_yield_curve
│       ├── timeseries.py       ← plot_timeseries / plot_rolling_average / plot_spread
│       └── dsa.py              ← plot_fan_chart
├── sovereign_debt_xl/          ← PyXLL / Excel add-in package
│   └── *.py
├── test_plotting.py            ← pytest suite for sovereign_debt_py
├── pyproject.toml              ← single pyproject for both packages
└── requirements.txt
```

---

## Option A — Preserve git history with `git subtree split`

Preserving history lets you see every commit that ever touched `sovereign_debt_py`
in the new repo, which is useful for `git blame`, changelogs, and bisect.

### Prerequisites

```bash
# git ≥ 1.7.11 ships subtree support built-in — no extra install needed
git --version
```

### Steps

```bash
# 1. Work in a fresh clone of sovereign_debt_xl so you can't accidentally
#    push the rewritten branch back to the wrong remote.
git clone https://github.com/zachessesjohnson/sovereign_debt_xl.git sdpy-extraction
cd sdpy-extraction

# 2. Create a local branch whose *entire* history consists only of commits
#    that touched sovereign_debt_py/, with that directory promoted to root.
git subtree split --prefix=sovereign_debt_py -b split/sovereign-debt-py

# 3. Create the new, empty GitHub repository via the web UI or gh CLI:
#      https://github.com/new  →  name it "sovereign_debt_py"
#    (Do NOT initialise it with a README — keep it completely empty.)

# 4. Add the new repo as a remote and push the extracted branch as main.
git remote add new-origin https://github.com/zachessesjohnson/sovereign_debt_py.git
git push new-origin split/sovereign-debt-py:main

# 5. Verify the new repo looks correct, then clean up the scratch clone.
cd ..
rm -rf sdpy-extraction
```

After the push, `sovereign_debt_py.git` will contain only the files that were
inside `sovereign_debt_py/` in each commit, and the commit timestamps / messages
will match those in `sovereign_debt_xl`.

### Alternative: `git filter-repo` (faster for large histories)

`git filter-repo` is a third-party tool (install with `pip install git-filter-repo`)
that is faster and safer than `filter-branch` for large repos.

```bash
pip install git-filter-repo

# Work in a fresh clone.
git clone https://github.com/zachessesjohnson/sovereign_debt_xl.git sdpy-extraction
cd sdpy-extraction

# Rewrite history, keeping only the sovereign_debt_py/ subtree.
git filter-repo --subdirectory-filter sovereign_debt_py

# Push the rewritten main branch to the new repository.
git remote add new-origin https://github.com/zachessesjohnson/sovereign_debt_py.git
git push new-origin main

cd ..
rm -rf sdpy-extraction
```

---

## Option B — Simple copy (no history)

Use this when you want a clean start in the new repo and do not need git history.

```bash
# 1. Create the new GitHub repository (empty, no README) via the web UI.

# 2. Copy the sub-project contents to a temporary directory.
cp -r sovereign_debt_py/ /tmp/sovereign_debt_py_new
cd /tmp/sovereign_debt_py_new

# 3. Initialise a fresh git repo and make the first commit.
git init -b main
git add .
git commit -m "Initial commit: extracted from sovereign_debt_xl"

# 4. Push to the new repository.
git remote add origin https://github.com/zachessesjohnson/sovereign_debt_py.git
git branch -M main
git push -u origin main
```

---

## After the extraction: adding a `pyproject.toml`

Once extracted into its own repo, `sovereign_debt_py` will need its own
`pyproject.toml`.  A minimal starting point:

```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[project]
name = "sovereign-debt-py"
version = "0.1.0"
description = "Pure-Python sovereign debt analytics and plotting"
requires-python = ">=3.11"
dependencies = [
    "numpy",
    "pandas",
    "matplotlib",
]

[project.optional-dependencies]
dev = ["pytest"]

[tool.setuptools.packages.find]
where = ["."]
include = ["sovereign_debt_py*"]
```

### Declaring the dependency in `sovereign_debt_xl`

**Via GitHub (before a PyPI release)** — edit `pyproject.toml` in `sovereign_debt_xl`:

```toml
[project]
dependencies = [
    "numpy",
    "pandas",
    "scipy",
    "statsmodels",
    "scikit-learn",
    "matplotlib",
    "sovereign-debt-py @ git+https://github.com/zachessesjohnson/sovereign_debt_py.git",
]
```

**Via PyPI (once published)** — replace the git URL with the package name:

```toml
dependencies = [
    ...
    "sovereign-debt-py",
]
```

**Via git submodule** — useful if you always want both repos in sync locally:

```bash
# From the sovereign_debt_xl repo root:
git submodule add https://github.com/zachessesjohnson/sovereign_debt_py.git sovereign_debt_py
git commit -m "Add sovereign_debt_py as a git submodule"
```

---

## CI / test updates

### In the new `sovereign_debt_py` repository

Add `.github/workflows/pytest.yml` in the new repo:

```yaml
name: pytest

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install
        run: |
          python -m pip install -U pip
          pip install -e ".[dev]"

      - name: Test
        run: pytest -q
```

> **Note:** `sovereign_debt_py` does **not** use PyXLL, so no `conftest.py`
> mock is needed.  The `[dev]` extra (defined in its `pyproject.toml`) already
> includes `pytest`.

### In `sovereign_debt_xl` after switching to the external package

The existing CI workflow (`.github/workflows/pytest.yml`) installs dependencies
via `requirements.txt` and `pip install -e .`.  Once `sovereign_debt_py` is
listed in `pyproject.toml` as a dependency, installing with `pip install -e .`
will pull it in automatically — no workflow changes are required.

If you pin the git-URL form of the dependency and want CI to always use the
latest commit, add a manual cache-bust step or use the `--no-cache-dir` flag:

```yaml
- name: Install dependencies
  run: |
    python -m pip install -U pip
    pip install --no-cache-dir -e .
```

---

## Quick-reference checklist

- [ ] Create a new GitHub repo `sovereign_debt_py` (empty, public or private)
- [ ] Choose Option A (history preserved) or Option B (clean start) above and run the commands
- [ ] Add a `pyproject.toml` to the new repo (see template above)
- [ ] Verify the new repo builds: `pip install -e ".[dev]"` and `pytest -q`
- [ ] Add `.github/workflows/pytest.yml` to the new repo
- [ ] Declare the dependency in `pyproject.toml` of `sovereign_debt_xl` (git URL or PyPI name)
- [ ] Remove the `sovereign_debt_py/` directory and its entry from the `pyproject.toml` package discovery in `sovereign_debt_xl`
- [ ] Confirm `sovereign_debt_xl` CI still passes after the removal
