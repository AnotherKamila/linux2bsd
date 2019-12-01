import fnmatch
import os
import queue
import re
from collections import namedtuple

import click

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '_data')
DATA_FILES_TO = 'bsd'
PREFIX_BONUS = 1.5

class BadDataFile(Exception):
    pass

Candidate = namedtuple('Candidate', ('score', 'result', 'match'))

def read_file(path):
    with open(path) as f:
        for line in f:
            try:
                line = line.strip()
                if not line or line.startswith('#'): continue
                k, v = line.split(',')
                yield (k.strip(), v.strip())
            except Exception as e:
                raise BadDataFile(f'Cannot parse file {path}: "{line}"') from e

def load_category(data_dir, category):
    return read_file(os.path.join(data_dir, category+'.csv'))

def load_data(data_dir, reverse=False):
    for fname in os.listdir(data_dir):
        if not fname.endswith('.csv'): continue
        for k, v in read_file(os.path.join(data_dir, fname)):
            if reverse: k, v = v, k
            yield (k, v)

def score_match(pattern, candidate):
    m = re.search(pattern, candidate)
    if not m: return 0
    return (m.end() - m.start())*(PREFIX_BONUS if m.start() == 0 else 1)

def translate(command, data_dir=DATA_DIR, to='bsd'):
    index = load_data(data_dir=data_dir, reverse=(to != DATA_FILES_TO))
    candidates = []
    for k, v in index:
        score = score_match(command, k)
        if score > 0:
            candidates.append(Candidate(score=score, match=k, result=v))
    return candidates

def get_categories(data_dir):
    files = [ f for f in os.listdir(data_dir) if f.endswith('.csv') ]
    return [ os.path.splitext(f)[0] for f in files]


@click.command()
@click.option('--to', '-t', type=click.Choice(['bsd', 'linux']), default='bsd',
              help='Linux to BSD or BSD to Linux?')
@click.option('--regex/--shell', '-E/-g', default=False,
              help="Interpret the pattern as a regex (default: shell-like)")
@click.option('--verbose/--quiet', '-v/-q', default=False,
              help="Print detailed info about the matches")
@click.option('--show-category', '-s', is_flag=True,
              help='Show a table for the given category (or categories)')
@click.option('--list-categories', '-l', is_flag=True,
              help='List all command categories')
@click.option('--limit', type=int, default=10,
              help='Limit the number of returned results')
@click.option('--data-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default=DATA_DIR, help='Path to command data files')
@click.argument('command', nargs=-1)
def linux2bsd(command, data_dir, to, regex, verbose, limit,
              show_category, list_categories):
    """TODO something"""
    # This is ugly, but it works:
    if list_categories:
        click.echo('\n'.join(get_categories(data_dir)))
    if show_category:
        for category in command:
            click.echo(category.upper())
            for k, v in load_category(data_dir, category):
                if to != DATA_FILES_TO: k, v = v, k
                click.echo(f'{k: <16}\t{v: <16}')
    else:
        # TODO if command empty and running interactively, prompt
        # TODO tokenization and things
        command = (' ').join(command)
        # translate from shell-like glob to regex
        if not regex: command = fnmatch.translate(command).replace(r'\Z', '')
        candidates = translate(command, data_dir=data_dir, to=to)[:limit]

        already_printed = set()
        for c in sorted(candidates, reverse=True):
            if verbose:
                click.echo(f'{c.match: <16}\t{c.result: <16}\t{int(c.score):2}')
            else:
                if not c.result in already_printed:
                    click.echo(c.result)
                    already_printed.add(c.result)


if __name__ == '__main__':
    linux2bsd(auto_envvar_prefix='LINUX2BSD')
