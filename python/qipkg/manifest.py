#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import re

import qisys.qixml
import qisys.version
from qisys import ui


def bump_version(xml_path, version=None):
    """ Bump Version """
    tree = qisys.qixml.read(xml_path)
    root = tree.getroot()
    if version is None:
        previous_version = root.get("version")
        version = qisys.version.increment_version(previous_version)
    root.set("version", version)
    qisys.qixml.write(tree, xml_path)


class Validator(object):
    """ Check if a manifest xml is valid """

    def __init__(self, manifest_path):
        """ Validator Init """
        self.errors = list()
        self.warnings = list()
        self.manifest_root = None
        self._load_manifest(manifest_path)
        self._validate_uid()
        self._validate_version()
        self._validate_robot_requirements()
        self._validate_naoqi_requirements()
        self._validate_trigger_sentences()
        self._validate_names()
        self._validate_description()

    @property
    def is_valid(self):
        """ Is Valid """
        return not self.errors

    def print_errors(self):
        """ Print Errors """
        if not self.errors:
            return
        ui.info(ui.red, "\nPackage errors:")
        for error in self.errors:
            ui.info(ui.bold, "\t%s" % error)

    def print_warnings(self):
        """ Print Warnings """
        if not self.warnings:
            return
        ui.info(ui.yellow, "\nPackage warnings:")
        for warning in self.warnings:
            ui.info(ui.bold, "\t%s" % warning)

    def _load_manifest(self, manifest_path):
        """ Load Manifest """
        tree = qisys.qixml.read(manifest_path)
        self.manifest_root = tree.getroot()

    def _add_error(self, error_message):
        """ Add Error """
        self.errors.append(error_message)

    def _add_warning(self, warning_message):
        """ Add Warning """
        self.warnings.append(warning_message)

    def _validate_uid(self):
        """ Validate UUID """
        uid = self.manifest_root.get('uuid', '')
        if not uid:
            self._add_error("Application UID is not defined.")
        elif re.match(r"[_\-a-z0-9]{1,50}\Z", uid) is None:
            self._add_error("Application UID is not defined correctly.")

    def _validate_version(self):
        """ Validate Version """
        version = self.manifest_root.get('version', '0.0.0.0')
        if qisys.version.compare(version, '0.0.0.0') < 1:
            self._add_error("Application version has to be greater that '0.0.0.0'.")

    def _validate_robot_requirements(self):
        """ Validate Robot Requirements """
        robot_requirements = self.manifest_root.findall(
            "requirements/robotRequirement")
        if not robot_requirements:
            self._add_error("Robot requirements are not defined.")
            return
        for requirement in robot_requirements:
            if requirement.get('model', '') == '':
                self._add_error("A robot requirement has no model defined.")

    def _validate_naoqi_requirements(self):
        """ Validate NAOqi Requirements """
        naoqi_requirements = self.manifest_root.findall(
            "requirements/naoqiRequirement")
        if not naoqi_requirements:
            self._add_error("NAOqi requirements are missing.")
            return
        for requirement in naoqi_requirements:
            if requirement.get('minVersion', '') == '':
                self._add_error("A NAOqi requirement has no "
                                "minimum version defined.")

    def _validate_trigger_sentences(self):
        """ Validate Trigger Sentences """
        if not self.manifest_root.findall(
                "contents/behaviorContent/triggerSentences/sentence"):
            return
        supported_languages = self.manifest_root.findall(
            "supportedLanguages/language")
        for behavior_content in self.manifest_root.findall(
                "contents/behaviorContent"):
            for supported_language in supported_languages:
                if behavior_content.find(
                        ".//triggerSentences/sentence[@lang=\'%s\']"
                        % supported_language.text) is None:
                    self._add_error("Behavior \'%s\' has no trigger "
                                    "sentence defined for \'%s\'."
                                    % (behavior_content.get("path"),
                                       supported_language.text))

    def _validate_names(self):
        """ Validate Names """
        supported_languages = self.manifest_root.findall(
            "supportedLanguages/language")
        for supported_language in supported_languages:
            if self.manifest_root.find("names/name[@lang=\'%s\']"
                                       % supported_language.text) is None:
                if supported_language.text == 'en_US':
                    self._add_error("Application name is "
                                    "not defined for \'%s\'."
                                    % supported_language.text)
                else:
                    self._add_warning("Application name is "
                                      "not defined for \'%s\'."
                                      % supported_language.text)

    def _validate_description(self):
        """ Validate Description """
        supported_languages = self.manifest_root.findall(
            "supportedLanguages/language")
        for supported_language in supported_languages:
            if self.manifest_root.find("descriptions/description[@lang=\'%s\']"
                                       % supported_language.text) is None:
                self._add_warning("Application description is "
                                  "not defined for \'%s\'."
                                  % supported_language.text)
