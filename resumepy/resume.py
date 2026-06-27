'''
Build HTML and text versions of a resume from YAML data files.
'''

import os
from glob import glob
from functools import cached_property
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
import click
from importlib.metadata import version as _pkg_version
from .config import *


class Resume:
    '''
    A resume document.

    :param str source_dir:      The string name of the directory to use containing
                                the source YAML files for the resume content
    :param str name:            Specify an alternate filename for published
                                files. Default is ``source_dir``.
    :param str section:         The config section to use from the local
                                ``config.ini`` file. Default is ``DEFAULT``.
    '''
    def __init__(self, source_dir, name=None, section='DEFAULT'):
        self._source_name = source_dir
        self.name = name if name else source_dir
        self.section = section
        self.CONFIG = load_config(source_dir)

        click.echo(f' ResumePy v{_pkg_version("resumepy")} '.center(80,'='))

        os.makedirs(self.publish_dir, exist_ok=True)

        # Read in resume data
        self.context = {'title': True} if self.CONFIG.get(self.section, 'TITLE') else {'title': False}
        source_files = glob(os.path.join( self.CONFIG.get(self.section, 'SOURCES_DIR'), source_dir, '*.yaml' ))
        source_file_names = list(map(lambda f: os.path.basename(f), source_files))
        default_files = glob(os.path.join( self.CONFIG.get(self.section, 'SOURCES_DIR'), 'Default', '*.yaml' ))

        for fname in default_files:
            if os.path.basename(fname) in source_file_names:
                bn = os.path.basename(fname)
                fname = list(filter(lambda f: bn in f, source_files))[0]
            with open(fname) as f:
                name = os.path.splitext(os.path.basename(fname))[0].replace('-', '_').replace(' ', '_')
                self.context[name] = yaml.safe_load(f)
        
        self.output_file = os.path.join(self.publish_dir, self.name)

    @cached_property
    def env(self):
        '''The Jinja environment object'''
        return Environment(
            loader=FileSystemLoader([ os.path.join(self.CONFIG.get(self.section,'TEMPLATES_DIR'), 'html'),
                                      os.path.join(self.CONFIG.get(self.section,'TEMPLATES_DIR'), 'text') ]),
            autoescape=select_autoescape(['html']),
            trim_blocks=True
        )

    @cached_property
    def publish_dir(self):
        '''The containing publish directory'''
        return self.CONFIG.get(self.section, 'PUBLISH_DIR')
    
    @cached_property
    def source_dir(self):
        '''The directory containing source YAML files'''
        return os.path.join(self.CONFIG.get(self.section, 'SOURCES_DIR'), self._source_name)
    
    @property
    def html(self):
        '''Return the rendered HTML form of the resume'''
        html_template = self.env.get_template(self.CONFIG.get(self.section, 'HTML_TEMPLATE') + '.html')
        
        # Layout the skills section if configured to do so
        if self.CONFIG.get(self.section, 'SKILLS_LAYOUT', fallback=None):
            sl = list(map(lambda x: x.split(','), self.CONFIG.get(self.section, 'SKILLS_LAYOUT').split('|')))
            for i,each in enumerate(sl):
                sl[i] = list(map(lambda x: x.strip(), each))

            self.context['skills_layout'] = sl

        return html_template.render(context=self.context)

    @property
    def text(self):
        '''Return the text form of the resume'''
        text_template = self.env.get_template(self.CONFIG.get(self.section, 'TEXT_TEMPLATE') + '.txt')
        return text_template.render(context=self.context)

    def publish(self):
        '''
        Save out all specified versions of the resume to the output directory.
        '''
        click.echo(f'Output files will be written to "{self.publish_dir}/"')

        # ///////////////////////////// Save HTML \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        self.save_file(self.html, self.output_file + '.html')
        click.echo(f'Saved HTML file to "{self.output_file}.html"')

        # ////////////////////////////// Save Text \\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        self.save_file(self.text, self.output_file + '.txt')
        click.echo(f'Saved TXT file to \"{self.output_file + ".txt"}\"')

    def save_file(self, content, filename):
        '''Save out a file'''
        with open(filename, 'w') as ofile:
            ofile.write(content)