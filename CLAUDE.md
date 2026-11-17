# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conventions

The repo's conventions live in `conventions/` and are imported here in full — they apply to all work in this repo, and everything below extends them. Keep this file consistent with them: nothing here should ever contradict a convention.

@conventions/all.md
@conventions/python.md
@conventions/pypi-publishing.md

`conventions/` is synced automatically from `bvandrc/bvandrc-conventions` by `.github/workflows/sync-conventions.yml`. The workflow deletes and recreates the directory on every run, so edits made here are lost — change them upstream. When a sync adds a new file to `conventions/`, add a matching `@conventions/<file>` import to this section.

## Commands

Requires Python 3.11+. The package only runs on Windows: it drives Mixed In Key's window, and pywin32 only installs there.

Set up the `.venv`:

```bash
python -m venv .venv
source .venv/Scripts/activate        # Git Bash on Windows
pip install -e ".[dev]"              # dependencies + ruff, pyright
```

```bash
pyright                              # type check (config in pyproject.toml)
ruff check --fix .                   # lint, and sort imports (config in pyproject.toml)
ruff format .                        # format, line-length 120
```

There's no test suite: everything here talks to a running Mixed In Key or its database. Check `mik_db` changes against a copy of `MIKStore.db`, never the real one.

CI (`.github/workflows/ci.yml`) runs `Lint` (pyright, plus Ruff's lint and format checks once) on windows-latest across Python 3.11-3.15.

The package is on PyPI as `mik-automator`. Up to 1.0.1 it was `mixed-in-key-automator`, installed from GitHub; the import package is still `mik_automator`.

Releasing and the changelog follow `pypi-publishing.md`. Specific to this repo:
- **Trusted publisher:** PyPI's names `release.yml` and its `pypi` environment, so renaming either means updating it on PyPI too.
- **Unreleased:** changes not yet released go under `## [Unreleased]`, which a release renames to the version.

## Architecture

Two modules in the `mik_automator` package (`src/mik_automator/`), for Mixed In Key 11 on Windows:

- `mik_automator.py` — `run(dir)` opens Mixed In Key (or connects to it), adds `dir`, waits for the analysis to finish, and closes it.
  - **Window control:** pywinauto's UIA backend, and pywin32 window messages where UIA can't reach. The Browse For Folder dialog has no path box, so the folder is selected with `BFFM_SETSELECTIONW`, written into the dialog's process memory.
  - **Done:** analysis counts as done once the database has stopped changing and closing the window doesn't bring up a confirmation.
- `mik_db.py` — reads and edits `MIKStore.db` directly (a SQLite database under `%LOCALAPPDATA%`, path hard-coded to version `11.0`).
  - **Songs:** a song is keyed by its `File` path. `FilePathHash` has to match Mixed In Key's own hash (`get_file_path_hash`), or it won't recognize the song.
  - **Reads** open the database read-only, so they're safe while Mixed In Key is running.

## Repository layout notes

- `conventions/` — see [Conventions](#conventions) above; imported, not editable in place.
