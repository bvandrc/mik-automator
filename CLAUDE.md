# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conventions

The repo's conventions live in `conventions/` and are imported here in full — they apply to all work in this repo, and everything below extends them. Keep this file consistent with them: nothing here should ever contradict a convention.

@conventions/all.md

`conventions/` is synced automatically from `bvandrc/bvandrc-conventions` by `.github/workflows/sync-conventions.yml`. The workflow deletes and recreates the directory on every run, so edits made here are lost — change them upstream. When a sync adds a new file to `conventions/`, add a matching `@conventions/<file>` import to this section.

## Commands

Requires Python 3.10+. The package only runs on Windows: it drives Mixed In Key's window, and pywin32 only installs there.

Work in the repo's `.venv` (gitignored), with the package installed editable so `mik_automator` imports resolve to `src/` rather than some other installed copy:

```bash
python -m venv .venv
source .venv/Scripts/activate        # Git Bash on Windows
pip install -e ".[dev]"              # dependencies + black, pylint, pyright
```

```bash
pylint $(git ls-files '*.py')        # lint (config in .pylintrc, most C/R checks disabled)
pyright                              # type check (config in pyproject.toml)
black .                              # format, line-length 120
```

This is a Python repo with no package manager scripts, so `black .` is the "format script" the conventions require before every commit; CI enforces it with `psf/black@stable`.

There's no test suite: everything here talks to a running Mixed In Key.

CI (`.github/workflows/ci.yml`) runs `Lint` (pylint and pyright, plus black once) on windows-latest across Python 3.10-3.15. Lint runs on every version because neither tool pins one: both check against the running interpreter, so 3.10 catches use of anything newer and later versions catch deprecations and removals.

The package isn't on PyPI. Consumers (like SD) install it from GitHub's `main`, so a merge to `main` is a release. Bump `version` in `pyproject.toml` and add a `CHANGELOG.md` entry for user-visible changes.

## Architecture

One module in the `mik_automator` package (`src/mik_automator/`), for Mixed In Key on Windows:

- `mik_automator.py` — `run(dir)` opens Mixed In Key (or connects to it), adds `dir`, waits for the analysis to finish, and closes it. It uses pywinauto's UIA backend. The Add Files button has no identifier, so it's clicked at its screen coordinates, scaled from 1920x1080, and the folder is picked by expanding the Browse For Folder tree, which is why `dir` has to be under the user dir. Analysis counts as done once closing the window doesn't bring up a confirmation.

## Repository layout notes

- `conventions/` — see [Conventions](#conventions) above; imported, not editable in place.
