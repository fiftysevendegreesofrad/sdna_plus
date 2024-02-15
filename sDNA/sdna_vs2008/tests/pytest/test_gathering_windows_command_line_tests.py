# -*- coding: utf-8 -*-

import os
import os.path
import sys
import glob
import re
import subprocess
import collections
import tempfile

import pytest

import filter_out_debug_only_output

PYTHON_3 = sys.version_info >= (3,)

try:
    import arcpy
    NO_ARCPY = False
except ImportError:
    NO_ARCPY = True

OUTPUT_SUFFIX = 'py%s' % sys.version_info[0]

ON_WINDOWS = (sys.platform == 'win32')

SDNA_DLL_LOCATIONS = (
             os.path.join(os.path.dirname(__file__), r'..\..\..\..\output\Debug\x64\sdna_vs2008.dll'),
             os.path.join(os.path.dirname(__file__), r'..\..\..\..\output\release\x64\sdna_vs2008.dll'),
             r'C:\Program Files (x86)\sDNA\x64\sdna_vs2008.dll',
            )

SDNA_DLL = os.getenv('sdnadll', '')

if not SDNA_DLL:
    for sdna_dll_path in SDNA_DLL_LOCATIONS:
        if os.path.isfile(sdna_dll_path):
            SDNA_DLL = sdna_dll_path
            break
    else:
        raise Exception(r'Env variable %sdnadll% not set, and no sdna_vs2008.dll found in locations: \n%s' % 
                        '\n'.join(SDNA_DLL_LOCATIONS)
                       )


print('SDNA_DLL: %s' % SDNA_DLL)


SDNA_DEBUG = bool(os.getenv('sdna_debug', ''))

print('SDNA_DEBUG: %s' % SDNA_DEBUG)


TMP_SDNA_DIR = os.path.join(tempfile.gettempdir(), 'sDNA', 'tests', 'pytest')

DONT_TEST_N_LINK_SUBSYSTEMS_ORDER = bool(os.getenv('DONT_TEST_N_LINK_SUBSYSTEMS_ORDER', ''))

print('DONT_TEST_N_LINK_SUBSYSTEMS_ORDER: %s' % DONT_TEST_N_LINK_SUBSYSTEMS_ORDER)

N_LINK_SUBSYSTEMS_PATTERN = r'(?P<N>\d+)-link subsystem contains link with id = (?P<id>\d+)'

SUBSYSTEM_LINK_NUMS_NOT_TO_TEST_ORDER_OF = ('1', '3')

if not os.path.isdir(TMP_SDNA_DIR):
    os.makedirs(TMP_SDNA_DIR)
# Python3 only: os.makedirs(TMP_SDNA_DIR, exist_ok=True)

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

# I don't know why on earth the behaviours on Python 2.7 are different when a) running
#  under Pytest 4.6.11 versus b) compared to when running this file as a script, 
# (especially when the glob is an absolute dir/pattern reference defined from __file__)
# but they are, and neither Python 2, nor Pytest versions that support Python 2 are 
# accepting fixes.
BATCH_FILES_GLOB = '*.bat' if (__name__=='__main__' and not PYTHON_3) else '../*.bat' 


def batch_file_tests():
    for file_ in glob.glob(os.path.join(os.path.dirname(__file__), BATCH_FILES_GLOB)):
        if os.path.basename(file_) in {'colourdiff.bat',
                                       'mydiff.bat',
                                       'awkward_test.bat',
                                       'arc_script_test.bat',
                                       'run_tests_windows.bat',
                                       'sdnavars64.bat',
                                       'quick_test.bat', # Duplicates debug_test.py in pause_debug_test.bat
                                      }:
            continue

        yield file_


def windows_test_commands():
    for file_ in batch_file_tests():
        with open(file_, 'rt') as f:
            for command in f:
                command = command.replace(r'%outputsuffix%', OUTPUT_SUFFIX)
                command = command.rstrip()

                for suffix in ['2>&1', '2>>&1', '2>>NUL', '2>NUL', '>NUL']:
                    if command.endswith(suffix):
                        command = command[:-len(suffix)].rstrip()
                
                yield command




def is_python_command(command):
    return command.lstrip().startswith('%pythonexe%')


def windows_python_test_commands():
    for command in windows_test_commands():
        # .startswith meands commands that set env vars before running
        # python are skipped.
        if is_python_command(command):
            yield command




