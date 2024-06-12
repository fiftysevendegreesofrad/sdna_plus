# -*- coding: utf-8 -*-

import os
import os.path
import sys
import glob
import re
import math
import itertools
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

REPO_ROOT_DIR = os.path.join(os.path.dirname(__file__), r'..\..\..\..')

ON_WINDOWS = (sys.platform == 'win32')

SDNA_DLL_LOCATIONS = (
             os.path.join(REPO_ROOT_DIR, r'\output\Debug\x64\sdna_vs2008.dll'),
             os.path.join(REPO_ROOT_DIR, r'\output\release\x64\sdna_vs2008.dll'),
             r'C:\Program Files (x86)\sDNA\x64\sdna_vs2008.dll',
            )

SDNA_DLL = os.getenv('sdnadll', '')

SDNA_BIN_SUFFIXES = ('integral', 'prepare', 'learn', 'predict')

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


SDNA_BIN_DIR = os.getenv('sdna_bin_dir', '')
DEFAULT_TEST_SDNA_BIN = r'..\..\..\arcscripts\bin'

def is_sdna_bin_dir(dir_):
    if not os.path.isdir(dir_):
        return False
        
    return all(os.path.isfile(os.path.join(dir_,'sdna%s.py' % suffix))
               for suffix in SDNA_BIN_SUFFIXES
              )

if not SDNA_BIN_DIR:
    # .casefold is more aggressive and is best practise for 
    # caseless matching of strings -- but only as a native 
    # language speaking human would match those strings.  
    # .casefold would not distinguish between the two dirs: c:\ss 
    # and c:\ß (dir paths are case-insensitive on Windows, unlike Linux).
    if SDNA_DLL.lower().startswith(REPO_ROOT_DIR.lower()):
        dir_ = os.path.join(REPO_ROOT_DIR, 'arcscripts', 'bin')
        
        if not is_sdna_bin_dir(dir_):    
            raise Exception('Cannot find an sDNA binary directory '
                            '(containing sdnaintegral.py etc.) to test with the dll. '
                            r'Set %sdnadll% to the dll of a complete sDNA '
                            'installation, test in the source code repo, or'
                            r' set %SDNA_BIN_DIR%.'
                            )    
    else:
        # e.g. for SDNA_DLL == r'C:\Program Files (x86)\sDNA\x64\sdna_vs2008.dll'
        dir_ = os.path.join(os.path.dirname(SDNA_DLL),'..','bin') 
        if not is_sdna_bin_dir(dir_):
            raise Exception(
                "Could not find sDNA 'bin'/ python files"
                "associated with SDNA_DLL: %s. "
                "Set SDNA_BIN_DIR to the dir containing the "
                "sDNA 'bin'/python files to be tested "
                "(sdna+ %s +.py), or ensure  is part of a"
                "complete sDNA installation. "
                % (SDNA_DLL, SDNA_BIN_SUFFIXES, SDNA_DLL)
                )

    SDNA_BIN_DIR = dir_


print(r'Testing the sdnaintegral.py etc. in: %sdna_bin_dir%== ' + SDNA_BIN_DIR)


SDNA_DEBUG = bool(os.getenv('sdna_debug', ''))

print('SDNA_DEBUG: %s' % SDNA_DEBUG)


TMP_SDNA_DIR = os.path.join(tempfile.gettempdir(), 'sDNA', 'tests', 'pytest')



# Configure allowing regression tests to pass despite issue #20
# https://github.com/fiftysevendegreesofrad/sdna_plus/issues/20
DONT_TEST_N_LINK_SUBSYSTEMS_ORDER = bool(os.getenv('DONT_TEST_N_LINK_SUBSYSTEMS_ORDER', ''))

print('DONT_TEST_N_LINK_SUBSYSTEMS_ORDER: %s' % DONT_TEST_N_LINK_SUBSYSTEMS_ORDER)

N_LINK_SUBSYSTEMS_PATTERN = r'^(?P<N>\d+)-link subsystem contains link with id = (?P<id>\d+)$'

SUBSYSTEM_LINK_NUMS_NOT_TO_TEST_ORDER_OF = ('1', '3')



# Configure allowing regression tests to pass despite issue #21
# https://github.com/fiftysevendegreesofrad/sdna_plus/issues/21
ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT = bool(os.getenv('ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT', ''))

print('ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT: %s' % ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT)

NEGATIVE_FORMULA_ERROR_PATTERN = r'^ERROR: Formula evaluation gave negative result for link (?P<num>\d+)$'
NEGATIVE_FORMULA_ERROR_LINK_PRESENT_PATTERN = r'^Polyline (?P<num>\d+) id=(?P<id>\d+)$'



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

ENV = os.environ.copy()

ENV['sdnadll'] = SDNA_DLL


