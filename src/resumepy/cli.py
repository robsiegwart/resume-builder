'''
    Click CLI
'''

import click
from . import builder


@click.group()
def cli():
    pass

@cli.command(help='Generate HTML, PDF, and text versions of a resume and save them in a directory.')
@click.argument('source_dir')
@click.option('--name', default=None, help='Specify an alternate filename for published files. Default is source_dir.')
@click.option('--config', default='DEFAULT', help='Specify a config group within local config.ini')
@click.option('--overwrite', default=False, help='Overwrite output files.', is_flag=True)
def build(*args,**kwawrgs):
    builder.build(*args,**kwawrgs)


@cli.command(help='Scaffold a basic file structure in the current directory.')
def init(*args,**kwawrgs):
    builder.init(*args,**kwawrgs)