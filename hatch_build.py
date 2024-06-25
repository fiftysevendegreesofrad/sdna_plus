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
    build_config: str = 'Release'
    generator_path: str = ''
    platform: str = 'x64'

PLATFORM = 'Windows' if sys.platform=='win32' else 'Linux'

CONFIGS = {'Linux' : Config(
                        'build_output_hatchling_linux',
                        '"Ninja Multi-Config"',
                        'OFF',
                        True,
                        'Release',
                        '/usr/bin/ninja'
                       ),
           'Windows' : Config(
                        'build_output_hatchling_windows',
                        '"Visual Studio 17 2022"',
                        'OFF',
                        False,
                        'Release',
                        '/usr/bin/ninja'
                       ),
          }

class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name not in ('wheel', 'bdist'):
            return

        config = CONFIGS[PLATFORM]


        build_dir = pathlib.Path(config.build_dir)

        build_dir = REPO_DIR / build_dir

        env = os.environ.copy()

        env.setdefault('VCPKG_INSTALLATION_ROOT','~/vcpkg')

        config_command_str = f"""
                cmake
                -G {config.generator}
                -D USE_ZIG={config.use_zig}
                -B {build_dir}
                -S .
            """.lstrip().replace('\n','')

        if PLATFORM == 'Windows' and config.platform:
            config_command_str += f' -A {config.platform}'
        else:
            config_command_str += f' -D CMAKE_MAKE_PROGRAM={config.generator_path}'


        subprocess.run(
            config_command_str,
            shell=config.shell,
            env=env,
        )

        subprocess.run(f"""
            cmake --build {build_dir} --config {config.build_config}
            """.lstrip().replace('\n',''),
            shell=config.shell
        )


    # def finalize(self, version, build_data, artifact_path):
    #     pass

    
        