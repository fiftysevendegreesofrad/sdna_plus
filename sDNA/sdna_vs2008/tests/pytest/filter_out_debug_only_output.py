from __future__ import print_function

import os
import sys
import re
import glob

glob_pattern = os.path.join(os.path.dirname(__file__), '..','..','*.[c,h]*')

def debug_statements():
    for file_ in glob.glob(glob_pattern):
        # print(os.path.basename(file_))
        with open(file_, 'rt') as f:
            lines = iter(f)
            for line in lines:
                if not re.match(r'\s*#ifdef _SDNADEBUG.*', line):
                    continue

                statements = []

                for line in lines:
                    if re.match(r'\s*#(endif|else)', line):
                        break
                    statements.append(line)

                yield statements

def debug_prefix_patterns():

    yield "partial edge called length="

    for lines in debug_statements():

        for line in lines:
            match = re.match(r'^\s*(std::)?cout << (?P<rest>.*)\s*$', line)
            if match:
                rest = match.group('rest')

                if any(rest.startswith(prefix) for prefix in ['"discarded"', '"rerouted"']):
                    continue

                debug_outputs = re.split(r' << ', rest)

                pattern_parts = []

                # first, print_all = True, False

                for output in debug_outputs:
                    if not output:
                        continue
                    if output[-1] == ';':
                        output = output[0:-1]
                    if output[0] == '"' == output[-1]:
                        # pattern_parts.append(re.escape(output[1:-1]))
                        pattern_parts.append(output[1:-1])
                    elif pattern_parts and (pattern_parts[0] == "moving link "):
                        break
                    elif 'endl' not in output:
                        pattern_parts.append(r'\d*\.?\d+([eE][+-]?\d+)?')
                    #     if first:
                    #         print_all = True
                    # first = False
                

                pattern = ''.join(pattern_parts)


                # if print_all:
                #     print('pattern: %s\npattern_parts: %s\n outputs: %s\nrest: %s' % 
                #           (pattern, pattern_parts, debug_outputs, rest))

                if pattern: 
                    yield pattern

SDNA_DEBUG_STATEMENT_PREFIX_PATTERNS = tuple(debug_prefix_patterns())


def filter_out_matches(lines, patterns = SDNA_DEBUG_STATEMENT_PREFIX_PATTERNS):
    for line in lines:
        # line = line.rstrip()

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if line.startswith("full"):
                    print('line: %s, pattern: %s' % (line, pattern))
                    raise Exception
                break

        if not match:
            yield line


if __name__ == '__main__':

    if len(sys.argv) >= 2:
        with open(sys.argv[1], 'rt') as f:
            for line in filter_out_matches(f):
                print(line)

        sys.exit(0)
    # print('Glob for source files: %s' % glob_pattern)

    # print('Debug statements behind #ifdef _SDNADEBUG from source files: \n%s'  % 
    #       '\n'.join(list(''.join(statement) for statement in debug_statements())))

    list(debug_prefix_patterns())

    # print('Debug prefix patterns (from first statement starting with "cout <<"): ')
    # for pattern in debug_prefix_patterns():
    #     print(len(pattern))