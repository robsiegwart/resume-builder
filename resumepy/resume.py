'''
Build a resume from YAML data files using a Jinja2 theme template.
'''

from pathlib import Path
from functools import cached_property
import yaml
import mistune
from resumepy.palettes import PALETTES, DEFAULT_PALETTE
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import click
from importlib.metadata import version as _pkg_version


THEMES_DIR = Path(__file__).parent / 'themes'


class Resume:
    '''
    A resume document.

    :param source_dir:  Path to the folder containing base YAML files.
    :param variant:     Name of a subfolder within source_dir with override YAML files.
    :param theme:       Bundled theme name or path to a custom template file.
    :param output_dir:  Directory to write the output file. Default: 'dist'.
    :param name:        Output filename base. Defaults to the source folder name.
    '''
    def __init__(self, source_dir, variant=None, theme='default', output_dir='dist', name=None, palette=DEFAULT_PALETTE):
        self.source_dir = Path(source_dir)
        self.variant = variant
        self.theme = theme
        self.output_dir = Path(output_dir)
        self.palette = PALETTES[palette]
        base = name or self.source_dir.resolve().name
        self.name = f'{base}-{variant}' if (variant and not name) else base

        click.echo(f' ResumePy v{_pkg_version("resumepy")} '.center(80, '='))

        self.context = {}
        self._load_yaml(self.source_dir)
        if variant:
            self._load_yaml(self.source_dir / variant)
        self._normalize_sections()

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_sections(self):
        sections = self.context.get('Header', {}).get('sections')
        if sections:
            self.context['Header']['sections'] = [
                s.replace('-', '_').replace(' ', '_') for s in sections
            ]

    def _load_yaml(self, directory):
        for f in sorted(Path(directory).glob('*.yaml')):
            key = f.stem.replace('-', '_').replace(' ', '_')
            self.context[key] = yaml.safe_load(f.read_text(encoding='utf-8'))

    @cached_property
    def _theme_info(self):
        '''Resolve (theme_dir, template_filename, output_suffix) from self.theme.'''
        theme_path = Path(self.theme)
        if theme_path.is_file():
            return theme_path.parent, theme_path.name, theme_path.suffix
        theme_dir = THEMES_DIR / self.theme
        candidates = list(theme_dir.glob(f'{self.theme}.*'))
        if not candidates:
            raise FileNotFoundError(f'No template found for theme "{self.theme}" in {theme_dir}')
        f = candidates[0]
        return theme_dir, f.name, f.suffix

    @cached_property
    def env(self):
        theme_dir, _, suffix = self._theme_info
        env = Environment(
            loader=FileSystemLoader(str(theme_dir)),
            autoescape=select_autoescape(['html']) if suffix == '.html' else False,
            trim_blocks=True,
            lstrip_blocks=True
        )
        _md = mistune.create_markdown(plugins=['strikethrough'])
        env.filters['markdown'] = lambda text: Markup(_md(text)) if isinstance(text, str) else Markup('')
        return env

    def render(self):
        _, template_name, _ = self._theme_info
        return self.env.get_template(template_name).render(context=self.context, palette=self.palette)

    def publish(self):
        _, _, suffix = self._theme_info
        out = self.output_dir / (self.name + suffix)
        click.echo(f'Output will be written to "{self.output_dir}/"')
        out.write_text(self.render(), encoding='utf-8')
        click.echo(f'Saved to "{out}"')
        return out

    def publish_pdf(self, html_path: Path):
        from playwright.sync_api import sync_playwright
        pdf_path = html_path.with_suffix('.pdf')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(html_path.resolve().as_uri())
            page.pdf(path=str(pdf_path), print_background=True)
            browser.close()
        click.echo(f'PDF saved to "{pdf_path}"')