def fix_path_seps(path_str):
    # Windows inputs only. Not a good idea to split on escape char on Posix
    return os.path.join(*path_str.split('\\'))

def path_to_file_in_dir_if_it_exists_there(path_str, dir_='.', exts = ('', '.shp')):
    if dir_ == '.':
        return path_str

    # Absolute paths will break this
    file_in_dir = os.path.join(dir_, path_str)
    for ext in exts:
        if os.path.isfile(file_in_dir + ext):
            return file_in_dir
    return path_str



class Command(object):
    # Require output file name of each diff test to be unique.  Probably no bad thing
    # to enforce well-designed, independent tests.  And tracking a list of lists of 
    # commands could be nightmareish to debug.  But this is a limitation.
    file = None

    pseudo_files_state = collections.defaultdict(list)

    pseudo_files_to_pipe_output_to = collections.defaultdict(str)

    # overwrite == False => piped output is appended.
    overwrite_file_to_pipe_output_to = False

    def register_file_mutation(self, file_):
        self.mutates.append(file_)

        # mutates the shared, class-wide variable, not an instance variable.
        self.pseudo_files_state[file_].append(self)


    # def __init__(self, command_str = '', mutates = None, requires = None, target_dir='..'):
    def __init__(self, command_str = '', mutates = None, requires = None, target_dir='.'):
        
        self.mutates = mutates or []
        self.requires = requires or []
        self.unparsed_str = command_str


        args = re.split(r'([,=;"> ])', command_str)

        for i in range(len(args)):
            # Don't test if each arg is file like or not, 
            # just clobber all of them.
            new_arg = fix_path_seps(args[i])
            new_arg = path_to_file_in_dir_if_it_exists_there(new_arg, dir_ = target_dir)
            args[i] = new_arg

            # if 'hybrid' in arg:
            #     print('arg: %s, new_arg: %s' % (arg, new_arg))

        command_str = ''.join(args)


        if '>' in command_str:

            command_str, __, file_ = command_str.rpartition('>')
            if command_str[-1] == '>':
                command_str = command_str[:-1]
            else:
                self.overwrite_file_to_pipe_output_to = True
                
            self.register_file_mutation(file_)
            self.file = file_

        self.command_str = command_str

        # if 'hybrid_test.py' in self.command_str:
        #     print('command: %s' % self.command_str)

        self.run_result = None


    @classmethod
    def _run_file_mutating_commands(cls, file_, input_ = ''):
        commands = cls.pseudo_files_state[file_]

        if not isinstance(commands, str):

            output = input_
            prev_output_file = None

            # Main command runner
            for command in commands:
                
                if command.file is None or command.file != prev_output_file:
                    output = input_
                
                output = command.run(output)

                if command.file is not None:
                    if command.overwrite_file_to_pipe_output_to:
                        cls.pseudo_files_to_pipe_output_to[command.file] = output
                    else:
                        cls.pseudo_files_to_pipe_output_to[command.file] += output

                prev_output_file = command.file

            # Memoise result of running (replaces commands).
            cls.pseudo_files_state[file_] = output

        return cls.pseudo_files_state[file_]

    # We assume each batch file only runs once, so cache the stdout & stderr.   
    # But multiple commands therein might be affected by a mutation to a file 
    # from a previous command.
    def run(self, output_so_far = ''):
        # if self.command_str.startswith('sed'):
        if self.run_result is None:

            output_from_requires = ''

            for required_file in self.requires:
                # Don't pass output_so_far to previous commands that produce a required file
                output_from_requires = self._run_file_mutating_commands(required_file)
                if required_file == self.file:
                    output_so_far = output_so_far or output_from_requires

            # output_so_far = output_so_far or self.pseudo_files_to_pipe_output_to.get(self.file, None)

            print('Running command type: %s, file: %s, .bat command: %s\n, requires: %s\n, mutates: %s\n\n' % 
                                    (self.__class__, self.file, self.unparsed_str, self.requires, self.mutates))

            tmp_output = self._run(output_so_far)

            if self.overwrite_file_to_pipe_output_to:
                output_so_far = tmp_output
            else:
                output_so_far += tmp_output

            self.run_result = output_so_far

        return self.run_result


