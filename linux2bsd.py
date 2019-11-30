import os
import queue

import click

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '_data')
DATA_FILES_TO = 'bsd'

def load_data(data_dir, reverse=False):
    cmd_list = []
    for fname in os.listdir(data_dir):
        if not fname.endswith('.csv'): continue
        with open(os.path.join(data_dir, fname)) as f:
            for line in f:
                if line.startswith('#'): continue
                k, v = line.split(',')
                if reverse: k, v = v, k
                cmd_list.append((k.strip(), v.strip()))
    return cmd_list

def score_match(pattern, candidate):
    # TODO if I want to match on common prefix, I should sort and binsearch the list
    # it's not paths, but it works :D
    commonprefix = len(os.path.commonprefix([pattern, candidate]))
    return commonprefix - 1

def translate(command, data_dir=DATA_DIR, to='bsd'):
    index = load_data(data_dir=data_dir, reverse=(to != DATA_FILES_TO))
    candidates = []
    for k, v in index:
        score = score_match(command, k)
        if score > 0:
            candidates.append((score, k, v))
    return sorted(candidates)


@click.command()
@click.option('--to', '-t', type=click.Choice(['bsd', 'linux']), default='bsd',
              help='Linux to BSD or BSD to Linux?')
@click.option('--verbose/--quiet', '-v/-q', default=False,
              help="Print detailed info about the matches")
@click.option('--max-results', type=int, default=10,
              help='Caps the number of returned results')
@click.option('--data-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default=DATA_DIR, help='Path to command data files')
@click.argument('command', nargs=-1)
def linux2bsd(command, data_dir, to, max_results, verbose):
    """TODO something"""
    # TODO if command empty and running interactively, prompt
    # TODO tokenization and things
    command = (' ').join(command)
    candidates = translate(command, data_dir=data_dir, to=to)[:max_results]

    already_printed = set()
    for score, match, result in candidates:
        if verbose:
            click.echo(f'{match: <16}\t{result: <16}\t{score:2}')
        else:
            if not result in already_printed:
                click.echo(result)
                already_printed.add(result)


if __name__ == '__main__':
    linux2bsd(auto_envvar_prefix='LINUX2BSD')
