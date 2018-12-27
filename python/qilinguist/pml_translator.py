#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qilinguist.project
import qilinguist.qtlinguist
import qisys.qixml
import qisys.command
from qisys import ui


def new_pml_translator(pml_path):
    """ New Pml Translator """
    return PMLTranslator(pml_path)


class PMLTranslator(qilinguist.project.LinguistProject):
    """ PMLTranslator Class """

    def __init__(self, pml_path):
        """ PMLTranslator Init """
        self.pml_path = pml_path
        self.path = os.path.dirname(pml_path)
        self.ts_files = translations_files_from_pml(pml_path)
        self.qm_files = list()
        path = os.path.dirname(pml_path)
        name = get_name(pml_path)
        super(PMLTranslator, self).__init__(name, path)

    def update(self):
        """ Update """
        raise NotImplementedError()

    def release(self, raises=True, build_config=None):
        """ Release """
        all_ok = True
        lrelease = qisys.command.find_program("lrelease", raises=True, build_config=build_config)
        for ts_file in self.ts_files:
            qm_file = ts_file.replace(".ts", ".qm")
            input_file = os.path.join(self.path, ts_file)
            output_file = os.path.join(self.path, qm_file)
            ok, message = qilinguist.qtlinguist.generate_qm_file(input_file, output_file)
            if not ok:
                ui.error(message)
                all_ok = False
            cmd = [lrelease, "-compress", input_file, "-qm", output_file]
            qisys.command.call(cmd)
            self.qm_files.append(output_file)
        if not all_ok and raises:
            raise Exception("`qilinguist release` failed")
        return all_ok

    def install(self, dest):
        """ Install """
        translations_dest = os.path.join(dest, "translations")
        qisys.sh.mkdir(translations_dest, recursive=True)
        for qm_file in self.qm_files:
            qisys.sh.install(qm_file, translations_dest)

    def __repr__(self):
        """ Represenation """
        return "<PMLTranslator for %s>" % self.pml_path


def translations_files_from_pml(pml_path):
    """ Translations Files From Pml """
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


def get_name(pml_path):
    """ Get Name """
    tree = qisys.qixml.read(pml_path)
    root = tree.getroot()
    return qisys.qixml.parse_required_attr(root, "name", xml_path=pml_path)