def _run_insecurely_in_shell_without_catching_exceptions(command_str):

    output = subprocess.check_output(
            command_str,
            env=ENV,
            shell=True,
            stderr=subprocess.STDOUT,
            )
    return output.decode('ascii')


class PythonCommand(Command):

    def __init__(self, command_str, retcode_zero_expected = False, **kwargs): 
        super(PythonCommand, self).__init__(command_str, **kwargs)




        self.retcode_zero_expected = retcode_zero_expected


        args_to_python = self.command_str.lstrip()

        for prefix in ['%pythonexe%', '-u', '-m']:

            if args_to_python.startswith(prefix):
                args_to_python = args_to_python[len(prefix):].lstrip()

        self.args_to_python = args_to_python

        self.command_str = self.command_str.replace(r'%pythonexe%', sys.executable)


    def _run(self, output_so_far):
        # print('self.command_str: %s' % self.command_str)
        if self.retcode_zero_expected:
            return output_so_far + _run_insecurely_in_shell_without_catching_exceptions(self.command_str)

        try:
            return _run_insecurely_in_shell_without_catching_exceptions(self.command_str)

        except subprocess.CalledProcessError as e:
            return e.output.decode('ascii')



class PythonScriptCommand(PythonCommand):

    def __init__(self, command_str, **kwargs): 
        super(PythonScriptCommand, self).__init__(command_str, **kwargs)

        assert '.py' in self.args_to_python, self.args_to_python
        py_file, __, args_to_py_file = self.args_to_python.lstrip().partition('.py')

        py_file += '.py'

        # Don't support python -c
        if not os.path.isfile(py_file):
            raise Exception('Test command: %s references non-existent Python script: %s'
                           % (command_str, py_file)
                           )   


        self.python_file = os.path.basename(py_file)
        self.args_to_python_file = args_to_py_file


class sDNACommand(PythonScriptCommand):

    sdna_dll_cli_arg = ('"%s"' % SDNA_DLL) if ' ' in SDNA_DLL else SDNA_DLL

    def __init__(self, command_str, **kwargs): 
        super(sDNACommand, self).__init__(command_str, **kwargs)


        self.command_str = self.command_str.replace(r'%sdnadll%', self.sdna_dll_cli_arg)

        for pattern in [r' --om "net=(\S*)"', r' -o (\S*) ']:
            for file_ in re.findall(pattern, self.command_str):

                # shp2txt.py is called with file names only, 
                # it appends '.shp' itself, so remove any .shp here.
                # (so that this sDNACommand can be run from a
                #  later Shp2TxtCommand on which it depends)
                # sDNA accepts shapefile names without '.shp's
                if file_.endswith('.shp'):
                    file_ = file_[:-4]

                self.register_file_mutation(file_)


class Shp2TxtCommand(PythonScriptCommand):
    def __init__(self, command_str, **kwargs): 
        super(Shp2TxtCommand, self).__init__(command_str, **kwargs)

        for pattern in self.args_to_python_file.split(' '):
            if pattern and not pattern.isspace():

                # TODO: Account for:
                # The globs passed to shp2txt.py
                # may refer to files that only exist at
                # shp2txt.py's run time (e.g. only once
                # created by a previous statement in a
                # source batch file), that may not yet exist
                # at the time of batch file parsing and pytest
                # test gathering.
                if pattern[-1] == '*':
                    pattern = pattern[:-1]

                self.requires.append(pattern)

    # def _run(self, output_so_far):
    #     retval = super(Shp2TxtCommand, self)._run(output_so_far)

    #     print('Shp2Txt, output_so_far: %r' % output_so_far)
    #     return retval


def python_command_and_pytest_param_decorator_factory(windows_command):

    retval, deco = sDNACommand(windows_command), None

    match = re.match(r'%\w+%',retval.command_str)
    if match:
        raise Exception('Unconverted Windows environment variable: %s in test command: [[ %s ]]' % (match, retval.command_str))
    

    # if retval.python_file == 'benchmark_dll.py':
    #     if os.getenv('RUN_BENCHMARK', False):
    #         # https://github.com/fiftysevendegreesofrad/sdna_plus/issues/11
    #         deco = lambda x: pytest.param(x, marks=pytest.mark.skipif(PYTHON_3, reason = 'Issue 11.  Access violation on Python 3'))

    # elif retval.python_file == 'awkward_test.py':
    #     deco = lambda x: pytest.param(x, marks=pytest.mark.skipif(NO_ARCPY, reason = 'Imports arcpy, which is not available'))

    return retval, deco


