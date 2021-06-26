'''
    Click CLI
'''

import click
from . import builder
from . import quickstart


@click.group()
def cli():
    pass

@cli.command(help='Generate HTML, PDF, and text versions of a resume and save them in a directory.')
@click.argument('source_dir')
@click.option('--name', default=None, help='Specify an alternate filename for published files. Default is source_dir.')
@click.option('--config', default='DEFAULT', help='Specify a config group within local config.ini')
@click.option('--overwrite', default=False, help='Overwrite output files.', is_flag=True)
@click.option('--html/--no-html', default=True, help='Create an html version. Default is true.')
@click.option('--text/--no-text', default=True, help='Create a text version. Default is true.')
@click.option('--pdf/--no-pdf', default=True, help='Create a pdf version. Default is true. (HTML is also enabled.)')
def build(*args,**kwargs):
    builder.build(*args,**kwargs)


@cli.command(help='Scaffold a basic file structure in the current directory.')
def init(*args,**kwargs):
    quickstart.init(*args,**kwargs)