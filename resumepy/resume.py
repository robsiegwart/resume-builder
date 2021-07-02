'''
Create a HTML version of a resume based on YAML data files and convert to PDF
and text.
'''

import os
from datetime import datetime
from glob import glob
from functools import cached_property
import yaml
import pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape, UndefinedError
import click
from .config import *
from .version import VERSION


class Resume:
    '''
    A resume document.

    :param str source_dir:      The string name of the directory to use containing
                                the source YAML files for the resume content
    :param str name:            Specify an alternate filename for published
                                files. Default is ``source_dir``.
    :param str section:         The config section to use from the local
                                ``config.ini`` file.
    '''
    def __init__(self, source_dir, name=None, section='DEFAULT'):
        self.source_dir = source_dir
        self.name = name if name else source_dir
        self.section = section
        self.CONFIG = load_config(source_dir)

        click.echo(f' ResumePy v{VERSION} '.center(80,'='))

        # Create the publish directory if it does not already exist
        if not os.path.exists(self.publish_dir):
            os.mkdir(self.publish_dir)
            click.echo(f'Creating publish dir "{self.publish_dir}"')

        # Create a new directory or clear existing directory to put built resume files in
        self.out_dir = os.path.join(self.publish_dir, source_dir + ' - ' + datetime.today().strftime('%m%d%Y-%H%M%S'))
        os.mkdir(self.out_dir)

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
        
        self.output_file = os.path.join(self.out_dir, self.name)

    @cached_property
    def env(self):
        '''Return the Jinja environment object'''
        return Environment(
            loader=FileSystemLoader([ os.path.join(self.CONFIG.get(self.section,'TEMPLATES_DIR'), 'html'),
                                      os.path.join(self.CONFIG.get(self.section,'TEMPLATES_DIR'), 'text') ]),
            autoescape=select_autoescape(['html']),
            trim_blocks=True
        )

    @cached_property
    def publish_dir(self):
        return self.CONFIG.get(self.section, 'PUBLISH_DIR')
    
    @cached_property
    def source_dir(self):
        return os.path.join(self.CONFIG.get(self.section, 'SOURCES_DIR'), self.source_dir)
    
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
        click.echo(f'Output files will be written to directory:\n   "{self.out_dir}"\n')

        # Save HTML
        self.save_file(self.html, self.output_file + '.html')
        click.echo(f'Saved HTML file to "{self.output_file}.html"')

        # save PDF
        pdf_in = self.output_file + '.html'
        pdf_out = self.output_file + '.pdf'
        PDF_OPTIONS = {'quiet':''}

        # Header/footer configuration and directory setup for PDF header
        if self.CONFIG.get(self.section,'HEADER',fallback=None):
            header_env = Environment(
                loader=FileSystemLoader(
                    [ os.path.join(self.CONFIG.get(self.section,'TEMPLATES_DIR'), 'html', self.CONFIG.get(self.section, 'HEADER_DIR')) ]),
                autoescape=select_autoescape(['html']),
                trim_blocks=True
            )

            header_template = header_env.get_template(self.CONFIG.get(self.section,'HEADER_TEMPLATE') + '.html')
            header = header_template.render({'name': self.context['Header']['name']})
            header_save_file = os.path.join(
                self.out_dir,
                self.CONFIG.get(self.section,'HEADER_TEMPLATE') + '.html')
            
            save = self.save_file(header, header_save_file)
            if save:
                click.echo(f'Using generated header file for PDF:\n    "{header_save_file}".\n')
            
            PDF_OPTIONS['header-html'] = header_save_file

        for k,v in self.CONFIG.items(self.section):
            if k.startswith('pdf'):
                key = k.replace('pdf_', '').replace('_', '-')
                PDF_OPTIONS[key] = v

        pdfkit.from_file(pdf_in, pdf_out, options=PDF_OPTIONS)
        click.echo(f'Saved PDF file to "{pdf_out}"')

        # Save text
        self.save_file(self.text, self.output_file + '.txt')
        click.echo(f'Saved TXT file to \"{self.output_file + ".txt"}\"')

    def save_file(self, content, filename):
        '''Save out a file'''
        with open(filename, 'w') as ofile:
            ofile.write(content)