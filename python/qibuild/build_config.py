import os
import qisys.qixml


import qibuild.config
import qibuild.profile
import qitoolchain
import platform


class CMakeBuildConfig(object):
    """ Compute a list of CMake flags from all the settings
    that can affect the build  (the toolchain name, the build
    profiles, etc ...)


    """
    def __init__(self, build_worktree):
        self.active_config = None
        self.build_worktree = build_worktree
        self.build_type = "Debug"
        self.user_flags = list()
        self.profiles = list()
        self.verbose_make = False
        self._default_config = None
        self.qibuild_cfg = self.read_global_qibuild_settings()
        self._cmake_generator = None
        self.read_local_settings()
        self.num_jobs = None


    @property
    def local_cmake(self):
        """ Path to the "custom" CMake file. Its content will be added
        to the generated CMake files when running ``qibuild configure``

        :returns: None if the custom CMake file does not exist
        """
        if not self.active_config:
            return None
        custom_cmake = os.path.join(self.build_worktree.root, ".qi",
                                    self.active_config + ".cmake")
        if os.path.exists(custom_cmake):
            return custom_cmake
        else:
            return None

    @property
    def toolchain(self):
        """ The current toolchain, either set by the user from the command
        line or read from the local qibuild settings

        """
        if self.active_config:
            return qitoolchain.get_toolchain(self.active_config)
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
        """ Wether we are building in debug. True unless user
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
        """ A dict defining the environnment used when building, as
        read from qibuild configuration files.
        ``os.environ`` will remain unchanged

        """
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.read_config(self.qibuild_cfg)
        return envsetter.get_build_env()

    def build_directory(self, prefix="build"):
        """ Return a suitable build directory, depending on the
        build setting of the worktree: the name of the toolchain,
        the build profiles, and the build type (debug/release)
        """
        parts = [prefix]
        if self.toolchain:
            parts.append(self.toolchain.name)
        else:
            parts.append("sys-%s-%s" % (platform.system().lower(),
                                        platform.machine().lower()))
        for profile in self.profiles:
            parts.append(profile)

        if self.build_type and self.build_type != "Debug":
            parts.append(self.build_type.lower())
        return "-".join(parts)


    @property
    def cmake_args(self):
        """ The CMake arguments to use

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

    @property
    def default_config(self):
        """ The default configuration, as read from the local build settings """
        self.read_local_settings()
        return self._default_config


    def read_global_qibuild_settings(self):
        """ Read ``~/.config/qi/qibuild.xml`` """
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(create_if_missing=True)
        return qibuild_cfg

    def read_local_settings(self):
        """ Read ``<worktree>/.qi/qibuild.xml`` """
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
        self._default_config = default_config
        self.qibuild_cfg.set_active_config(default_config)
        self.set_active_config(default_config)

    def set_active_config(self, active_config):
        """ Set the active configuration. This should match an
        existing toolchain name.

        Used when running ``qibuild configure -c <config>``

        """
        self.active_config = active_config
        self.qibuild_cfg.set_active_config(active_config)
