'''
File: analyze_structure.py
Author: Gavin Vogt
This program will analyze a file structure. It allows the user to select various
options that modify its behavior. The most important modifier is the -r option,
which tells the program to recurse through all subdirectories of the given directory.
If the directory name is not specified, it defaults to use the current working
directory.

Usage: analyze_structure [directory_name] [options]
Available options:
-a              : show all directories instead of just those containing files with the correct extension
-e [...exts]    : file extensions to search for (DEFAULT = `py`)
-h              : print help message and exit (also --help)
--if [...files] : names of files to ignore (no absolute paths, must include file extension)
--id [...dirs]  : names of directories to ignore (no absolute paths)
-l              : long analysis (line count, non-blank line count, char count)
-r              : recurse through all subdirectories
-s              : include file sizes
-t              : display graphical file tree
'''

# dependencies
import os
import sys
import abc
import argparse

def without_leading_period(string):
    '''Removes leading period from string (`.ext` -> `ext`)'''
    return string.lstrip('.')

# Create the argument parser
parser = argparse.ArgumentParser(
    description = "Analyze the file structure of a directory for information about the files, such as line count and the visual file tree",
    epilog = "Defaults to current working directory",
)

# Add arguments
parser.add_argument('dir_name', nargs='?', default=os.getcwd(),
    help='absolute or relative path to directory to analyze')
parser.add_argument('-r', action='store_true', required=False,
    help='recurse through all subdirectories', dest='recursive')
parser.add_argument('-t', action='store_true', required=False,
    help='display graphical file tree', dest='show_tree')
parser.add_argument('-e', action='extend', nargs='+', default=[], type=without_leading_period,
    required=False, help='file extensions to search for', metavar='EXT', dest='extensions')
parser.add_argument('--if', action='extend', nargs='+', default=[], type=os.path.basename,
    required=False, help='names of files to ignore (must include extension)', metavar='IF', dest='ignore_files')
parser.add_argument('--id', action='extend', nargs='+', default=[], type=os.path.basename,
    required=False, help='names of directories to ignore', metavar='ID', dest='ignore_dirs')


"""parser.add_argument('--nb', action='store_true', required=False,
    help='include non-blank line count in each file', dest='non_blank')
parser.add_argument('-w', action='store_true', required=False,
    help='include word count in each file', dest='words')
parser.add_argument('-c', action='store_true', required=False,
    help='include character count in each file', dest='chars')"""


parser.add_argument('-s', action='store_true', required=False,
    help='include file sizes', dest='show_sizes')
# TODO: edit this one too
parser.add_argument('-l', action='store_true', required=False,
    help='long analysis including non-blank line count and char count', dest='long_analysis')

parser.add_argument('-a', action='store_true', required=False,
    help='show all directories instead of just those containing relevant files', dest='show_all')

