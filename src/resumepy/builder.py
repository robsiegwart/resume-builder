# MIT License
# 
# Copyright(c) 2020 Rob Siegwart
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
    Create a HTML version of a resume based on YAML data files and convert to
    PDF and text.
'''

import os
from datetime import datetime
from glob import glob
from collections import OrderedDict
import yaml
import pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape
import click

from .config import *
from .version import VERSION



def file_dir_exists(path):
    try:
        return os.path.exists(path)
    except AssertionError:
        fn = os.path.basename(path)
        click.echo(f'Template {fn} does not exist. Exiting ...')
        return False
    return True


def build(*args,**kwargs):
    '''
        Generate HTML, PDF, and text versions of a resume and save them in a
        directory.
    '''

    click.echo(f' ResumePy v{VERSION} '.center(80,'='))

    # GET AND SET VARIABLES
    # ---------------------
    source_dir = kwargs.get('source_dir')
    name = kwargs.get('name')
    config = kwargs.get('config')
    overwrite = kwargs.get('overwrite')
    html = kwargs.get('html') 
    text = kwargs.get('text') 
    pdf =  kwargs.get('pdf')
    
    CONFIG = load_config(source_dir)
    
    PUBLISH_DIR = CONFIG.get(config,'PUBLISH_DIR')
    SOURCE_DIR =    os.path.join(CONFIG.get(config, 'SOURCES_DIR'), source_dir)
    TEMPLATES_DIR = os.path.join(CONFIG.get(config, 'TEMPLATES_DIR'))

    
    # FILE AND DIRECTORY SETUP
    # ------------------------
    if not all([file_dir_exists(loc) for loc in [ SOURCE_DIR, TEMPLATES_DIR ]]):
        click.echo('SOURCE_DIR or TEMPLATES_DIR does not exist. Exiting ...')
        return
    
    html_template_exists = file_dir_exists( os.path.join(TEMPLATES_DIR, 'html',f'{CONFIG.get(config,"HTML_TEMPLATE")}.html') ) if html else None
    text_template_exists = file_dir_exists( os.path.join(TEMPLATES_DIR, 'text', f'{CONFIG.get(config,"TEXT_TEMPLATE")}.txt') ) if text else None
    if pdf:
        if not html_template_exists:
            click.echo('HTML template does not exist for PDF creation. Exiting.')
            return
    
    if not glob(os.path.join(SOURCE_DIR,'*.yaml')):
        click.echo('No source YAML files were found.')
        return

    # Create the publish directory if it does not already exist
    if not os.path.exists(PUBLISH_DIR):
        os.mkdir(PUBLISH_DIR)
        click.echo(f'Creating publish dir "{PUBLISH_DIR}"')

    # Create a new directory or clear existing directory to put built resume files in
    new_folder = source_dir + ' - ' + datetime.today().strftime('%b-%d-%Y')
    if os.path.exists(os.path.join(PUBLISH_DIR, new_folder)):
        if not overwrite:
            i = 1
            while os.path.exists(os.path.join(PUBLISH_DIR, new_folder + f' ({i})')):
                i += 1
            new_folder = new_folder + f' ({i})'
            os.mkdir(os.path.join(PUBLISH_DIR, new_folder))
        else:
            out_files = glob(os.path.join(PUBLISH_DIR, new_folder,'*'))
            try:
                for file in out_files:
                    os.remove(file)
            except PermissionError as e:
                click.echo("\nPlease close the listed file.")
                return
    else:
        os.mkdir(os.path.join(PUBLISH_DIR, new_folder))
    

    out_dir = os.path.join(PUBLISH_DIR, new_folder)
    output_file = os.path.join(out_dir,name) if name else os.path.join(out_dir,source_dir)


    # LOAD RESUME DATA
    # ----------------
    context = {'title': True} if CONFIG.get(config, 'TITLE') else {'title': False}

    source_files = glob(os.path.join( CONFIG.get(config,'SOURCES_DIR'), source_dir, '*.yaml' ))
    source_file_names = list(map(lambda f: os.path.basename(f), source_files))
    default_files = glob(os.path.join( CONFIG.get(config,'SOURCES_DIR'), 'Default', '*.yaml' ))

    for fname in default_files:
        if os.path.basename(fname) in source_file_names:
            bn = os.path.basename(fname)
            fname = list(filter(lambda f: bn in f, source_files))[0]
        with open(fname) as f:
            name = os.path.basename(fname)
            name = os.path.splitext(name)[0].replace('-','_').replace(' ','_')
            context[name] = yaml.safe_load(f)


    # BUILD RESUME
    # ------------
    # Setup Jinja templating
    env = Environment(
        loader=FileSystemLoader([ os.path.join(CONFIG.get(config,'TEMPLATES_DIR'), 'html'),
                                  os.path.join(CONFIG.get(config,'TEMPLATES_DIR'), 'text') ]),
        autoescape=select_autoescape(['html']),
        trim_blocks=True
    )
    
    html_template = env.get_template(CONFIG.get(config, 'HTML_TEMPLATE') + '.html')
    text_template = env.get_template(CONFIG.get(config, 'TEXT_TEMPLATE') + '.txt')
    
    # Layout the skills section if configured to do so
    if CONFIG.get(config,'SKILLS_LAYOUT', fallback=None):
        sl = list(map(lambda x: x.split(','), CONFIG.get(config, 'SKILLS_LAYOUT').split('|')))
        for i,each in enumerate(sl):
            sl[i] = list(map(lambda x: x.strip(), each))

        context['skills_layout'] = sl


    # RENDER AND SAVE FILES
    # ---------------------
    click.echo(f'Output files will be written to directory:\n   "{out_dir}"\n')
    if overwrite:
        click.echo('Files will be overwritten.')

    # HTML
    if html or pdf:
        html = html_template.render(context=context)
        save_file(html,output_file + '.html')
        click.echo(f'Saved HTML file to "{output_file}.html"')

        # PDF
        if pdf:
            pdf_in = output_file + '.html'
            pdf_out = output_file + '.pdf'
            PDF_OPTIONS = { 'quiet':''}

            # Header/footer configuration and directory setup for PDF header
            if CONFIG.get(config,'HEADER',fallback=None):
                header_env = Environment(
                    loader=FileSystemLoader(
                        [ os.path.join(CONFIG.get(config,'TEMPLATES_DIR'), 'html', CONFIG.get(config, 'HEADER_DIR')) ]),
                    autoescape=select_autoescape(['html']),
                    trim_blocks=True
                )

                header_template = header_env.get_template(CONFIG.get(config,'HEADER_TEMPLATE') + '.html')
                header = header_template.render({'name': context['Header']['name']})
                
                header_save_file = os.path.join(
                    out_dir,
                    CONFIG.get(config,'HEADER_TEMPLATE') + '.html')
                
                save = save_file(header, header_save_file)
                if save:
                    click.echo(f'Using generated header file for PDF:\n    "{header_save_file}".\n')
                
                PDF_OPTIONS['header-html'] = header_save_file

            for k,v in CONFIG.items(config):
                if k.startswith('pdf'):
                    key = k.replace('pdf_', '').replace('_', '-')
                    PDF_OPTIONS[key] = v
            
            pdfkit.from_file(pdf_in, pdf_out, options=PDF_OPTIONS)
            click.echo(f'Saved PDF file to "{pdf_out}"')

    # TEXT
    if text:
        text = text_template.render(context=context)
        save_file(text,output_file + '.txt')
        click.echo(f'Saved TXT file to \"{output_file + ".txt"}\"')

    click.echo('\n\n'+'End'+'\n')


def save_file(content,output_file):
    ''' Write content 'content' to the file 'output_file. '''
    with open(output_file,'w') as ofile:
        ofile.write(content)
    if os.path.exists(output_file):
        return True
