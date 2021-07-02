'''
Command-line interface.
'''

import click
from resumepy import Resume
from resumepy import quickstart


@click.group()
def cli():
    pass


@cli.command(help='Generate HTML, PDF, and text versions of a resume and save them in a directory.')
@click.argument('source_dir')
@click.option('--name', default=None, help='Specify an alternate filename for published files. Default is SOURCE_DIR.')
@click.option('--section', default='DEFAULT', help='The config section to use from the local config.ini file. Default is "DEFAULT"')
def build(source_dir, name, section):
    resume = Resume(source_dir, name, section)
    resume.publish()


@cli.command(help='Scaffold a basic file structure in the current directory.')
def init(*args,**kwargs):
    quickstart.init(*args,**kwargs)