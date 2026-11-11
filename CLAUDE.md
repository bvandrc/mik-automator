# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conventions

The repo's conventions live in `conventions/` and are imported here in full — they apply to all work in this repo, and everything below extends them. Keep this file consistent with them: nothing here should ever contradict a convention.

@conventions/all.md

`conventions/` is synced automatically from `bvandrc/bvandrc-conventions` by `.github/workflows/sync-conventions.yml`. The workflow deletes and recreates the directory on every run, so edits made here are lost — change them upstream. When a sync adds a new file to `conventions/`, add a matching `@conventions/<file>` import to this section.

## Commands

Requires Python 3.11+. The package only runs on Windows: it drives Mixed In Key's window, and pywin32 only installs there.

Work in the repo's `.venv` (gitignored), with the package installed editable so `mik_automator` imports resolve to `src/` rather than some other installed copy:

```bash
python -m venv .venv
source .venv/Scripts/activate        # Git Bash on Windows
pip install -e ".[dev]"              # dependencies + black, isort, pylint, pyright
```

```bash
pylint $(git ls-files '*.py')        # lint (config in .pylintrc, most C/R checks disabled)
pyright                              # type check (config in pyproject.toml)
isort .                              # sort imports (config in pyproject.toml)
black .                              # format, line-length 120
```

This is a Python repo with no package manager scripts, so `isort .` then `black .` is the "format script" the conventions require before every commit; CI checks both.

There's no test suite: everything here talks to a running Mixed In Key or its database. Check `mik_db` changes against a copy of `MIKStore.db`, never the real one.

CI (`.github/workflows/ci.yml`) runs `Lint` (pylint and pyright, plus isort and black once) on windows-latest across Python 3.11-3.15. Lint runs on every version because neither tool pins one: both check against the running interpreter, so 3.11 catches use of anything newer and later versions catch deprecations and removals.

The package is on PyPI as `mik-automator` (it was `mixed-in-key-automator`, installed from GitHub, up to 1.0.1); the import package is still `mik_automator`. A merge to `main` isn't a release on its own. To release, bump `version` in `pyproject.toml`, add a `CHANGELOG.md` entry for user-visible changes, merge, then publish a GitHub release tagged `v<version>` (e.g. `gh release create v1.2.0 --title v1.2.0 --notes ""`). Publishing it runs `Release` (`.github/workflows/release.yml`), which checks the tag matches the version, builds, and uploads to PyPI through trusted publishing, so the repo holds no PyPI token. A release published with empty notes gets the version's `CHANGELOG.md` section as its notes, and the built distributions are attached to it. PyPI's trusted publisher names that workflow file and its `pypi` environment, so renaming either means updating it on PyPI too.

End every sentence of a changelog entry with a period, the last one included, so an entry of two sentences doesn't end one with a period and not the other.

PyPI never accepts the same version twice, even after a release is deleted, so a bad upload means a new version.

## Architecture

Two modules in the `mik_automator` package (`src/mik_automator/`), for Mixed In Key 11 on Windows:

- `mik_automator.py` — `run(dir)` opens Mixed In Key (or connects to it), adds `dir`, waits for the analysis to finish, and closes it. It uses pywinauto's UIA backend for the window, and pywin32 window messages where UIA can't reach: the Browse For Folder dialog has no path box, so the folder is selected with `BFFM_SETSELECTIONW`, written into the dialog's process memory. Analysis counts as done once the database has stopped changing and closing the window doesn't bring up a confirmation.
- `mik_db.py` — reads and edits `MIKStore.db` (a SQLite database under `%LOCALAPPDATA%`, path hard-coded to version `11.0`) directly. A song is keyed by its `File` path; `FilePathHash` has to match Mixed In Key's own hash (`get_file_path_hash`), or it won't recognize the song. Reads open the database read-only, so they're safe while Mixed In Key is running.

## Repository layout notes

- `conventions/` — see [Conventions](#conventions) above; imported, not editable in place.
