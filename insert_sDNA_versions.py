# sDNA+ (c) Crispin Cooper on behalf of Cardiff University 2015

""" Populates version tags in text and Python files, matching: 
__version__ = "VERSION_PLACEHOLDER" with SDNA_VERSION from
./sDNA/sdna_vs2008/version_template.h
Please refer to adacent files or Git for the version of this 
file itself.  It does not actually get shipped in formally versioned 
.msi releases or wheels.
"""

import argparse
from pathlib import Path
import sys
import re


PARENT_DIR = Path(__file__).parent

def getVersion(
    version_file: Path | None = None,
    ) -> str:
    version_file = version_file or PARENT_DIR / "sDNA" / "sdna_vs2008" / "version_template.h"
    version = None
    version_line_num = None
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


def _replace_version_specifiers_in_scripts_files(
    version: str,
    target_dir: Path = PARENT_DIR / "output" / "release",
    ) -> None:

    sub_dirs = ["", "bin"]
    exclude = {"shapefile.py", "placeholder.txt"}
    target_exts = {".py", ".pyt", ".r", ".txt"} # must all be lower case to run on Windows.


    for sub_dir in sub_dirs:
        dir_ = target_dir / sub_dir
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

def _replace_version_specifier_in_advinst_config_file(
    version: str,
    file: Path = PARENT_DIR / "installerbits" / "advanced" / "sdna.aip",
    ) -> None:
    version_line_template = '    <ROW Property="ProductVersion" Value="{version}" Options="32"/>'
    old = version_line_template.format(version="1.0.0")
    new = version_line_template.format(version=version)
    pattern=version_line_template.format(version=r"\d+\.\d+\.\d+")

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
        "--version-file",
        type=Path,
    )
    parser.add_argument(
        "--scripts",
        type=Path,
    )
    parser.add_argument(
        "--advinst-config-file",
        type=Path,
    )

    args_namespace = parser.parse_args(args)
    version_file = getattr(args_namespace, "version_file", None)
    version = getVersion(version_file = version_file)

    if (scripts_target := getattr(args_namespace, "scripts", None)) is not None:
        print(f"Inserting {version=} into Python files in: {scripts_target} (and bin sub dir)...")
        _replace_version_specifiers_in_scripts_files(
            version=version,
            target_dir=scripts_target,
        )

    if (advinst_file := getattr(args_namespace, "advinst_config_file", None)) is not None:
        print(f"Inserting {version=} into Advanced Installer config file: {advinst_file}...")
        _replace_version_specifier_in_advinst_config_file(
            version=version,
            file = advinst_file,
        )

    print(f"{__file__} done. ")

    return 0

if __name__ == '__main__':
    sys.exit(main())
