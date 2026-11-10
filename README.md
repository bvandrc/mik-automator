Windows automator and database tools for Mixed In Key 11.

# Installation

```bash
pip install mik-automator
```

Windows only, Python 3.10+.

If you installed it from GitHub as `mixed-in-key-automator`, uninstall that first (`pip uninstall mixed-in-key-automator`): both install the `mik_automator` package, so keeping both leaves them overwriting each other's files.

# Usage

## `mik_automator`

Opens Mixed In Key (or connects to it if it's already open), adds a folder, waits for the analysis to finish, then closes it.

```python
from mik_automator import mik_automator

mik_automator.run(r"C:\Users\me\Music\DJ Tracks")
```

It knows the analysis is done once Mixed In Key's database stops changing and the window closes without asking to confirm.

## `mik_db`

Reads and edits Mixed In Key's database (`MIKStore.db`) directly.

- `rename_file(src, dest, names=None)`: points a song at its renamed file, so it keeps its analysis.
- `remove_files(filepaths)` and `remove_missing_files()`: remove songs, so they're analyzed again when added, or because their file is gone.
- `get_song_files()` and `get_files_missing_from_db(dir)`: read-only, safe while Mixed In Key is running.

Run `python -m mik_automator.mik_db` to remove the songs whose files no longer exist.

# Development

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -e ".[dev]"
```

Lint with `pylint $(git ls-files '*.py')` and `pyright`, and format with `isort .` then `black .`. CI checks all four on pull requests.

# License

[MIT](LICENSE)