def python_commands_and_pytest_params():
    for windows_command in windows_python_test_commands():
        


        py_command, deco = python_command_and_pytest_param_decorator_factory(windows_command)

        if py_command is None:
            continue

        if deco is not None:
            yield deco(py_command)
            continue

        yield py_command

ENV = os.environ.copy()
ENV['sdnadll'] = SDNA_DLL

# @pytest.mark.parametrize('command',list(python_commands_and_pytest_params()))
# def test_command(command):

#     # This try/except block is the easiest way I can think of
#     # to use a high level subprocess function (i.e. without directly
#     # working with Popen), 
#     # that does pretty much the same as the modern helper
#     # subprocess.run (from Python >=3.5), that works in both
#     # Python 2 and 3.
#     #
#     # try:
#     output = subprocess.check_output(
#                     command.command_str,
#                     env=ENV,
#                     shell=True,
#                     stderr=subprocess.STDOUT,
#                     )
#     # except subprocess.CalledProcessError as e:
#         # pass
#     # Some of the tests are expected to return codes != 0
#     # 
#     #
#     # Even though only subprocess.CalledProcessError is allowed to pass,
#     # it is now important to add some assert statements that actually 
#     # test something (or add More Tests!) to avoid false confidence from 
#     # 'tests' that all trivially pass, that cannot be failed.  Or treat the
#     # expected failures differently and ditch this try/except.




class EchoCommand(Command):
    def __init__(self, command_str, **kwargs):
        super(EchoCommand, self).__init__(command_str, **kwargs)
        assert self.command_str.startswith('echo ')
        self.output_str = self.command_str[5:].strip()
        

    def _run(self, output_so_far):
        return self.output_str + '\n'



class SedCommand(Command):
    def __init__(self, command_str, **kwargs):
        super(SedCommand, self).__init__(command_str, **kwargs)


        assert self.command_str.startswith('sed ')
        after_sed = self.command_str[4:]

        # Sed commands containing whitespace will break this
        sed_command, __, input_file = after_sed.strip().partition(' ')

        # De-quote
        if sed_command[0] == sed_command[-1] in ('"', "'"):
            sed_command = sed_command[1:-1]

        self.sed_command = sed_command

        self.requires.append(input_file)



    def _run(self, output_so_far):

        tmp_file = os.path.join(TMP_SDNA_DIR, 'input_for_sed_command_buffer.txt')
        try:
            with open(tmp_file,'wt') as f:
                f.write(output_so_far)

                # The inefficiency of calling out, keeps the test(s) the same as before, 
                # as far as possible.  And avoids inserting Python 'sed' 
                # code into the existing sDNA tests.

                # cmd.exe treats single quotes the same as any other character, 
                # but e.g. on bash, double quotes can trigger expansions, but
                # single quotes are a literal string.
            quote = '' if ON_WINDOWS else "'"
            sed_command = ''.join([quote, self.sed_command, quote])


            output = _run_insecurely_in_shell_without_catching_exceptions(
                            'sed %s <%s' % (sed_command, tmp_file)
                            )

            # print('Sed output: %s' % output)
        finally:
            os.unlink(tmp_file)

        return output




