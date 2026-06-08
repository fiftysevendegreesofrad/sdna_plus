import argparse
from pathlib import Path
import sys
import re


PARENT_DIR = Path(__file__).parent

def getVersion() -> str:
    version = None
    version_line_num = None
    version_file = PARENT_DIR / "sDNA" / "sdna_vs2008" / "version_template.h"
    for i, line in enumerate(version_file.read_text().splitlines()):
        m = re.match(r'^const char \*SDNA_VERSION = "(.*)";.*', line)
        if m:
            if version:
                raise Exception(
                    f"Multiple repeated (or ambiguous!!) version specifiers found!  Set one only. \n"
                    f"Already got {version=} from previous match on line num: {version_line_num}. "
                    "Second match found on line: {i} \n"
                    "line: {line}. "
                )
            version = m.group(1)
            version_line_num = i
    return version


# sDNA+ (c) Crispin Cooper on behalf of Cardiff University 2015

__version__ = "VERSION_PLACEHOLDER"

def _insert_version_info(file: Path, version: str) -> None:
    line = ""
    prefix = "__version__ = "
    lines = [
        f'{prefix}"{version}"' if line.startswith(prefix) else line
        for line in file.read_text().splitlines()
    ]
    file.write_text("\n".join(lines))

def main(args = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        prog = Path(__file__).name,
        description = "sDNA version updater build tool",
    )

    parser.add_argument(
        "--target",
        type=Path,
        default=PARENT_DIR / "output" / "release",
    )
    args_namespace = parser.parse_args(args)    

    sub_dirs = ["", "bin"]
    exclude = {"shapefile.py", "placeholder.txt"}
    target_exts = {".py", ".pyt", ".r", ".txt"} # must all be lower case to run on Windows.

    version = getVersion()

    for sub_dir in sub_dirs:
        dir_ = args_namespace.target / sub_dir
        if not dir_.is_dir():
            continue
        for file in dir_.iterdir():
            if not file.is_file():
                continue
            if file.name.lower() in exclude:
                continue
            if file.suffix.lower() not in target_exts:
                continue
            _insert_version_info(file, version)

    return 0

if __name__ == '__main__':
    sys.exit(main())

