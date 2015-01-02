import zipfile

import qisys.qixml
from qisys.qixml import etree

def name_from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    xml_data = archive.read("manifest.xml")
    elem = etree.fromstring(xml_data)
    return elem.get("uuid")
