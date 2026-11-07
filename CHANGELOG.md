# Changelog

Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-11-07

- Published to PyPI as `mik-automator`: install with `pip install mik-automator`. It was `mixed-in-key-automator`, installed from GitHub; uninstall that first, since both install the `mik_automator` package. Imports don't change.
- Licensed under MIT

## [1.0.1] - 2026-11-06

- Don't crash when the "Adding files to queue" popup is gone before it's checked, or when a control errors as it closes
- Importing the package no longer looks up Mixed In Key's exe

## [1.0.0] - 2026-11-06

### Breaking

- Only supports Mixed In Key 11: `run` watches its database to know when the analysis is done

### Features

- Add `mik_db`, which reads and edits Mixed In Key 11's database: `rename_file` points a song at its renamed file so it keeps its analysis, and `remove_files` / `remove_missing_files` remove songs
- `run` waits for the database to go quiet before closing Mixed In Key, and only counts it as closed once its window is gone

## [0.3.0] - 2026-11-06

- `run` adds the folder without clicking screen coordinates or expanding the folder tree, so it works for any folder, not only ones under the user dir, at any screen resolution
- Remove `scale_coords`, `split_dir`, and `get_screen_resolution`, and make `get_mik_window` private
- Depends on pywin32 directly

## [0.2.0] - 2025-05-06

- `run` opens Mixed In Key, adds a folder under the user dir through its Add Files dialog, waits for the analysis to finish, and closes it
