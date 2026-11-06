# Changelog

Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-11-06

- `run` adds the folder without clicking screen coordinates or expanding the folder tree, so it works for any folder, not only ones under the user dir, at any screen resolution
- Remove `scale_coords`, `split_dir`, and `get_screen_resolution`, and make `get_mik_window` private
- Depends on pywin32 directly

## [0.2.0] - 2025-05-06

- `run` opens Mixed In Key, adds a folder under the user dir through its Add Files dialog, waits for the analysis to finish, and closes it