class DiffCommand(Command):

    def __init__(self, command_str, **kwargs):
        super(DiffCommand, self).__init__(command_str, **kwargs)

        match = re.match(r'.*diff.* (?P<expected>.*correctout.*\.txt) (?P<actual>.*testout.*\.txt)\s*', self.command_str)

        # print('Expected: %s, actual: %s' % (match.group('expected'), match.group('actual')))

        self.expected_output_file = match.group('expected')
        
        self.requires.append(match.group('actual'))

        self.file = match.group('actual')

    def _run(self, output_so_far):
        # print('Expected: %s, actual: %s' % (self.expected_output_file, self.file))
        buffer_size = 10
        actual_buffer = collections.deque([], maxlen=buffer_size)
        expected_buffer = collections.deque([], maxlen=buffer_size)

        # with open('pytest_diff_output.txt', 'wt') as f:
        #     f.write(output_so_far)

        print('self.pseudo_files_to_pipe_output_to: %s\n' % self.pseudo_files_to_pipe_output_to)
        # print('self.pseudo_files_state: %s' % self.pseudo_files_state)

        if DONT_TEST_N_LINK_SUBSYSTEMS_ORDER:
            actual_n_link_subsystems = collections.defaultdict(collections.Counter)
            expected_n_link_subsystems = collections.defaultdict(collections.Counter)

        with open(self.expected_output_file, 'rt') as f:
            if SDNA_DEBUG:
                expected_lines = f
            else:
                expected_lines = filter_out_debug_only_output.filter_out_matches(f)

            # expected = ''
            # print('Num of lines in actual output: %s' % len(output_so_far.splitlines()))
            print('output_so_far: %r' % output_so_far[:50])
            # actual_lines = iter(output_so_far.splitlines())
            # sDNA prepends Progress and other strings with '\r' (in 
            # SdnaShapefileEnvironment calls) which .splitlines splits on,
            # so split explicitly on '\n' and .strip afterwards
            actual_lines = iter(output_so_far.split('\n'))
            m = 0

            def de_progress(str_):
                return re.split(r'Progress: 1?\d?\d(\.\d)?%', str_)[-1]

            def tuples_of_nontrivial_nonProgress_strings(*iterables):
                iterators = [iter(iterable) 
                             for iterable in iterables
                            ]
                return zip(*[(de_progress(str_)
                              for str_ in iterator 
                              if de_progress(str_).strip()
                             )
                             for iterator in iterators
                            ]
                          )



            prev_expected = ''
            i=0
            for i, (expected, actual) in enumerate(tuples_of_nontrivial_nonProgress_strings(
                                                        expected_lines,
                                                        output_so_far.split('\n'),
                                                        )
                                                   ):

                expected, actual = expected.rstrip(), actual.rstrip()

                # if prev_expected.startswith('Progress') and not expected:
                # continue
                # actual = next(actual_lines)
                # if not expected:
                #     continue
                # for j, actual in actual_lines:
                #     if actual:
                #         break


                # print('Expected: %s, \n\nActual: %s' % (expected, actual))

                # Allow the result of a test, requiring most of 
                # of correctout_prepbarns.txt to be exactly the same, 
                # to not depend on that one line out of the 17855 lines,
                # that requires the exact same environment variable value, 
                # as in the environment the file was created.  
                if expected.startswith("dll is"):
                    continue

                # Can't capture this string from env for some reason?
                if expected.startswith("sDNA processing"):
                    continue
                

                if DONT_TEST_N_LINK_SUBSYSTEMS_ORDER and 'testout_prep_' in self.file:

                    match_actual = re.match(N_LINK_SUBSYSTEMS_PATTERN, actual) 
                    match_expected = re.match(N_LINK_SUBSYSTEMS_PATTERN, expected)

                    if (match_actual and match_expected and 
                        (match_actual['N'] == match_expected['N']) and
                        match_actual['N'] in SUBSYSTEM_LINK_NUMS_NOT_TO_TEST_ORDER_OF):
                        #
                        actual_n_link_subsystems[match_actual['N']].update([match_actual['id']])
                        expected_n_link_subsystems[match_expected['N']].update([match_expected['id']])
                        continue

                # if actual.startswith('Progress: '):
                #     continue

                # imitate "sed s/_%outputsuffix%//g <%2 >%2.fordiff.txt" from mydiff.bat
                if 'mydiff' in self.command_str:
                    actual = actual.replace('_%s' % OUTPUT_SUFFIX, '')

                actual_buffer.append(actual)
                expected_buffer.append(expected)

                if 'sDNA is running in ' in actual:
                    if actual.startswith('Progress:') and actual.endswith('-bit mode'):
                        actual = ''.join(actual.partition('sDNA is running in ')[1:])

                assert actual == expected, '[101mError[0m on line num i: %s.  This line (and up to the %s previous ones):\nExpected: "%s", \n\n Actual: "%s"' % (i, buffer_size - 1,'\n'.join(expected_buffer), '\n'.join(actual_buffer))
                # assert actual == expected, 'i: %s, Expected: "%s", Actual: "%s"' % (i, expected, actual)
                prev_expected = expected
                m += 1

            assert m >= 1, 'm==%s lines tested from: %s. output_so_far: %s.  Raising AssertionError to avoid false positive. This test needs should be fixed!! ' % (m, self.file, output_so_far)

            if DONT_TEST_N_LINK_SUBSYSTEMS_ORDER:
                for N in SUBSYSTEM_LINK_NUMS_NOT_TO_TEST_ORDER_OF:
                    actual_counter, expected_counter = actual_n_link_subsystems[N], expected_n_link_subsystems[N]

                    assert actual_counter == expected_counter, ("Num links in subsytem: %s\n, Expected - Actual: %s, \n\nActual - Expected: %s" % 
                                                                (N,
                                                                 expected_counter - actual_counter, 
                                                                 actual_counter - expected_counter
                                                                ))

            print('[92mPassed![0m Num of equal expected & actual lines": %s. (Num lines skipped: %s exc debug etc.)' % (m,i-m))


        return output_so_far




