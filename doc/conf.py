import os
import sys
sys.path.insert(0, os.path.abspath(".."))
import mandb

master_doc = "index"

project = "Mandb"
copyright = "2016, Kehr"

version = release = mandb.version

extensions = ["sphinx.ext.autodoc", "sphinx.ext.coverage", "sphinx.ext.viewcode"]

primary_domain = 'py'
default_role = 'py:obj'

autodoc_member_order = "bysource"
autoclass_content = "both"

coverage_skip_undoc_in_source = True
