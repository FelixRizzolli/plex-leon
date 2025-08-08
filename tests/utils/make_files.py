from pathlib import Path
from typing import Iterable


def make_files(base: Path, names: Iterable[str]) -> list[Path]:
    paths = []
    for name in names:
        p = base / name
        if name.endswith('/'):
            p.mkdir(parents=True, exist_ok=True)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x")
        paths.append(p)
    return paths
