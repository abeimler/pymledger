# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from os.path import abspath, dirname
from sphinx.highlighting import lexers
from pygments.lexers.data import YamlLexer

sys.path.insert(0, abspath(dirname(dirname(dirname(__file__)))))

project = 'pYMLedger'
copyright = '2023, Alex Beimler'
author = 'Alex Beimler'
version = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages'
    #'sphinxcontrib.spelling',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'de'
#spelling_lang = 'de_DE'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

pygments_style = 'sphinx'

lexers['yaml'] = YamlLexer()
lexers['yml'] = YamlLexer()