# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make test                                        # run all tests
make lint                                        # ruff check src/
pytest tests/test_sift.py::test_name -v         # run a single test
pip install -r requirements.txt                  # install test dependencies
```

## Development Environment

This project uses a containerized dev environment built with Podman. The image is based on Python 3.12 and includes Claude Code, lazygit, and zellij.

```bash
make dev        # build image and drop into a bash shell
make dev-ui     # build image and launch the zellij UI (lazygit + claude + shell)
make dev-image  # build the image only
```

The zellij layout (`.zellij/dev.kdl`) splits the terminal into: lazygit on the left, claude agent + a shell on the right.

A VS Code devcontainer is also available (`.devcontainer/devcontainer.json`) using the same Python 3.12 base with Node and Claude Code features.

## Project

- **Language:** Python 3.12
- **Formatter:** Black (format-on-save in VS Code/devcontainer)
- **Linter:** Ruff (`.ruff_cache/` is gitignored)
- **Test runner:** pytest (dependencies in `requirements.txt`)

## Architecture

`src/sift` is a single executable Python script (no `.py` extension, shebang `#!/usr/bin/env python3`). It is stdlib-only (`argparse`, `pathlib`, `shutil`).

Core functions:
- `discover_files(src)` — returns all files under `src` via `rglob`
- `move_files(src, dest)` — moves each file to its mirrored path under `dest`, skipping files that already exist there

`tests/conftest.py` loads `src/sift` as an importable module (using `SourceFileLoader`) so unit tests can import its functions directly despite the missing `.py` extension.