def batch_file_tests():
    for file_ in glob.glob(os.path.join(os.path.dirname(__file__), BATCH_FILES_GLOB)):
        if os.path.basename(file_) in {'colourdiff.bat',
                                       'mydiff.bat',
                                       'awkward_test.bat',
                                       'arc_script_test.bat',
                                       'run_tests_windows.bat',
                                       'sdnavars64.bat',
                                       'quick_test.bat', # Duplicates debug_test.py in pause_debug_test.bat
                                       'run_benchmark.bat'
                                      }:
            continue

        yield file_


def windows_test_commands():
    for file_ in batch_file_tests():
        with open(file_, 'rt') as f:
            for command in f:
                command = command.replace(r'%outputsuffix%', OUTPUT_SUFFIX)
                command = command.rstrip()

                for suffix in ['2>&1', '2>>&1', '2>>NUL', '2>NUL', '>NUL', '>NUL 2>NUL']:
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

    pipe_to = ''


    pseudo_files_to_pipe_output_to = collections.defaultdict(str)

    # overwrite == False => piped output is appended.
    overwrite_file_to_pipe_output_to = False


    def __init__(self, command_str = '', target_dir='.'):
        
        self.unparsed_str = command_str


        args = re.split(r'([,=;"> ])', command_str)

        for i in range(len(args)):
            # Don't test if each arg is file like or not, 
            # just clobber all of them.
            new_arg = fix_path_seps(args[i])
            new_arg = path_to_file_in_dir_if_it_exists_there(new_arg, dir_ = target_dir)
            args[i] = new_arg

        command_str = ''.join(args)


        if '>' in command_str:

            command_str, __, file_ = command_str.rpartition('>')
            if command_str[-1] == '>':
                command_str = command_str[:-1]
            else:
                self.overwrite_file_to_pipe_output_to = True
                
            self.pipe_to = file_

        self.command_str = command_str


        self.run_result = None


    def run(self):
        tmp_output = self._run()

        if self.pipe_to is not None:
            if self.overwrite_file_to_pipe_output_to:
                self.pseudo_files_to_pipe_output_to[self.pipe_to] = tmp_output
            else:
                self.pseudo_files_to_pipe_output_to[self.pipe_to] += tmp_output


    def __str__(self):
        return '<%s, pipe_to: %s>' % (self.__class__.__name__, self.pipe_to)


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


    def _run(self):
        if self.retcode_zero_expected:
            return _run_insecurely_in_shell_without_catching_exceptions(self.command_str)

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

        # Support testing the released Python files shipped with 
        # sdna_vs2008.dll, not the source code repo's Python files 
        # at '..\..\..\arcscripts\bin'
        if SDNA_BIN_DIR and (DEFAULT_TEST_SDNA_BIN in self.python_file):
            self.python_file = self.python_file.replace(DEFAULT_TEST_SDNA_BIN, SDNA_BIN_DIR)






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
        

    def _run(self):
        return self.output_str + '\n'


class ReadsTextInputFile(Command):
    # sub class constructors must set: self.input_file
    # and sub classes must define: self._run_using_input(input_)

    def _run(self):
        
        return self._run_using_input(self.pseudo_files_to_pipe_output_to[self.input_file])


class SedCommand(ReadsTextInputFile):
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

        self.input_file = os.path.basename(input_file)

    def __str__(self):
        return '<%s, input: %s>' % (super(SedCommand, self).__str__()[1:-1], self.input_file)

    def _run_using_input(self, output_so_far):

        tmp_file = os.path.join(TMP_SDNA_DIR, 'input_for_sed_command_buffer.txt')
        # try:
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
        # finally:
        os.unlink(tmp_file)

        return output


class CatCommand(Command):
    def __init__(self, command_str, **kwargs):
        super(CatCommand, self).__init__(command_str, **kwargs)


        assert self.command_str.startswith('cat ')
        self.input_file = self.command_str.partition('cat ')[2].strip()
        
    def _run(self):
        with open(self.input_file, 'rt') as f:
            return f.read()

NUM_PATTERN = r'([+-]?\d+(\.\d*)?([eE][+-]?\d+)?)'

