import click
import os
import sys
from distutils.dir_util import copy_tree
from shutil import copy


SAMPLE_FOLDERS = ['Sample Templates', 'Sample Data']


def init():
    '''
    Copy the sample data to the user's working directory.
    '''
    click.echo('Copying sample data into the current directory ...')
    pkg_dir = os.path.dirname(sys.modules[__name__].__file__)
    wd = os.getcwd()
    
    clean_install = []
    
    for folder in SAMPLE_FOLDERS:
        if not os.path.exists(os.path.join(wd,folder)):
            copy_tree(os.path.join(pkg_dir,'data',folder), os.path.join(wd,folder))
            click.echo(f'  {folder}/')
            clean_install.append(True)
            continue

        click.echo(f'  Folder "{folder}" already exists in current directory. Skipping ...')
        clean_install.append(False)
    
    # copy config.ini file
    if not os.path.exists('config.ini'):
        copy(os.path.join(pkg_dir,'data','config.ini'), wd)
        click.echo('  Config file "config.ini"')
        clean_install.append(True)
    
    else:
        click.echo('  Existing global "config.ini" file found in current directory. Skipping ...')
        clean_install.append(False)
    
    
    if all(clean_install):
        click.echo('\nTo start, issue:\n\n    resumepy build Default\n\n')
