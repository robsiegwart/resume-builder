import click
import os
from pathlib import Path
from shutil import copy


SAMPLE_DATA_DIR = Path(__file__).parent / 'sample-data'


def init(folder='resume'):
    '''Copy sample YAML files into a new folder in the current directory.'''
    dest = Path(os.getcwd()) / folder

    if dest.exists():
        click.echo(f'Folder "{folder}" already exists. Skipping.')
        return

    dest.mkdir()
    click.echo(f'Creating "{folder}/" with sample resume data:')
    for yaml_file in sorted(SAMPLE_DATA_DIR.glob('*.yaml')):
        copy(yaml_file, dest / yaml_file.name)
        click.echo(f'  {yaml_file.name}')

    click.echo(f'\nTo build, run:\n\n    resumepy build {folder}\n')
