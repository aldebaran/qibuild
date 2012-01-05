import sys, os

# Specific extensions:
sys.path.insert(0, os.path.abspath("../source/tools"))

extensions.extend(["naoqi", "extendcpp", "cppwithparams"])

templates_path = ['../source/_templates']

html_additional_pages = {
    'index'    : 'index.html',
    'contents' : 'contents.html'
}

html_static_path = ['../source/_static']
project = u'NAO Software Documentation'

