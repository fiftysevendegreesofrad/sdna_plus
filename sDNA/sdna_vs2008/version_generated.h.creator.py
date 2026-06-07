import pathlib
import subprocess

PARENT_DIR = Path(__file__).parent
version_template = PARENT_DIR / 'version_template.h'
version_generated = PARENT_DIR / 'version_generated.h'

git_hash = subprocess.check_output('git rev-parse HEAD').decode('utf8').rstrip()

template_content =  version_template.read_text()

content = template_content.replace('#GITHASH#', git_hash)

# Overwrites any existing file.
version_generated.write_text(content)