class StructureObject(metaclass=abc.ABCMeta):
    '''
    Abstract Base Class representing a File or Directory, providing
    some default functionality

    Methods that must be defined:
        - line_count()
        - non_blank_line_count()
        - char_count()
        - size()
    '''
    @property
    def name(self):
        '''
        Allows access to the `name` property (read-only)
        '''
        return self._name

    def __eq__(self, other):
        '''
        Checks if file names are equal
        '''
        return (self.name == other.name)

    def __ne__(self, other):
        '''
        Checks if file names are not equal
        '''
        return (self.name != other.name)

    def __lt__(self, other):
        '''
        Checks if this file name is less than the other file name
        '''
        return (self.name < other.name)

    def __le__(self, other):
        '''
        Checks if this file name is less than or equal to the other file name
        '''
        return (self.name <= other.name)

    def __gt__(self, other):
        '''
        Checks if this file name is greater than the other file name
        '''
        return (self.name > other.name)

    def __ge__(self, other):
        '''
        Checks if this file name is greater than or equal to the other file name
        '''
        return (self.name >= other.name)

    @abc.abstractmethod
    def line_count(self):
        '''
        Gets the total line count
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def non_blank_line_count(self):
        '''
        Gets the total non-blank line count
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def char_count(self):
        '''
        Gets the total char count
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def size(self):
        '''
        Gets the total size
        '''
        raise NotImplementedError


class Directory(StructureObject):
    '''
    This class represents a file directory crawled, storing any relevant
    information about the directory and the files it holds
    '''
    def __init__(self, dir_name, **kwargs):
        '''
        Constructs a new Directory with the given properties
        '''
        self._name = os.path.basename(dir_name)
        self._items = []

    def __repr__(self):
        '''
        String representation of the Directory
        '''
        return f"Directory({self._name})"

    def __iadd__(self, item):
        '''
        Adds a file structure item to the list of items in the directory
        '''
        self._items.append(item)
        return self

    def line_count(self):
        '''
        Gets the total line count
        '''
        count = 0
        for item in self._items:
            count += item.line_count()
        return count

    def non_blank_line_count(self):
        '''
        Gets the total non-blank line count
        '''
        count = 0
        for item in self._items:
            count += item.non_blank_line_count()
        return count

    def char_count(self):
        '''
        Gets the total char count
        '''
        count = 0
        for item in self._items:
            count += item.char_count()
        return count

    def size(self):
        '''
        Gets the total size
        '''
        total_size = 0
        for item in self._items:
            total_size += item.size()
        return total_size

    def has_file(self):
        '''
        Checks if this Directory contains any File objects
        '''
        for item in self._items:
            if isinstance(item, File):
                # found a file
                return True
            elif isinstance(item, Directory):
                if item.has_file():
                    # found a directory with at least one file
                    return True
        return False

    def item_counts(self):
        '''
        Counts the number of directories and files in the structure,
        not including itself.
        Return: tuple (dir_count, file_count)
        '''
        dir_count = 0
        file_count = 0
        for item in self._items:
            if isinstance(item, File):
                file_count += 1
            elif isinstance(item, Directory):
                counts = item.item_counts()
                dir_count += 1 + counts[0]
                file_count += counts[1]
        return dir_count, file_count

    def num_hidden(self):
        '''
        Counts the number of hidden directories (don't have any files)
        '''
        count = 0
        for item in self._items:
            if isinstance(item, Directory):
                if not item.has_file():
                    count += 1
                count += item.num_hidden()
        return count

    def print(self, recurse, show_all, depth=0):
        '''
        Prints out the structure inside this Directory
        recurse: bool, representating whether to recurse into subdirectories
        show_all: bool, representing whether to show directories with no files
        depth: (optional) int, representing the current depth
        '''
        # Print out the name of the overarching directory
        self._print_depth(depth)
        print(self._name + "/")

        depth += 1
        for item in self._items:
            if isinstance(item, File):
                self._print_depth(depth)
                print(item.name + "  " + item.info_string())
            elif isinstance(item, Directory):
                if not recurse:
                    # Just print the directory name
                    self._print_depth(depth)
                    print(item.name + "/")
                elif recurse and (show_all or item.has_file()):
                    # Have the item recursively print
                    item.print(recurse, show_all, depth)

    def _print_depth(self, depth):
        '''
        Prints text to represent the given depth
        depth: int, representing the depth
        '''
        for i in range(depth - 1):
            print("|   ", end="")
        if depth > 0:
            print("|—— ", end="")


class File(StructureObject):
    '''
    This class represents a file crawled, storing any relevant information
    about the file
    '''
    def __init__(self, file_name, **kwargs):
        '''
        Constructs a new File with the given properties
        '''
        self._name = os.path.basename(file_name)
        self._line_count = kwargs.get('line_count')
        self._non_blank_line_count = kwargs.get('non_blank_line_count')
        self._char_count = kwargs.get('char_count')
        self._size = kwargs.get('size')

    def __repr__(self):
        '''
        String representation of the File
        '''
        return f"File({self._name})"

    def line_count(self):
        '''
        Gets the total line count
        '''
        return self._line_count

    def non_blank_line_count(self):
        '''
        Gets the total non-blank line count
        '''
        return self._non_blank_line_count

    def char_count(self):
        '''
        Gets the total char count
        '''
        return self._char_count

    def size(self):
        '''
        Gets the total file size
        '''
        return self._size

    def info_string(self):
        '''
        Returns the info string representing the File. Includes all
        information known about line counts, char counts, and size
        '''
        info = []
        if self._line_count:
            info.append(f"{self._line_count} lines")
        if self._non_blank_line_count:
            info.append(f"{self._non_blank_line_count} non-blank lines")
        if self._char_count:
            info.append(f"{self._char_count} chars")
        if self._size:
            info.append(f"{self._size} bytes")
        return ", ".join(info)

class FileCrawler:
    '''
    This class will crawl through directories and files, getting the word
    and line counts for each file.
    '''

    __slots__ = ('dir_name', 'extensions', 'ignore_files', 'ignore_dirs', 'show_all',
                 'long_analysis', 'recursive', 'show_sizes', 'show_tree')

    def __init__(self, *, skip_construction=False, **kwargs):
        '''
        Constructs a new FileCrawler with the provided settings
        skip_construction: ignore if you are manually instantiating a FileCrawler;
                           meant to delay construction until argparse parses the
                           command line arguments into the object
        kwargs: dir_name      : str, name of directory to crawl
                ignore_files  : set[str], names of files to ignore
                ignore_dirs   : set[str], names of directories to ignore
                extensions    : set[str], file extensions to look for
                show_all      : bool, whether to show all directories
                long_analysis : bool, whether to include non-blank line and char counts
                recursive     : bool, whether to recurse into subdirectories
                show_sizes    : bool, whether to include file sizes
                show_tree     : bool, whether to display the file tree
        '''
        if not skip_construction:                                    # ARGUMENT NAME / FLAG
            self.dir_name = kwargs.get("dir_name", os.getcwd())      # dir_name
            self.ignore_files = kwargs.get("ignore_files", set())    # --if
            self.ignore_dirs = kwargs.get("ignore_dirs", set())      # --id
            self.extensions = kwargs.get("extensions", set())        # -e
            self.show_all = kwargs.get("show_all", False)            # -a
            self.long_analysis = kwargs.get("long_analysis", False)  # -l
            self.recursive = kwargs.get("recursive", False)          # -r
            self.show_sizes = kwargs.get("show_sizes", False)        # -s
            self.show_tree = kwargs.get("show_tree", False)          # -t
            self.validate_arguments()

    def __repr__(self):
        '''
        String representation of the FileCrawler
        '''
        attrs = ", ".join([f"{attr}={repr(getattr(self, attr))}" for attr in self.__slots__])
        for attr_name in self.__slots__:
            getattr(self, attr_name)
        return f"{self.__class__.__name__}({attrs})"

    def crawl(self):
        '''
        Crawls the file structure and prints out the results
        '''
        # Load the structure inside the main directory
        structure = self._load_dir(self.dir_name)

        print()
        if self.show_tree:
            # print out the tree
            structure.print(self.recursive, self.show_all)
            print()

        # Print out the totals
        dir_count, file_count = structure.item_counts()
        print("Total directories:", dir_count, end="")
        if not self.show_all:
            num_hidden = structure.num_hidden()
            print(f" ({dir_count - num_hidden} shown, {num_hidden} hidden)")
        else:
            print()
        print("Total files:", file_count)
        print("Total lines:", structure.line_count())
        if self.long_analysis:
            print("Total non-blank lines:", structure.non_blank_line_count())
            print("Total chars:", structure.char_count())
        if self.show_sizes:
            print("Total size:", structure.size(), "bytes")

    def validate_arguments(self):
        '''
        Makes sure the crawler has valid arguments to do the crawl
        '''
        # Validate directory name
        if not os.path.isdir(self.dir_name):
            sys.stderr.write(f"Error: {self.dir_name} is not a valid directory path\n")
            sys.exit(1)

        # Make sure extensions, ignore_files, and ignore_dirs are sets
        self.ignore_files = set(self.ignore_files)
        self.ignore_dirs = set(self.ignore_dirs)
        self.extensions = set(self.extensions)
        if len(self.extensions) == 0:
            # use `py` as the default extension if none provided
            self.extensions.add("py")

    def _load_dir(self, dir_path):
        '''
        Crawls a single directory, and recurses if the class is set to recurse
        dir_path: str, representing the path to the directory
        Return: list of StructureObject objects (mix of File and Directory)
        '''
        current_dir = Directory(dir_path)
        for item_name in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item_name)
            if os.path.isdir(item_path) and item_name not in self.ignore_dirs:
                if self.recursive:
                    current_dir += self._load_dir(item_path)
                else:
                    current_dir += Directory(item_path)
            elif (os.path.isfile(item_path) and self._is_valid_file(item_path)):
                current_dir += self._load_file(item_path)
        return current_dir

    def _load_file(self, file_path):
        '''
        Loads the File object information for the given file
        file_path: str, representing the path to the file
        Return: File representing the file
        '''
        file_info = {}
        self._read_file(file_info, file_path)   # read the line / char counts
        if self.show_sizes:
            # include file sizes
            file_info['size'] = os.path.getsize(file_path)

        return File(file_path, **file_info)

    def _read_file(self, file_info, file_path):
        '''
        Reads the information in a file
        file_info: dict, to store file information in
        file_path: str, representing the path to the file
        '''
        file_info["line_count"] = 0
        if self.long_analysis:
            file_info["non_blank_line_count"] = 0
            file_info["char_count"] = 0
            def read_info(line):
                '''Read information with long analysis'''
                file_info["line_count"] += 1
                file_info["char_count"] += len(line)
                if len(line.strip()) > 0:
                    file_info["non_blank_line_count"] += 1
        else:
            def read_info(line):
                '''Read information with only line count'''
                file_info["line_count"] += 1

        f = open(file_path, 'r', encoding='utf8')
        for line in f:
            line = line.strip("\n")
            read_info(line)

    def _is_valid_file(self, file_path):
        '''
        Checks if the given file path is valid to read stats of,
        by making sure it is not this program itself, checking if
        the file is one of the extensions to look for, and if the
        file's name is not in the set of files to ignore
        file_path: str, representing the path to the file
        '''
        file_name = os.path.basename(file_path)
        return (
            not os.path.samefile(file_path, sys.argv[0])
            and file_name.split(".")[-1] in self.extensions
            and file_name not in self.ignore_files
        )


def main():
    # Parse the arguments into a FileCrawler
    fc = FileCrawler(skip_construction=True)
    parser.parse_args(namespace=fc)
    fc.validate_arguments()
    print(repr(fc))

    # Crawl the file structure
    print(f"""Searching for file extensions '.{"', '.".join(fc.extensions)}' ...""")
    fc.crawl()

if __name__ == "__main__":
    main()