import os
import sys
source_suffix = '.rst'
copyright = u'2011-2012, Aldebaran Robotics'
version = "{version}"
release = "{version}"
master_doc = 'index'
pygments_style="sphinx"

html_theme_path = ["{themes_path}"]
html_theme="djangodocs"
html_use_index = True

sys.path.insert(0, "{ext_path}")

extensions = ["sphinx.ext.pngmath",
              "sphinx.ext.todo",
              "sphinx.ext.intersphinx",
              "sphinx.ext.ifconfig",
              "doxylink"]

doxylink = {doxylink}
intersphinx_mapping = {intersphinx_mapping}

build_type = os.environ.get("build_type")

if build_type == "release":
    html_show_source_link=False
    html_copy_source=False
    keep_warnings=False
    todo_include_todos=False
else:
    html_show_source_link=True
    html_copy_source=True
    keep_warnings=True
    todo_include_todos=True

def setup(app):
    app.add_config_value("build_type", "internal", True)
