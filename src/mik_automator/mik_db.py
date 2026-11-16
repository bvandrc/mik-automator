import glob
import hashlib
import os
import sqlite3
from collections.abc import Collection
from contextlib import closing, contextmanager
from pathlib import Path
from typing import TypedDict

appdata_dir = os.getenv("LOCALAPPDATA")
assert appdata_dir, "local appdata"
db_file = os.path.join(appdata_dir, "Mixed In Key", "Mixed In Key", "11.0", "MIKStore.db")

AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".aif", ".aiff", ".m4a")


class ArtistTitle(TypedDict):
    artist: str
    title: str


@contextmanager
def connect():
    """Opens the MIK database, committing on success and always closing."""
    connection = sqlite3.connect(db_file)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def get_song_files() -> set[str]:
    """Returns every song's path, lowercased. Opens read-only, so it's safe while Mixed In Key is running."""
    with closing(sqlite3.connect(f"{Path(db_file).as_uri()}?mode=ro", uri=True)) as connection:
        return {row[0].lower() for row in connection.execute("SELECT File FROM Song")}


def get_files_missing_from_db(dir: str) -> list[str]:
    song_files = get_song_files()
    files = (f for f in glob.iglob(os.path.join(dir, "**", "*"), recursive=True) if os.path.isfile(f))
    return [f for f in files if os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS and f.lower() not in song_files]


def get_file_path_hash(filepath: str, disk_serial: str) -> str:
    """Same as Mixed In Key's: paths are tied to the disk, so they still match if the drive letter changes."""
    id_string = f"{disk_serial}:{filepath.split(':', 1)[1]}" if disk_serial.strip() else filepath
    return hashlib.md5(id_string.lower().encode("utf-8")).hexdigest().upper()


def rename_file(src: str, dest: str, names: ArtistTitle | None = None) -> bool:
    """Points a song at its renamed file, so it keeps its analysis. Returns whether the song was found.

    Pass names when known, since filenames lose characters ("RÜFÜS DU SOL" is "RUFUS DU SOL"). Otherwise they come
    from the filename, which must be "Artist - Title", as the file's tags may not be updated yet."""
    if names is None:
        filename = os.path.splitext(os.path.basename(dest))[0]
        try:
            artist, title = filename.split(" - ", 1)
        except ValueError as e:
            raise ValueError(f"couldn't parse {filename} as Artist - Title") from e
        names = {"artist": artist, "title": title}

    with connect() as connection:
        row = connection.execute("SELECT DiskSerialNumber FROM Song WHERE File = ?", (src,)).fetchone()
        if row is None:
            return False
        # src's file replaced whatever was at dest, so that song's row would be a duplicate
        if src != dest:
            connection.execute("DELETE FROM Song WHERE File = ?", (dest,))
        connection.execute(
            "UPDATE Song SET File = ?, FilePathHash = ?, ArtistName = ?, SongName = ? WHERE File = ?",
            (dest, get_file_path_hash(dest, row[0]), names["artist"], names["title"], src),
        )
    return True


def remove_files(filepaths: Collection[str]):
    if len(filepaths) == 0:
        return
    with connect() as connection:
        connection.executemany("DELETE FROM Song WHERE File = ?", [(filepath,) for filepath in filepaths])


def remove_missing_files() -> list[str]:
    """Removes songs whose file no longer exists. Skips files on drives that aren't connected. Returns the removed paths."""
    with connect() as connection:
        filepaths = [row[0] for row in connection.execute("SELECT File FROM Song")]

    missing = [f for f in filepaths if os.path.exists(os.path.splitdrive(f)[0] + os.sep) and not os.path.exists(f)]
    remove_files(missing)
    return missing


if __name__ == "__main__":
    removed = remove_missing_files()
    for filepath in removed:
        print(filepath)
    print(f"Removed {len(removed)} missing files")
