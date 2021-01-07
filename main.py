from os import walk, stat, listdir
import sys
import re
from stat import *


class Arguments:
    search_from = ''
    search_for_contents = None
    search_by_perm = (False, 0)

    find_empty_dirs = False
    case_sensitive = False

    find_dirs = False
    find_files = False

    min_size = 0
    max_size = sys.maxsize


def regexify(string, ignore_case):
    current_sequence = ''
    regex = ''

    if string[0] != '*':
        regex += '^'

    for char in string:
        if char == '*':
            if current_sequence:
                regex += '(' + current_sequence + ').*'
            else:
                regex += '.*'
            current_sequence = ''
        else:
            if ignore_case:
                current_sequence += char.lower()
            else:
                current_sequence += char

    if current_sequence:
        regex += '(' + current_sequence + ')$'

    return regex


def save_args():
    if len(sys.argv) < 4:
        print('Invalid Number of Arguments. Provide find start directory and what to look for')
        exit(0)

    Arguments.search_from = sys.argv[1]

    try:
        for arg_index in range(1, len(sys.argv)):
            if sys.argv[arg_index] == '-name':
                print(sys.argv[3])
                Arguments.search_for_contents = regexify(sys.argv[arg_index + 1], True)

            if sys.argv[arg_index] == '-iname':
                Arguments.search_for_contents = regexify(sys.argv[arg_index + 1])
                Arguments.case_sensitive = True

            if sys.argv[arg_index] == '+':
                Arguments.min_size = int(sys.argv[arg_index + 1])

            if sys.argv[arg_index] == '-':
                Arguments.max_size = int(sys.argv[arg_index + 1])

            if sys.argv[arg_index] == '-f':
                Arguments.find_files = True

            if sys.argv[arg_index] == '-d':
                Arguments.find_dirs = True

            if sys.argv[arg_index] == '-empty':
                Arguments.find_empty_dirs = True

            if sys.argv[arg_index] == '-p':
                Arguments.search_by_perm = (True, sys.argv[arg_index + 1])

        if not Arguments.find_files and not Arguments.find_dirs and not Arguments.find_empty_dirs:
            Arguments.find_files = True
            Arguments.find_dirs = True
            Arguments.find_empty_dirs = True
    except IndexError as BadFormatting:
        print('Bad Format of Arguments')
        exit(0)


def parse_directory():
    entries = []
    print(Arguments.search_for_contents)
    for root, dirs, files in walk(Arguments.search_from):
        if Arguments.find_dirs or Arguments.find_empty_dirs:
            for directory in dirs:
                if re.match(Arguments.search_for_contents, directory):
                    entries.append((root, directory))
        if Arguments.find_files:
            for file in files:
                if re.match(Arguments.search_for_contents, file):
                    entries.append((root, file))

    filtered_entries = [entry for entry in entries]

    for entry in entries:
        st = stat(entry[0])

        if not Arguments.min_size <= st.st_size <= Arguments.max_size:
            if entry in filtered_entries:
                filtered_entries.remove(entry)

        if Arguments.find_empty_dirs and not Arguments.find_dirs:
            if not listdir(entry[0]):
                if entry in filtered_entries:
                    filtered_entries.remove(entry)

        if Arguments.search_by_perm[0]:
            if not oct(st.st_mode)[4:] == str(Arguments.search_by_perm[1]):
                if entry in filtered_entries:
                    filtered_entries.remove(entry)

    return filtered_entries


if __name__ == '__main__':
    save_args()

    results = parse_directory()
    for entry in results:
        print(f'\t{entry[0]}: {entry[1]}')
