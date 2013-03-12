import qibuild.profile
import qitoolchain


class CMakeBuildConfig(object):
    """ Just a container for the various settings
    that can affect the build

    """
    # FIXME: what about qibuild config files ?
    def __init__(self, toolchain_name=None,
                 build_type="Debug", cmake_generator=None,
                 user_flags=None, profiles=None):
        if toolchain_name:
            self.toolchain = qitoolchain.get_toolchain(toolchain_name)
        else:
            self.toolchain = None
        self.build_type = build_type
        self.cmake_generator = cmake_generator
        if user_flags is None:
            self.user_flags = list()
        else:
            self.user_flags = user_flags[:]
        if profiles is None:
            self.profiles = list()
        else:
            self.profiles = profiles[:]

    @property
    def visual_studio(self):
        return self.cmake_generator and \
                "Visual Studio" in self.cmake_generator

    def cmake_args(self, build_worktree):
        """ Compute the CMake arguments to use, using the
        profiles registered in the given worktree

        """
        args = list()
        if self.cmake_generator:
            args.append("-G%s" % self.cmake_generator)
        if self.toolchain:
            args.append("-DCMAKE_TOOLCHAIN_FILE=%s" % self.toolchain.toolchain_file)
        args.append("-DCMAKE_BUILD_TYPE=%s" % self.build_type)
        cmake_flags = qibuild.profile.get_cmake_flags(build_worktree.qibuild_xml,
                                                      self.profiles)
        for (name, value) in cmake_flags:
            args.append("-D%s=%s" % (name, value))
        for (name, value) in self.user_flags:
            args.append("-D%s=%s" % (name, value))
        return args
