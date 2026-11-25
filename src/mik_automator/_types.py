import os
from typing import TypeAlias

# What the functions that take a path accept: a str, or a pathlib.Path or other path object
StrPath: TypeAlias = str | os.PathLike[str]
