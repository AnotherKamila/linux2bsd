#!/usr/bin/env python
import fnmatch
import os
import queue
import re
import shutil
import subprocess
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
    return sorted(candidates, reverse=True)

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
@click.option('--interactive/--non-interactive', '-i/-n', default=True,
              help="Prompt to run command or show the man page")
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
              interactive, show_category, list_categories):
    """Translate common commands between Linux and BSD equivalents"""
    # This is ugly, but it works:
    # but TODO https://click.palletsprojects.com/en/7.x/options/#callbacks-and-eager-options
    if list_categories:
        click.echo('\n'.join(get_categories(data_dir)))

    if show_category:
        if command == ('all',): command = get_categories(data_dir)
        for category in command:
            click.echo(category.upper())
            for k, v in load_category(data_dir, category):
                if to != DATA_FILES_TO: k, v = v, k
                click.echo(f'{k: <16}\t{v: <16}')
            click.echo()

    else:
        # TODO if command empty and running interactively, prompt
        # TODO tokenization and things
        command = (' ').join(command)
        # translate from shell-like glob to regex
        if not regex: command = fnmatch.translate(command).replace(r'\Z', '')
        candidates = translate(command, data_dir=data_dir, to=to)[:limit]

        # TODO only print unique
        for i, c in enumerate(candidates):
            if verbose:
                click.echo(f'{c.match: <16}\t{c.result: <16}\t{int(c.score):2}')
            else:
                click.echo(f'{i+1:2} {c.result}' if interactive else f'{c.result}')

        # TODO this is the worst code I've written in a looong time :D
        if interactive:

            # TODO attrs + validator for text format
            class PromptChoice(namedtuple('PromptChoice', ('text', 'handler'))):
                @property
                def key(self):
                    return self.text[1].lower()

            choices = {}  # key => PromptChoice
            prompt_for = []  # list of keys
            some_other_dict = {}
            for i, candidate in enumerate(candidates):
                my_choices = []
                # TODO move to its own function
                command, *args = [arg.strip() for arg in candidate.result.split('#')[0].split()]

                # expecting format like: whoami(1)
                manpage = None
                if len(command) > 3 and command[-3] == '(' and command[-1] == ')':
                    command, manpage = command[:-3], int(command[-2])

                executable = shutil.which(command)

                def runcmd(cmd):
                    subprocess.call(cmd)

                if manpage:
                    my_choices.append(PromptChoice('[m]an page', lambda: subprocess.call(['man', str(manpage), command])))
                if executable:
                    my_choices.append(PromptChoice('[r]un', lambda: runcmd([command]+args)))

                for c in my_choices:
                    if len(candidates) > 1:
                        choices[f'{i+1}{c.key}'] = c
                        if not c.key in prompt_for:
                            prompt_for.append(c.key)
                    else:
                        choices[c.key] = c
                        prompt_for.append(c.key)
                some_other_dict.update({c.key: c for c in my_choices})

            if choices:
                choices['q'] = PromptChoice('[Q]uit', lambda: None)
                some_other_dict['q'] = choices['q']
                prompt_for.append('q')
                prompt_text =  'number + ' if len(candidates) > 1 else ''
                prompt_text += ', '.join(some_other_dict[k].text for k in prompt_for)
                res = click.prompt(prompt_text, default='q',
                                    type=click.Choice(choices.keys(), case_sensitive=False),
                                    prompt_suffix='? ', show_choices=False, show_default=False)
                handler = choices[res].handler
                handler()


if __name__ == '__main__':
    linux2bsd(auto_envvar_prefix='LINUX2BSD')
