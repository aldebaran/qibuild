# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import re

from qisys import ui
import qisys.qixml
import qisys.version


def bump_version(xml_path, version=None):
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
        return not self.errors

    def print_errors(self):
        if not self.errors:
            return

        ui.info(ui.red, "\nPackage errors:")
        for error in self.errors:
            ui.info(ui.bold, "\t%s" % error)

    def print_warnings(self):
        if not self.warnings:
            return

        ui.info(ui.yellow, "\nPackage warnings:")
        for warning in self.warnings:
            ui.info(ui.bold, "\t%s" % warning)

    def _load_manifest(self, manifest_path):
        tree = qisys.qixml.read(manifest_path)
        self.manifest_root = tree.getroot()

    def _add_error(self, error_message):
        self.errors.append(error_message)

    def _add_warning(self, warning_message):
        self.warnings.append(warning_message)

    def _validate_uid(self):
        uid = self.manifest_root.get('uuid', '')
        if not uid:
            self._add_error("Application UID is not defined.")
        elif re.match(r"[_\-a-z0-9]{1,50}\Z", uid) is None:
            self._add_error("Application UID is not defined correctly.")

    def _validate_version(self):
        version = self.manifest_root.get('version', '0.0.0.0')
        if qisys.version.compare(version, '0.0.0.0') < 1:
            self._add_error("Application version has to be greater that '0.0.0.0'.")

    def _validate_robot_requirements(self):
        robot_requirements = self.manifest_root.findall(
            "requirements/robotRequirement")
        if not robot_requirements:
            self._add_error("Robot requirements are not defined.")
            return

        for requirement in robot_requirements:
            if requirement.get('model', '') == '':
                self._add_error("A robot requirement has no model defined.")

    def _validate_naoqi_requirements(self):
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
        supported_languages = self.manifest_root.findall(
            "supportedLanguages/language")
        for supported_language in supported_languages:
            if self.manifest_root.find("descriptions/description[@lang=\'%s\']"
                                       % supported_language.text) is None:
                self._add_warning("Application description is "
                                  "not defined for \'%s\'."
                                  % supported_language.text)
