import os
import sys
import subprocess
import pathlib
import dataclasses
import shutil

# https://discuss.python.org/t/custom-build-steps-moving-bokeh-off-setup-py/16128/3
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

REPO_DIR = pathlib.Path(__file__).parent
BUILD_CONFIG_CMAKE = 'Release'

for __init__dot_py_dir in [REPO_DIR / 'output' / BUILD_CONFIG_CMAKE,
                            REPO_DIR / 'output' / BUILD_CONFIG_CMAKE / 'bin',
                            ]:
    __init__dot_py_dir.mkdir(exist_ok = True, parents=True)
    (__init__dot_py_dir / '__init__.py').touch(exist_ok=True)


@dataclasses.dataclass
class Config:
    build_dir: str
    generator: str
    use_zig: str
    shell: bool
    output_dir: str
    build_config: str = 'Release'


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name not in ('wheel', 'bdist'):
            return

        config = Config('build_output_hatch',
                        '"Ninja Multi-Config"',
                        'OFF',
                        True,
                        'Release'
                       )


        build_dir = pathlib.Path(config.build_dir)

        build_dir = REPO_DIR / build_dir

        env = os.environ.copy()

        env['VCPKG_INSTALLATION_ROOT']='/root/vcpkg'

        subprocess.run(f"""
            cmake
                -G {config.generator}
                -D USE_ZIG={config.use_zig}
                -B {build_dir}
                -S .
            """.replace('\n',''),
            shell=config.shell,
            env=env,
        )

        subprocess.run(f"""
            cmake --build build_output_cmake_zig --config Release
            """.replace('\n',''),
            shell=config.shell
        )


    # def finalize(self, version, build_data, artifact_path):
    #     pass

    
        