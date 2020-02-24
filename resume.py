'''
    Title:          Resume Builder Module
    Description:    Create a HTML version of a resume based on YAML data files
                    and convert to PDF.
'''

import os
from datetime import datetime
from glob import glob
from collections import OrderedDict
import configparser
import yaml, pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape
import click


@click.group()
def cli():
    pass


def load_config(source_dir):
    GlobalConfig = configparser.ConfigParser(defaults={ 'TEMPLATES_DIR': 'Templates',
                                                        'SOURCES_DIR': 'Resume Data',
                                                        'PUBLISH_DIR': 'Publish' })
    GlobalConfig.read('config.ini')
    SOURCES_DIR = GlobalConfig.get('DEFAULT','SOURCES_DIR')

    LocalConfig = configparser.ConfigParser(defaults = { 'HTML_TEMPLATE': 'default',
                                                         'TEXT_TEMPLATE': 'default',
                                                         'PDF_MARGIN_TOP': '0.5in',
                                                         'PDF_MARGIN_RIGHT': '0.5in',
                                                         'PDF_MARGIN_BOTTOM': '0.5in',
                                                         'PDF_MARGIN_LEFT': '0.5in',
                                                         'PDF_PAGE_SIZE': 'Letter' })
    LocalConfig.read(os.path.join(SOURCES_DIR,source_dir,'config.ini'))
    
    # set any properties that should be parsed with other than just get()
    dtypes = { 'PDF_DISABLE_EXTERNAL_LINKS': lambda x: x.getboolean }

    CONFIG = {}
    
    for config in [GlobalConfig,LocalConfig]:
        for key in config['DEFAULT']:
            keyu = key.upper()
            if keyu in dtypes.keys():
                CONFIG[keyu] = dtypes[keyu](config)('DEFAULT', key)
            else:
                CONFIG[keyu] = config.get('DEFAULT', key)

    CONFIG['PDF_OPTIONS'] = { 'margin-top': CONFIG['PDF_MARGIN_TOP'],
                              'margin-right': CONFIG['PDF_MARGIN_RIGHT'],
                              'margin-bottom': CONFIG['PDF_MARGIN_BOTTOM'],
                              'margin-left': CONFIG['PDF_MARGIN_LEFT'],
                              'page-size': CONFIG['PDF_PAGE_SIZE'],
                              'disable-external-links': False }
    
    return CONFIG


@click.command()
@click.argument('source_dir')
@click.option('--name',default=None,help='Specify an alternate filename for published files. Default is source_dir.')
def build(source_dir,name):
    '''
        Generate HTML, PDF, and text versions of a resume and save them in a
        directory.

        SOURCE_DIR is the name of a folder in the 'Resume Data' folder.
    '''
    CONFIG = load_config(source_dir)

    context = { 'title': True } if CONFIG.get('TITLE') else { 'title': False }

    # Create a new directory to put files in (autorename to avoid overwriting)
    new_folder = source_dir + ' - ' + datetime.today().strftime('%d%b-%Y')
    if os.path.exists(os.path.join(CONFIG['PUBLISH_DIR'],new_folder)):
        i = 1
        while os.path.exists(os.path.join(CONFIG['PUBLISH_DIR'],new_folder+' ({})'.format(i))):
            i += 1
        new_folder = new_folder+' ({})'.format(i)
    os.mkdir(os.path.join(CONFIG['PUBLISH_DIR'],new_folder))
    
    out_dir = os.path.join(CONFIG['PUBLISH_DIR'],new_folder)
    
    if name:
        output_file = os.path.join(out_dir,name)
    else:
        output_file = os.path.join(out_dir,source_dir)

    context['TEMPLATE_DIR_REL'] = os.path.relpath(CONFIG['TEMPLATES_DIR'],out_dir)

    # Load resume data into variable 'context'
    #  - only changed files are added to new directory
    #  - all other unchanged data will be loaded from 'default' directory

    source_files = glob(CONFIG['SOURCES_DIR']+'\\{}\\*.yaml'.format(source_dir))
    source_file_names = list(map(lambda f: os.path.basename(f), source_files))
    default_files = glob(CONFIG['SOURCES_DIR']+'\\Default\\*.yaml')

    for fname in default_files:
        if os.path.basename(fname) in source_file_names:
            bn = os.path.basename(fname)
            fname = list(filter(lambda f: bn in f, source_files))[0]
        with open(fname) as f:
            name = os.path.basename(fname)
            name = os.path.splitext(name)[0].replace('-','_').replace(' ','_')
            context[name] = yaml.safe_load(f)
    
    # Setup Jinja templating
    env = Environment(
        loader=FileSystemLoader([os.path.join(CONFIG['TEMPLATES_DIR'],'html'),os.path.join(CONFIG['TEMPLATES_DIR'],'text')]),
        autoescape=select_autoescape(['html']),
        trim_blocks=True
    )
    
    # Load templates
    def load_template(type,selection):
        if not selection:
            return env.get_template('default.'+type)
        else:
            return env.get_template(selection+'.'+type)
    
    html_template = load_template('html', CONFIG.get('HTML_TEMPLATE'))
    text_template = load_template('txt', CONFIG.get('TEXT_TEMPLATE'))
    
    # Layout the skills section if configured to do so
    if CONFIG.get('SKILLS_LAYOUT'):
        sl = list(map(lambda x: x.split(','), CONFIG['SKILLS_LAYOUT'].split('|')))
        for i,each in enumerate(sl):
            sl[i] = list(map(lambda x: x.strip(), each))

        context['skills_layout'] = sl

    # HTML
    html = html_template.render(context=context)
    save_file(html,output_file+'.html')
    print('Saved HTML\n')

    # PDF
    pdf_in = output_file+'.html'
    pdf_out = output_file+'.pdf'
    pdfkit.from_file(pdf_in, pdf_out, options=CONFIG['PDF_OPTIONS'])
    print('\nSaved PDF\n')

    # TEXT
    text = text_template.render(context=context)
    save_file(text,output_file+'.txt')
    print('Saved TXT\n')


def save_file(content,output_file):
    ''' Write content 'content' to the file 'output_file. '''
    with open(output_file,'w') as ofile:
        ofile.write(content)


cli.add_command(build)


if __name__ == '__main__':
    cli()
