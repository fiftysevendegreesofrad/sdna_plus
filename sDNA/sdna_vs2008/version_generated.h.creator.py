import datetime
import pathlib
import sys
import subprocess

PARENT_DIR = pathlib.Path(__file__).parent
version_template = PARENT_DIR / 'version_template.h'
version_generated = PARENT_DIR / 'version_generated.h'

shell = (sys.platform != 'win32')

git_hash = subprocess.check_output('git rev-parse HEAD', shell = shell).decode('utf8').rstrip()

template_content = version_template.read_text()

content = template_content.replace('#GITHASH#', git_hash)

version_generated.write_text(content)