def almost_equal(a, b, abs_tol = 2e-15):
    # Whereas "0.000001E-17" != "0.0"
    # almost_equal("0.000001E-17", "0.0") is True

    last_a = 0
    last_b = 0

    matches_a = re.finditer(NUM_PATTERN, a)
    matches_b = re.finditer(NUM_PATTERN, b)

    while True:

        match_a = next(matches_a, None)
        match_b = next(matches_b, None)

        if match_a is None and match_b is None:
            return a[last_a:] == b[last_b:]

        if not (match_a and match_b):
            print('match_a: %s, match_b: %s' % (match_a, match_b))
            return False

        
        start_a = match_a.start(0)
        start_b = match_b.start(0)

        if a[last_a:start_a] != b[last_b:start_b]:
            
            print('a[last_a:start_a]: %s,  b[last_b:start_b]: %s' 
                 % (a[last_a:start_a],  b[last_b:start_b]))
            return False

        
        last_a = match_a.end(0)
        last_b = match_b.end(0)

        if abs(float(match_a.group(0)) - float(match_b.group(0))) > abs_tol:
            print('float(match_a.group(0)): %s, float(match_b.group(0)): %s' 
                 % (float(match_a.group(0)), float(match_b.group(0))))
            return False

        





class DiffCommand(ReadsTextInputFile):

    def __init__(self, command_str, **kwargs):
        super(DiffCommand, self).__init__(command_str, **kwargs)

        match = re.match(r'.*diff.* (?P<expected>.*correctout.*\.txt) (?P<actual>.*testout.*\.txt)\s*', self.command_str)

        # print('Expected: %s, actual: %s' % (match.group('expected'), match.group('actual')))

        self.expected_output_file = match.group('expected')
        
        self.input_file = match.group('actual')

    def _run_using_input(self, output_so_far):
        # print('Expected: %s, actual: %s' % (self.expected_output_file, self.input_file))
        buffer_size = 10
        actual_buffer = collections.deque([], maxlen=buffer_size)
        expected_buffer = collections.deque([], maxlen=buffer_size)

        # with open('pytest_diff_output.txt', 'wt') as f:
        #     f.write(output_so_far)

        # print('self.pseudo_files_to_pipe_output_to: %s\n' % self.pseudo_files_to_pipe_output_to)

        if DONT_TEST_N_LINK_SUBSYSTEMS_ORDER:
            actual_n_link_subsystems = collections.defaultdict(collections.Counter)
            expected_n_link_subsystems = collections.defaultdict(collections.Counter)

        if ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT:
            link_num_with_negative_formula_error = None
            error_on_non_existent_link = False

        with open(self.expected_output_file, 'rt') as f:
            if SDNA_DEBUG:
                expected_lines = f
            else:
                expected_lines = filter_out_debug_only_output.filter_out_matches(f)

            # expected = ''
            # print('Num of lines in actual output: %s' % len(output_so_far.splitlines()))
            # print('output_so_far: %r' % output_so_far[:50])
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
                                                        ),
                                                    start=1
                                                   ):

                expected, actual = expected.rstrip().lstrip('\r'), actual.rstrip().lstrip('\r')


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
                

                if DONT_TEST_N_LINK_SUBSYSTEMS_ORDER and 'testout_prep_' in self.input_file:

                    match_n_link_actual = re.match(N_LINK_SUBSYSTEMS_PATTERN, actual) 
                    match_n_link_expected = re.match(N_LINK_SUBSYSTEMS_PATTERN, expected)

                    if (match_n_link_actual and match_n_link_expected and 
                        (match_n_link_actual.group('N') == match_n_link_expected.group('N')) and
                        match_n_link_actual.group('N') in SUBSYSTEM_LINK_NUMS_NOT_TO_TEST_ORDER_OF):
                        #
                        num_links = match_n_link_actual.group('N')

                        # add to Counters, to be tested for equality at end
                        actual_n_link_subsystems[num_links].update([match_n_link_actual.group('id')])
                        expected_n_link_subsystems[num_links].update([match_n_link_expected.group('id')])
                        continue

                if ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT and 'correctout.txt' == self.expected_output_file:
                    
                    # Require that negative formula errors are only raised for links that exist.
                    if error_on_non_existent_link:
                        match_neg_formula_link_present = re.match(NEGATIVE_FORMULA_ERROR_LINK_PRESENT_PATTERN, actual)

                        if (match_neg_formula_link_present and
                            str(link_num_with_negative_formula_error) == match_neg_formula_link_present.group('num')):
                            #
                            error_on_non_existent_link = False

                    match_neg_formula_actual = re.match(NEGATIVE_FORMULA_ERROR_PATTERN, actual)
                    match_neg_formula_expected = re.match(NEGATIVE_FORMULA_ERROR_PATTERN, expected)
                

                    if (match_neg_formula_actual and match_neg_formula_expected):

                        # Handle any uncleared previous negative formula error on a non-existing link
                        # (no link found before the next negative formula error). 
                        assert not error_on_non_existent_link, "Negative formula error raised on non-existent link: %s" % link_num_with_negative_formula_error
                            
                        link_num_with_negative_formula_error = match_neg_formula_actual.group('num')
                        error_on_non_existent_link = True

                        continue




                # imitate "sed s/_%outputsuffix%//g <%2 >%2.fordiff.txt" from mydiff.bat
                if 'mydiff' in self.command_str:
                    actual = actual.replace('_%s' % OUTPUT_SUFFIX, '')

                actual_buffer.append(repr(actual))
                expected_buffer.append(repr(expected))

                if 'sDNA is running in ' in actual:
                    if actual.startswith('Progress:') and actual.endswith('-bit mode'):
                        actual = ''.join(actual.partition('sDNA is running in ')[1:])

                assert almost_equal(actual, expected), '[101mError[0m on line num i: %s.  This line (and up to the %s previous ones):\nExpected: %s, \n\n Actual: %s' % (i+1, buffer_size - 1,'\n'.join(expected_buffer), '\n'.join(actual_buffer))
                # assert actual == expected, 'i: %s, Expected: "%s", Actual: "%s"' % (i, expected, actual)
                prev_expected = expected
                m += 1

            assert m >= 1, 'm==%s lines tested from: %s. output_so_far: %s.  Raising AssertionError to avoid false positive. This test should be fixed!! ' % (m, self.pipe_to, output_so_far)

            if DONT_TEST_N_LINK_SUBSYSTEMS_ORDER:
                for N in SUBSYSTEM_LINK_NUMS_NOT_TO_TEST_ORDER_OF:
                    actual_counter, expected_counter = actual_n_link_subsystems[N], expected_n_link_subsystems[N]

                    assert actual_counter == expected_counter, ("Num links in subsytem: %s\n, Expected - Actual: %s, \n\nActual - Expected: %s" % 
                                                                (N,
                                                                 expected_counter - actual_counter, 
                                                                 actual_counter - expected_counter
                                                                ))

            if ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT:
                assert not error_on_non_existent_link, "Negative formula error raised on non-existent link at: %s." % match_neg_formula_actual.group(0)

            print('[92mPassed![0m Num of equal expected & actual lines": %s. (Num lines skipped: %s exc debug etc.)' % (m,i-m))


        return output_so_far


    def __str__(self):
        return '<%s, input: %s, expected: %s>' % (super(DiffCommand, self).__str__()[1:-1], self.input_file, self.expected_output_file) 





    
