'''
Command-line interface.
'''

import click
from resumepy import Resume
from resumepy import quickstart
from resumepy.palettes import PALETTES, DEFAULT_PALETTE


@click.group()
def cli():
    pass


@cli.command(help='Generate HTML and text versions of a resume and save them in a directory.')
@click.argument('source_dir')
@click.option('--variant', default=None, help='Subfolder of SOURCE_DIR containing override YAML files.')
@click.option('--name', default=None, help='Output filename base. Defaults to the source folder name.')
@click.option('--theme', default='default', help='Bundled theme name or path to a custom HTML template. Default: default.')
@click.option('--output', default='dist', help='Output directory. Default: dist.')
@click.option('--palette', default=DEFAULT_PALETTE, type=click.Choice(list(PALETTES)), show_default=True, help='Color palette.')
def build(source_dir, variant, name, theme, output, palette):
    resume = Resume(source_dir, variant=variant, theme=theme, output_dir=output, name=name, palette=palette)
    resume.publish()


@cli.command(help='Create a sample resume folder in the current directory.')
@click.argument('name', default='resume')
def init(name):
    quickstart.init(name)
