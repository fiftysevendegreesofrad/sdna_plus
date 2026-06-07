import argparse
from pathlib import Path
import re


PARENT_DIR = Path(__file__).parent

def getVersion() -> str:
    version = None
    version_line_num = None
    version_file = Path(__file__).parent / "sDNA" / "sdna_vs2008" / "version_template.h"
    for i, line in enumerate(version_file.read_text().splitlines())
        m = re.match(r'^const char \*SDNA_VERSION = "(.*)";.*', line)
        if m:
            if version:
                raise Exception(
                    f"Multiple repeated (or ambiguous!!) version specifiers found!  Set one only. \n"
                    f"Already got {version=} from previous match on line num: {version_line_num}. "
                    "Second match found on line: {i} \n"
                    "line: {line}".
                )
            version = m.group(1)
            version_line_num = i
    return version


def _insert_version_info(file: Path, version: str) -> None:
    lines = []
    old_lines = iter(file.read_text("rt").splitlines())

    for line in old_lines:
        if not line.startswith("#"):
            break
        lines.append(line)
    if not lines:
        lines.append("# sDNA+ (c) Crispin Cooper on behalf of Cardiff University 2015")
        lines.append("")

    lines.append(f'__version__ = "{version}"')

    if line.strip():
        lines.append("")
    lines.append(line)
    lines.extend(old_lines)

    file.write_text("\n".join(lines))

def main()
    parser = argparse.ArgumentParser(
        name = Path(__file__).name
        description = "sDNA version updater build tool"
    )

    parser.add_argument(
        "dir",
        type=Path,
        default=PARENT_DIR / "output" / "release",
    )
    args_namespace = parser.parse_args(args)    

    sub_dirs = ["", "bin"]
    exclude = {"shapefile.py"}
    target_exts = {".py", ".pyt", ".r", ".txt"}

    version = getVersion()

    for sub_dir in sub_dirs:
        dir_ = args_namespace.dir / sub_dir
        for file in dir_.iterdir():
            if file.name.lower() in exclude:
                continue
            if file.suffix.lower() not in target_exts:
                continue
            _insert_version_info(file, version)

