'''
    Create a HTML version of a resume based on YAML data files.

'''

import os
from datetime import datetime
from glob import glob
from collections import OrderedDict
import yaml, pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape



TEMPLATES_DIR = 'Templates'
SOURCES_DIR = 'Resume Data'
PUBLISH_DIR = 'Publish'


def build_resume(output_file, source_dir='default', html_template='default',
                 text_template='default', skills_col=4, skills_layout=None,
                 title=True, pdf_options=None):
    ''' Main build command. Generates html, pdf, and text versions of resume and
        saves them in a directory.

    Parameters
    ----------
    output_file : str
        base name of output file(s) (w/o extension)
    source_dir : str
        name of directory to load data from
    html_template : str
        name of template to use for html/pdf generation
    text_template : str
        name of template to use for text generation
    skills_col : int
        number of columns for the skills section
    skills_layout : list
        list of lists containing the skills headings in order to be printed
    title : boolean
        show or not the title field
    pdf_options : dict
        a dictionary of parameters to send to wkhtmltopdf
        
    '''
    context = {'title': title}

    # Create a new directory to put files in (autorename to avoid overwriting)
    new_folder = datetime.today().strftime('%d%b-%Y') + ' - ' + output_file
    if os.path.exists(os.path.join(PUBLISH_DIR,new_folder)):
        i = 1
        while os.path.exists(os.path.join(PUBLISH_DIR,new_folder+' ({})'.format(i))):
            i += 1
        new_folder = new_folder+' ({})'.format(i)
    os.mkdir(os.path.join(PUBLISH_DIR,new_folder))
    
    out_dir = os.path.join(PUBLISH_DIR,new_folder)
    output_file = os.path.join(out_dir,output_file)
    context['TEMPLATE_DIR_REL'] = os.path.relpath(TEMPLATES_DIR,out_dir)

    # Load resume data into variable 'context'
    #  - only changed files need to be added to new directory
    #  - all other unchanged data will be loaded from 'default' directory

    source_files = glob(SOURCES_DIR+'\\{}\\*.yaml'.format(source_dir))
    source_file_names = list(map(lambda f: os.path.basename(f), source_files))
    default_files = glob(SOURCES_DIR+'\\Default\\*.yaml')

    for fname in default_files:
        if os.path.basename(fname) in source_file_names:
            bn = os.path.basename(fname)
            fname = list(filter(lambda f: bn in f, source_files))[0]
        with open(fname) as f:
            name = os.path.basename(fname)
            name = os.path.splitext(name)[0].lower().replace('-','_').replace(' ','_')
            context[name] = yaml.safe_load(f)

    # Setup Jinja templating
    env = Environment(
        loader=FileSystemLoader([os.path.join(TEMPLATES_DIR,'html'),os.path.join(TEMPLATES_DIR,'text')]),
        autoescape=select_autoescape(['html']),
        trim_blocks=True
    )
    
    # Load templates
    def load_template(type,selection):
        if not selection:
            return env.get_template('default.'+type)
        else:
            return env.get_template(selection+'.'+type)
    
    html_template = load_template('html', html_template)
    text_template = load_template('txt', text_template)
    
    # Layout the skills section if it exceeds the number of columns
    cats = len(context.get('skills').get('Skills').keys())       # number of skill categories
    if cats > skills_col:
        if not skills_layout:
            skills_layout = []                                   # category labels for each column (ordered left to right)
            skills = OrderedDict(sorted(context['skills']['Skills'].items(), key = lambda t: len(t[1]), reverse=True))  # sort by num of skills
            b = 1
            for i,cat in enumerate(skills.keys()):
                if i < skills_col:
                    skills_layout.append([cat])
                else:
                    skills_layout[skills_col-b].append(cat)
                    b += 1
        context['skills_layout'] = skills_layout

    # Create and save the html version
    html = html_template.render(context=context)
    save_file(html,output_file+'.html')
    
    # Convert and save the pdf file
    pdf_in = output_file+'.html'
    pdf_out = output_file+'.pdf'
    print('Creating pdf ...')
    if pdf_options:
        pdf_options = { **pdf_options_default, **pdf_options}
    else:
        pdf_options = pdf_options_default

    pdfkit.from_file(pdf_in, pdf_out, options=pdf_options)

    # Create and save the text version
    # text = text_template.render(context=context)
    # save_file(text,output_file+'.txt')


def save_file(content,output_file):
    ''' Write content 'content' to the file 'output_file. '''
    with open(output_file,'w') as ofile:
        ofile.write(content)
    print('\nSaved file "{}"'.format(output_file))


pdf_options_default = {
    'margin-top': '14',       # mm
    'margin-bottom': '5',     # mm
    'margin-left': '14',      # mm
    'margin-right': '14',     # mm
    'page-size': 'Letter',
    'disable-external-links': None,
}