class DiffTest(object):
    def __init__(self, commands):

        steps, diff_command = commands[:-1], commands[-1]
        assert all(isinstance(step, Command) for step in steps)
        assert isinstance(diff_command, DiffCommand)

        self.steps = steps
        self.diff_command = diff_command

    def run(self):
        for step in self.steps:
            # piped output is passed via Command.pseudo_files_to_pipe_output_to,
            # not via retvals.
            step.run()
        
        self.diff_command.run()

    def __str__(self):
        sep = ',\n' + ' ' * (len(self.expected_output_file) + 4)
        return '%s:  [%s%s%s]\n' % (
                              self.expected_output_file,
                              sep.join(str(step) for step in self.steps),
                              sep,
                              str(self.diff_command)
                             ) 

    @property
    def expected_output_file(self):
        return self.diff_command.expected_output_file

def commands_generator_factory():
    for command in windows_test_commands():

        if is_python_command(command):
            if any(('sdna%s.py' % suffix) in command 
                       for suffix in SDNA_BIN_SUFFIXES):
                yield sDNACommand(command)
            else:
                yield PythonScriptCommand(command)
        
        elif command.startswith('echo '):
            yield EchoCommand(command)
        
        elif command.startswith('sed '):
            yield SedCommand(command)

        elif command.startswith('cat '):
            yield CatCommand(command)

        elif 'diff' in command:
            yield DiffCommand(command)
        #else: raise Exception('Could not process command: %s' % command)


def sequential_diff_tests():
    diff_test_commands = []

    for command in commands_generator_factory():

        diff_test_commands.append(command)

        if isinstance(command, DiffCommand):
            yield DiffTest(diff_test_commands)
            diff_test_commands = []


diff_tests = list(sequential_diff_tests())
diff_test_expected_files = [diff_test.diff_command.expected_output_file 
                            for diff_test in diff_tests
                           ]


@pytest.mark.parametrize('diff_test', diff_tests, ids = diff_test_expected_files)
def test_diff_(diff_test):
    diff_test.run()


if __name__=='__main__':

    s = set()

    for f in batch_file_tests():
        with open(f,'rt') as f:
            for l in f:
                first_word = l.partition(' ')[0]
                s.add(first_word)



   


    if len(sys.argv) == 1:
        for diff_test in diff_tests:
            diff_test.run()
    else:
        try:
            test_index = int(sys.argv[1])
            diff_test = diff_tests[test_index]
        except:
            diff_test = next(diff_test
                             for diff_test in diff_tests
                             if sys.argv[1] in diff_test.expected_output_file
                            )

        print(diff_test)

        diff_test.run()