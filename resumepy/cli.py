'''
Command-line interface.
'''

from pathlib import Path
import click
from resumepy import Resume
from resumepy import quickstart
from resumepy.palettes import PALETTES, DEFAULT_PALETTE
from resumepy.resume import THEMES_DIR


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
    source_path = Path(source_dir)
    if not source_path.is_dir():
        raise click.BadParameter(f'"{source_dir}" is not a valid directory.', param_hint='SOURCE_DIR')
    if variant and not (source_path / variant).is_dir():
        location = 'the current directory' if source_path == Path('.') else f'"{source_dir}"'
        raise click.BadParameter(f'Variant "{variant}" not found in {location}.', param_hint='--variant')
    theme_path = Path(theme)
    if not theme_path.is_file() and not (THEMES_DIR / theme).is_dir():
        raise click.BadParameter(f'"{theme}" is not a built-in theme or a valid template file path.', param_hint='--theme')
    resume = Resume(source_dir, variant=variant, theme=theme, output_dir=output, name=name, palette=palette)
    resume.publish()


@cli.command(help='Create a sample resume folder in the current directory.')
@click.argument('name', default='resume')
def init(name):
    quickstart.init(name)
