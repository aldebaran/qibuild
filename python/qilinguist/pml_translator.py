import os

import qisys.command
import qisys.qixml

def new_pml_translator(pml_path):
    return PMLTranslator(pml_path)

class PMLTranslator(object):
    def __init__(self, pml_path):
        self.pml_path = pml_path
        self.path = os.path.dirname(pml_path)
        self.ts_files = translations_files_from_pml(pml_path)

    def update(self):
        raise NotImplementedError()

    def release(self):
        for ts_file in self.ts_files:
            qm_file = ts_file.replace(".ts", ".qm")
            input = os.path.join(self.path, ts_file)
            output = os.path.join(self.path, qm_file)
            cmd = ["lrelease", "-compress", input, "-qm", output]
            qisys.command.call(cmd)

    def __repr__(self):
        return "<PMLTranslator for %s>" % self.pml_path


def translations_files_from_pml(pml_path):
    res = list()
    tree = qisys.qixml.read(pml_path)
    root = tree.getroot()
    translations_elem = root.find("Translations")
    if translations_elem is None:
        return list()
    translation_elems = translations_elem.findall("Translation")
    for translation_elem in translation_elems:
        res.append(translation_elem.get("src"))
    return res
