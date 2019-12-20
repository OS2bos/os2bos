# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import django

current_dir = os.path.dirname(__file__)
python_sources = os.path.abspath(os.path.join(current_dir, "..", "..", "backend"))
sys.path.insert(0, python_sources)
os.environ["DJANGO_SETTINGS_MODULE"] = "bevillingsplatform.settings"
os.environ["BEV_USER_CONFIG_PATH"] = "../../dev-environment/test-settings.ini"
django.setup()

os.environ["SPHINXBUILDING"] = "YES"


# -- Project information -----------------------------------------------------

project = "bevillingsplatform"
copyright = "2019, Magenta ApS"
author = "Magenta ApS"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinxcontrib_django"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

master_doc = "index"
