import subprocess


version_template = r'version_template.h'
version_generated = r'version_generated.h'

git_hash = subprocess.check_output('git rev-parse HEAD').decode('utf8').rstrip()

with open(version_template, 'rt') as f:
    template_content = f.read()

content = template_content.replace('#GITHASH#', git_hash)

with open(version_generated, 'wt') as f:
    f.write(content)