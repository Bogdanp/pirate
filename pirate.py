"""Usage: python {} OPTION [PARAMETER..]

Available options:
  -d ID      Download the torrent at ID.
  -h         Print this and exit.
  -i ID      See information about a particular magnet link.
  -l         List all the links in the magnet file.
  -s KEYWORD List only the links that match the given KEYWORD.\
"""
from __future__ import print_function
import re
import sys
import webbrowser

MAGNETFILE = 'magnets'

class ItemError(Exception): pass
class Item(object):
    def __init__(self, line):
        line = line.split('|')
        self.line = line
        self.id = line.pop(0)
        self.link = line.pop().rstrip()
        self.leechers = line.pop()
        self.seeders = line.pop()
        self.size = bytes_to_readable(line.pop())
        self.title = '|'.join(line)

    def __str__(self):
        return '{}: {}'.format(self.id, self.title)

    def pretty_print(self):
        print(self.title)
        print('Id: {}'.format(self.id))
        print('Size: {}'.format(self.size))
        print('Seeders: {}'.format(self.seeders))
        print('Leechers: {}'.format(self.leechers))

    def get_link(self):
        return 'magnet:?xt=urn:btih:{}'.format(self.link)

def items():
    for i, line in enumerate(open(MAGNETFILE)):
        yield Item(line)

def find_item(id):
    for item in items():
        if item.id == id:
            return item
    raise ItemError('Could not find an item at id {}'.format(id))

def print_help():
    print(__doc__.format(sys.argv[0]))
    return 0

def bytes_to_readable(bytes):
    suffixes, i = ['B', 'KB', 'MB', 'GB', 'TB'], 0
    bytes = float(bytes)
    while bytes >= 1024:
        bytes /= 1024
        i += 1
    return '{:.2f}{}'.format(bytes, suffixes[i])

def download(id):
    webbrowser.open(find_item(id).get_link())
    return 0

def list_items():
    for item in items():
        print(item)
    return 0

def get_information(id):
    find_item(id).pretty_print()
    return 1

def search(*expression):
    expression = ' '.join(expression)
    for item in items():
        if re.match(expression, item.title):
            print(item)
    return 0

def main(args):
    try:
        return {
            '-d': download,
            '-h': print_help,
            '-i': get_information,
            '-l': list_items,
            '-s': search,
        }[args[1]](*args[2:])
    except IOError:
        print('Could not read magnet file at "{}".'.format(MAGNETFILE))
        return 1
    except ItemError as e:
        print('Error: {}'.format(e))
        return 1
    except TypeError:
        print('Error: Missing argument to {}.'.format(args[1]))
        return 1
    except KeyboardInterrupt:
        return 1
    except (IndexError, KeyError):
        return print_help()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
