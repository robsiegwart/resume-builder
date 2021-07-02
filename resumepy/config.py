'''
Configuration handling.
'''

import configparser
import os


DEFAULT_CONFIG = {
    'DEFAULT': {
        'TEMPLATES_DIR' :              'Templates',
        'SOURCES_DIR' :                'Resume Data',
        'PUBLISH_DIR' :                'Publish',
        'HTML_TEMPLATE' :              'default',
        'HEADER':                      '',
        'HEADER_DIR':                  'headers',
        'HEADER_TEMPLATE':             'header_default',
        'TEXT_TEMPLATE' :              'default',
        'PDF_MARGIN_TOP' :             '0.5in',
        'PDF_MARGIN_RIGHT' :           '0.5in',
        'PDF_MARGIN_BOTTOM' :          '0.5in',
        'PDF_MARGIN_LEFT' :            '0.5in',
        'PDF_PAGE_SIZE' :              'Letter',
        'PDF_DISABLE_EXTERNAL_LINKS' : '',
        'TITLE':                       '',
    }
}


def load_config(source_dir):
    CONFIG = configparser.ConfigParser()
    CONFIG.read_dict(DEFAULT_CONFIG)
    # Try to read any global config
    CONFIG.read('config.ini')
    # Try to read any config.ini saved in the source directory
    CONFIG.read(os.path.join(
        CONFIG.get('DEFAULT', 'SOURCES_DIR'),
        source_dir,
        'config.ini'
    ))
    return CONFIG