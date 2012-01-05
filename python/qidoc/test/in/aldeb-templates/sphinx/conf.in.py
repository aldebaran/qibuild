import os
import sys
source_suffix = '.rst'
copyright = u'2011-2012, Aldebaran Robotics'
version = "{version}"
release = "{version}"
master_doc = 'index'
pygments_style="sphinx"

html_theme_path = ["_themes"]
html_theme="djangodocs"
html_use_index = True

extensions = ["sphinx.ext.pngmath",
              "sphinx.ext.todo",
              "sphinx.ext.intersphinx",
              "doxylink"]

sys.path.insert(0, os.path.abspath("tools/doxylink"))
doxylink = {doxylink}
intersphinx_mapping = {intersphinx_mapping}

# Useful when building internal doc,
# we should remove that when building
# official doc
nitpicky=True
keep_warnings=True
html_show_source_link=True
todo_include_todos=True
