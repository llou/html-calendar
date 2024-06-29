import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'html-calendar'
copyright = '2023, Jorge Monforte González'
author = 'Jorge Monforte González'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage',
              'sphinx.ext.napoleon', 'sphinx_rtd_theme']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