def command_and_decorator_factory(command_str):

    if is_python_command(command_str):
        if 'shp2txt.py' in command_str:
            return Shp2TxtCommand(command_str), None
        else:
            return python_command_and_pytest_param_decorator_factory(command_str)
    
    if command_str.startswith('echo '):
        return EchoCommand(command_str), None
    
    if command_str.startswith('sed'):
        return SedCommand(command_str), None

    if 'diff' in command_str:
        return DiffCommand(command_str), None
        # raise Exception('Could not process command: %s' % command_str)

    return None, None



def diff_tests_and_pytest_params():

    pytest_param_decorators = {}
    diff_tests = {}

    for command_str in windows_test_commands():

        command, deco = command_and_decorator_factory(command_str)

        if command is None or not hasattr(command, 'file'):
            continue
            # raise Exception('Unclassifiable command %s' % command_str)

        file_ = command.file

        if isinstance(command, DiffCommand):
            diff_tests[file_] = command

        if deco is not None:
            pytest_param_decorators[file_] = deco

    # print("pseudo_file_state['testout_py3.txt']: %s" % Command.pseudo_files_state['testout_py3.txt'])

    # print('diff_tests: %s' % diff_tests)

    # print({file_: commands
    #        for file_, commands in Command.pseudo_files_state.items()
        #    if any(x in file_ for x in ['testout_learn_']) #, 'table'])
        #    if any(isinstance(command, DiffCommand) for command in commands)
        #   })

    for file_, diff_test in diff_tests.items():
            
        if file_ in pytest_param_decorators:
            yield pytest_param_decorators[file_](diff_test)
            continue

        yield diff_test


diff_tests = list(diff_tests_and_pytest_params())
diff_test_expected_files = [diff_test.expected_output_file for diff_test in diff_tests]


@pytest.mark.parametrize('diff_test', diff_tests, ids = diff_test_expected_files)
def test_diff_(diff_test):
    diff_test.run()

    



if __name__=='__main__':

    s = set()

    for f in batch_file_tests():
        with open(f,'rt') as f:
            for l in f:
                # first_word = l.split(maxsplit=1)[0] if ' ' in l else l
                first_word = l.partition(' ')[0]
                s.add(first_word)

    # print('Set of initial batch file commands: %s' % s)

    # print('Batch files: \n%s' % '\n'.join(
    #                             os.path.basename(f) 
    #                             for f in batch_file_tests()
    #                             )
    #      )
    # print('\n\n  Windows test commands: \n%s' % '\n'.join(windows_test_commands()))
    # print('\n\n  Python test commands for this platform: \n%s' % '\n\n'.join(command.command_str for command in commands()))

    # print('\n\n Test files for diffing: %s\n' % diff_tests)
    # print('\n\n Diffing test commands: %s\n' % [command.command_str for command in diff_tests])

    # print('diff_test_expected_files: %s' % diff_test_expected_files)

    # print('Hybrid command_strs: %s' % '\n'.join([str((command, vars(command))) for commands in Command.pseudo_files_state.values()
    #                                                        for command in commands
    #                                                        if 'hybrid_test.py' in command.command_str ]))

    # print('patterns: %s' % '\n'.join(SDNA_DEBUG_STATEMENT_PREFIX_PATTERNS))

   


    if len(sys.argv) == 1:
        diff_test = diff_tests[8]
    else:
        try:
            test_index = int(sys.argv[1])
            diff_test = diff_tests[test_index]
        except:
            diff_test = next(diff_test
                             for diff_test in diff_tests
                             if sys.argv[1] in diff_test.expected_output_file
                            )

    print('Testing expected: %s' % diff_test.expected_output_file)
    diff_test.run()