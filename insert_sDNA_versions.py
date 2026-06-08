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


def _replace_version_specifiers_in_scripts_files(version: str) -> None:
    sub_dirs = ["", "bin"]
    exclude = {"shapefile.py", "placeholder.txt"}
    target_exts = {".py", ".pyt", ".r", ".txt"} # must all be lower case to run on Windows.


    for sub_dir in sub_dirs:
        dir_ = PARENT_DIR / "output" / "release" / sub_dir
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

def _replace_version_specifier_in_advinst_config_file(version: str) -> None:
    version_line_template = '    <ROW Property="ProductVersion" Value="{version}" Options="32"/>'
    old = version_line_template.format(version="1.0.0")
    new = version_line_template.format(version=version)
    pattern=version_line_template.format(version=r"\d+\.\d+\.\d+")

    file = PARENT_DIR / "installerbits" / "advanced" / "sdna.aip"
    lines = file.read_text().splitlines()

    matches = [(j, m) for j, line in enumerate(lines) if (m := re.match(pattern, line))]

    if not matches:
        raise Exception(f"Pattern: {pattern} not found in: {file}")

    if len(matches) >= 2:
        raise Exception(f"Multiple lines in {file} match pattern: {pattern}, {matches=}")

    i = matches[0][0]
    lines[i] = new
    lines.append("")

    file.write_text("\n".join(lines))

    

def main(args = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        prog = Path(__file__).name,
        description = "sDNA version updater build tool",
    )

    parser.add_argument(
        "targets",
        nargs='*',
        type=str,
        default="scripts",
    )

    args_namespace = parser.parse_args(args)    
    version = getVersion()

    if "scripts" in args_namespace.targets:
        _replace_version_specifiers_in_scripts_files(version)

    if "advinst-config-file" in args_namespace.targets:
        _replace_version_specifier_in_advinst_config_file(version)



    return 0

if __name__ == '__main__':
    sys.exit(main())

