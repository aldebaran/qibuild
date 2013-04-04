import os
import qisys.qixml

import qibuild.config
import qibuild.profile
import qitoolchain


class CMakeBuildConfig(object):
    """ Just a container for the various settings
    that can affect the build

    """
    def __init__(self, build_worktree):
        self.active_config = None
        self.build_worktree = build_worktree
        self.build_type = "Debug"
        self.user_flags = list()
        self.profiles = list()
        self.qibuild_cfg = self.read_global_qibuild_settings()
        self._cmake_generator = None
        self.read_local_settings()

    @property
    def using_visual_studio(self):
        return self.cmake_generator and "Visual Studio" in self.cmake_generator

    @property
    def local_cmake(self):
        if not self.active_config:
            return None
        custom_cmake = os.path.join(self.build_worktree.root, ".qi",
                                    self.active_config + ".cmake")
        if os.path.exists(custom_cmake):
            return custom_cmake
        else:
            return None

    @property
    def using_make(self):
        return self.cmake_generator and "Unix Makefiles" in self.cmake_generator

    @property
    def cmake_generator(self):
        if self._cmake_generator:
            return self._cmake_generator
        return self.qibuild_cfg.cmake.generator

    @property
    def toolchain(self):
        if self.active_config:
            return qitoolchain.get_toolchain(self.active_config)
        return None

    @cmake_generator.setter
    def cmake_generator(self, value):
        self._cmake_generator = value

    @property
    def build_env(self):
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.read_config(self.qibuild_cfg)
        return envsetter.get_build_env()

    @property
    def cmake_args(self):
        """ Compute the CMake arguments to use, using the
        profiles registered in the given worktree

        """
        args = list()
        if self.cmake_generator:
            args.append("-G%s" % self.cmake_generator)
        if self.toolchain:
            args.append("-DCMAKE_TOOLCHAIN_FILE=%s" % self.toolchain.toolchain_file)
        args.append("-DCMAKE_BUILD_TYPE=%s" % self.build_type)
        cmake_flags = qibuild.profile.get_cmake_flags(self.build_worktree.qibuild_xml,
                                                      self.profiles)
        for (name, value) in cmake_flags:
            args.append("-D%s=%s" % (name, value))
        for (name, value) in self.user_flags:
            args.append("-D%s=%s" % (name, value))
        return args


    def read_global_qibuild_settings(self):
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(create_if_missing=True)
        return qibuild_cfg

    def read_local_settings(self):
        local_settings = qibuild.config.LocalSettings()
        tree = qisys.qixml.read(self.build_worktree.qibuild_xml)
        local_settings.parse(tree)
        default_config = local_settings.defaults.config
        if not default_config:
            return
        try:
            qitoolchain.get_toolchain(default_config)
        except Exception:
            mess = """ \
Incorrect config detected for worktree in {build_worktree.root}
Default config set in .qi/qibuild.xml is {default_config}
but this does not match any toolchain name
"""
            mess = mess.format(build_worktree=self.build_worktree,
                               default_config=default_config)
            raise Exception(mess)
        self.qibuild_cfg.set_active_config(default_config)
        self.set_active_config(default_config)

    def set_active_config(self, active_config):
        self.active_config = active_config
        self.qibuild_cfg.set_active_config(active_config)
