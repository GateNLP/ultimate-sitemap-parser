# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys, os

sys.path.append(os.path.abspath('extensions'))

from usp import __version__ as usp_version


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information



project = 'Ultimate Sitemap Parser'
copyright = '2018-2024, Ultimate Sitemap Parser Contributors'
author = 'Ultimate Sitemap Parser Contributors'
release = usp_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.extlinks',
    'sphinx_design',
    'sphinxext.opengraph',
    'sphinx_copybutton',
    'custom_graphviz'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

modindex_common_prefix = ['usp.']

nitpicky = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

_gh_root = 'https://github.com/GateNLP/ultimate-sitemap-parser'

html_theme = 'furo'
html_static_path = ['_static']
html_title = 'Ultimate Sitemap Parser'
html_css_files = [
    'css/custom.css',
]
html_theme_options = {
    'source_repository': _gh_root,
    'source_branch': 'main',
    'source_directory': 'docs/'
}
html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "https://usp-dummy.gate.ac.uk/")

# -- Extension Config --------------------------------------------------------

autodoc_class_signature = 'separated'
autodoc_member_order = 'groupwise'

extlinks = {
    'issue': (f'{_gh_root}/issues/%s', '#%s'),
    'pr': (f'{_gh_root}/pull/%s', '#%s'),
    'user': (f'https://github.com/%s', '@%s'),
    'commit': (f'{_gh_root}/commit/%s', '%.7s'),
}

graphviz_output_format = 'svg'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'dateutil': ('https://dateutil.readthedocs.io/en/stable', None),
    'requests': ('https://requests.readthedocs.io/en/latest', None)
}

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 3

pygments_style = "friendly"

coverage_show_missing_items = True

copybutton_exclude = '.linenos'
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
