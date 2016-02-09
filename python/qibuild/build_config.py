## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import platform

import qisys.error
import qisys.sh
import qisys.qixml
import qibuild.cmake
import qibuild.config
import qibuild.profile
import qitoolchain


class CMakeBuildConfig(object):
    """ Compute a list of CMake flags from all the settings
    that can affect the build  (the toolchain name, the build
    profiles, etc ...)

    """
    def __init__(self, build_worktree):
        self.build_worktree = build_worktree
        self.build_type = "Debug"
        self.active_build_config = None
        self.build_prefix = None
        self.user_flags = list()
        self._profiles = list()
        self._profile_flags = list()
        self.verbose_make = False
        self._default_config = None
        self.qibuild_cfg = qibuild.config.QiBuildConfig()
        self.qibuild_cfg.read(create_if_missing=True)
        self._cmake_generator = None
        self.read_local_settings()
        self.num_jobs = None
        self._toolchain = None

    @property
    def profiles(self):
        return self._profiles

    @property
    def local_cmake(self):
        """ Path to the "custom" CMake file. Its content will be added
        to the generated CMake files when running ``qibuild configure``

        :returns: None if the custom CMake file does not exist
        """
        if not self.active_build_config:
            return None
        custom_cmake = os.path.join(self.build_worktree.root, ".qi",
                                    self.active_build_config.name + ".cmake")
        if os.path.exists(custom_cmake):
            return custom_cmake
        else:
            return None

    @property
    def toolchain(self):
        """ The current toolchain, either set by the user from the command
        line or read from the local qibuild settings

        """
        if self._toolchain:
            return self._toolchain
        if self.active_build_config:
            toolchain_name = self.active_build_config.toolchain
            if toolchain_name:
                self._toolchain = qitoolchain.get_toolchain(toolchain_name)
            return self._toolchain
        else:
            return None

    @property
    def cmake_generator(self):
        """ The current CMake generator, either set by the user from the command
        line or read from the qibuild configuration files

        """
        if self._cmake_generator:
            return self._cmake_generator
        return self.qibuild_cfg.cmake.generator

    @property
    def debug(self):
        """ Whether we are building in debug. True unless user
        specified --release

        """
        return self.build_type == "Debug"

    @property
    def using_make(self):
        """ Whether we are using make """
        return self.cmake_generator and "Unix Makefiles" in self.cmake_generator

    @property
    def using_visual_studio(self):
        " Whether we are using visual studio "
        return self.cmake_generator and "Visual Studio" in self.cmake_generator

    @property
    def using_mingw(self):
        return self.cmake_generator and "mingw" in self.cmake_generator.lower()

    # pylint: disable-msg=E1101
    @cmake_generator.setter
    # pylint: disable-msg=E0102
    def cmake_generator(self, value):
        self._cmake_generator = value

    @property
    def build_env(self):
        """ A dictionary defining the environment used when building, as
        read from qibuild configuration files.
        ``os.environ`` will remain unchanged

        """
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.read_config(self.qibuild_cfg)
        return envsetter.get_build_env()

    def build_directory(self, prefix="build", name=None, system=False):
        """ Return a suitable build directory, making sure
        there is one build directory per config name.

        If name is None, read the active build config
        (set by the user with ``-c``, or read as the default config for the worktree0

        If system is True, returns ``sys-<system>-<arch>``
        """
        if prefix:
            res = prefix + "-"
        else:
            res = ""

        if name:
            res += name
        else:
            if self.active_build_config and not system:
                res += self.active_build_config.name
            else:
                res += "sys-%s-%s" % (platform.system().lower(),
                                    platform.machine().lower())

        return res

    @property
    def cmake_args(self):
        """ The CMake arguments to use

        """
        self.parse_profiles(warns=False)
        args = list()
        if self.cmake_generator:
            args.append("-G%s" % self.cmake_generator)
        if self.toolchain:
            args.append("-DCMAKE_TOOLCHAIN_FILE=%s" % self.toolchain.toolchain_file)
        args.append("-DCMAKE_BUILD_TYPE=%s" % self.build_type)

        for (name, value) in self._profile_flags:
            args.append("-D%s=%s" % (name, value))
        for (name, value) in self.user_flags:
            args.append("-D%s=%s" % (name, value))

        # Set QI_VIRTUALENV_PATH (useful when calling Python code from
        # C++)
        venv_path = self.build_worktree.venv_path
        args.append("-DQI_VIRTUALENV_PATH=%s" % qisys.sh.to_posix_path(venv_path))

        # Set qibuild_DIR in cache so that re-running CMake from an IDE
        # finds qibuild cmake modules
        cmake_qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
        cmake_qibuild_dir = os.path.join(cmake_qibuild_dir, "qibuild")
        cmake_qibuild_dir = qisys.sh.to_posix_path(cmake_qibuild_dir)
        args.append("-Dqibuild_DIR=%s" % cmake_qibuild_dir)

        return args

    @property
    def default_config(self):
        """ The default configuration, as read from the local build settings """
        self.read_local_settings()
        return self._default_config

    def read_local_settings(self):
        """ Read ``<worktree>/.qi/qibuild.xml`` """
        local_settings = qibuild.config.LocalSettings()
        tree = qisys.qixml.read(self.build_worktree.qibuild_xml)
        local_settings.parse(tree)
        self.build_prefix = local_settings.build.prefix
        if self.build_prefix and not os.path.isabs(self.build_prefix):
            self.build_prefix = os.path.join(self.build_worktree.root, self.build_prefix)
            self.build_prefix = qisys.sh.to_native_path(self.build_prefix)

        # Legacy: in .qi/qibuild.xml
        default_config = local_settings.defaults.config
        if not default_config:
            # New location: in ~/.config/qi/qibuild.xml
            self.qibuild_cfg.read()
            default_config = self.qibuild_cfg.get_default_config_for_worktree(
                                    self.build_worktree.root)
        if default_config:
            matching_config = self.qibuild_cfg.configs.get(default_config)
            if not matching_config:
                mess = """ \
Incorrect config detected for worktree in {build_worktree.root}
Default config is {default_config} but this does not match any
config in ~/.config/qi/qibuild.xml
"""
                mess = mess.format(build_worktree=self.build_worktree,
                                default_config=default_config)
                raise qisys.error.Error(mess)
            self._default_config = matching_config.name
            self.set_active_config(matching_config.name)

    def parse_profiles(self, warns=True):
        self._profile_flags = list()
        known_profiles = self.build_worktree.get_known_profiles(warns=warns)
        known_names = known_profiles.keys()
        for name in self._profiles:
            if not name in known_names:
                raise NoSuchProfile(name, known_names)
            flags = known_profiles[name].cmake_flags
            self._profile_flags.extend(flags)

    def set_active_config(self, config_name):
        """ Set the active configuration. This should match an
        existing config name

        Used when running ``qibuild configure -c <config>``

        """
        self.qibuild_cfg.read()
        self.active_build_config = self.qibuild_cfg.configs.get(config_name)
        if not self.active_build_config:
            raise qisys.error.Error("No such build config: %s" % config_name)
        self.qibuild_cfg.set_active_config(config_name)
        if self.active_build_config:
            self._profiles = self.active_build_config.profiles
            self.parse_profiles()

class NoSuchProfile(qisys.error.Error):
    """ The profile specified by the user cannot be found """
    def __init__(self, name, known_profiles):
        self.name = name
        self.known_profiles = known_profiles

    def __str__(self):
        return """ Could not find profile {name}.
Known profiles are: {profiles}
""".format(name=self.name,
           profiles=', '.join(sorted(self.known_profiles)))
