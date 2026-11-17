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
pip install -e ".[dev]"              # dependencies + ruff, pyright
```

```bash
pyright                              # type check (config in pyproject.toml)
ruff check --fix .                   # lint, and sort imports (config in pyproject.toml)
ruff format .                        # format, line-length 120
```

This is a Python repo with no package manager scripts, so `ruff check --fix .` then `ruff format .` is the "format script" the conventions require before every commit; CI checks both.

There's no test suite: everything here talks to a running Mixed In Key or its database. Check `mik_db` changes against a copy of `MIKStore.db`, never the real one.

CI (`.github/workflows/ci.yml`) runs `Lint` (pyright, plus Ruff's lint and format checks once) on windows-latest across Python 3.11-3.15.
- **Lint on every version:** pyright checks against the running interpreter, so 3.11 catches use of anything newer and later versions catch deprecations and removals. Ruff checks against `requires-python` instead, so it runs once.
- **Ruff's rules and version:** `pyproject.toml` selects every stable rule (`ALL`) and ignores, each with its reason, those that don't fit. For a one-off finding that's right as it is, silence it on its line with `# noqa: RULE` and a reason, rather than adding to that list. Ruff is pinned below its next minor version (`ruff>=0.17,<0.18` in the `dev` extra), since only a minor release adds stable rules or changes the formatting. So moving to a new minor version is its own PR, deciding for each new rule whether to fix what it flags or ignore it.

The package is on PyPI as `mik-automator`. Up to 1.0.1 it was `mixed-in-key-automator`, installed from GitHub; the import package is still `mik_automator`.

**Releasing:** a merge to `main` isn't a release on its own. To release, bump `version` in `pyproject.toml`, add a `CHANGELOG.md` entry for user-visible changes, merge, then publish a GitHub release tagged `v<version>` (e.g. `gh release create v1.2.0 --title v1.2.0 --notes ""`). Publishing it runs `Release` (`.github/workflows/release.yml`):
- **Build:** it checks the tag matches the version and builds.
- **Notes:** the release's notes are set to the version's `CHANGELOG.md` section, replacing any written on it.
- **Publish:** it uploads to PyPI through trusted publishing, so the repo holds no PyPI token, and attaches the built distributions to the release. PyPI's trusted publisher names that workflow file and its `pypi` environment, so renaming either means updating it on PyPI too.
- **Shared steps:** its build and release-notes steps are shared actions from [bvandrc-conventions](https://github.com/bvandrc/bvandrc-conventions) (`.github/actions/`), used from `main`, so change them there. Only the publish step stays in this file, since PyPI's trusted publishing matches the workflow file that runs it.
- **Versions are final:** PyPI never accepts the same version twice, even after a release is deleted, so a bad upload means a new version.

**Changelog entries:**
- **Sentences:** end every sentence of an entry with a period, the last one included, so an entry of two sentences doesn't end one with a period and not the other.
- **Headings:** a new version's heading is `## [x.y.z] - YYYY-MM-DD`, with a link definition added at the top of the list at the bottom of the file, comparing the previous version's tag with its own (`[x.y.z]: https://github.com/bvandrc/mik-automator/compare/v<previous>...vx.y.z`). The link 404s until the release creates the tag.
- **Unreleased:** changes not yet released go under `## [Unreleased]`, whose link compares the latest tag with `HEAD`. At a release, rename that heading to the version and point its link at the new tag.
- **PRs:** entries don't name PRs, since one often spans several; the compare link lists them, and `git blame` leads from an entry to its PR.

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
