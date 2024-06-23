import os
import sys
import subprocess
import pathlib
import dataclasses
import shutil

# https://discuss.python.org/t/custom-build-steps-moving-bokeh-off-setup-py/16128/3
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

REPO_DIR = pathlib.Path(__file__).parent
PYTHON_LIB_SRC_DIR = REPO_DIR / 'src'
PYTHON_LIB_SDNA_DIR = PYTHON_LIB_SRC_DIR / 'sDNA'
BUILD_CONFIG_CMAKE = 'Release'

@dataclasses.dataclass
class Config:
    build_dir: str
    generator: str
    use_zig: str
    shell: bool
    output_dir: str
    build_config: str = 'Release'

PYTHON_LIB_SDNA_DIR.mkdir(parents = True, exist_ok = True)

class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name not in ('wheel', 'bdist'):
            return


        for __init__dot_py_dir in [PYTHON_LIB_SDNA_DIR,
                                   PYTHON_LIB_SDNA_DIR / 'bin',
                                  ]:
            __init__dot_py = __init__dot_py_dir / '__init__.py'
            __init__dot_py.touch()


        config = Config('build_output_hatch',
                        '"Ninja Multi-Config"',
                        'OFF',
                        True,
                        'Release'
                       )


        build_dir = pathlib.Path(config.build_dir)

        build_dir = REPO_DIR / build_dir

        subprocess.run(f"""
            cmake
                -G {config.generator}
                -D USE_ZIG={config.use_zig}
                -B {build_dir}
                -S .
            """.replace('\n',''),
            shell=config.shell
        )

        subprocess.run(f"""
            cmake --build build_output_cmake_zig --config Release
            """.replace('\n',''),
            shell=config.shell
        )

        shutil.move(REPO_DIR / 'output' / config.output_dir, PYTHON_LIB_SRC_DIR) 

        (PYTHON_LIB_SRC_DIR / config.output_dir).rename(PYTHON_LIB_SRC_DIR / 'sDNA')

    def finalize(self, version, build_data, artifact_path):

        build_data['force_include']["output/Release"]="sDNA"

        shutil.rmtree(PYTHON_LIB_SDNA_DIR)
    
        