import qibuild.profile
import qitoolchain


class CMakeBuildConfig(object):
    """ Just a container for the various settings
    that can affect the build

    """
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
        self.profiles = profiles

    @property
    def visual_studio(self):
        return "Visual Studio" in self.cmake_generator

    def cmake_args(self, build_worktree):
        import ipdb; ipdb.set_trace()
        args = list()
        if self.cmake_generator:
            args.append("-G%s" % self.cmake_generator)
        if self.toolchain:
            args.append("-DCMAKE_TOOLCHAIN_FILE=%s" % self.toolchain.toolchain_file)
        args.append("-DCMAKE_BUILD_TYPE=%s" % self.build_type)
        cmake_flags = get_cmake_flags(build_worktree, self.profiles)
        for (name, value) in cmake_flags:
            args.append("-D%s=%s" % name, value)
        for (name, value) in self.user_flags:
            args.append("-D%s=%s" % name, value)
        return args

def get_cmake_flags(build_worktree, profile_names):
    cmake_flags = list()
    profiles = qibuild.profile.parse_profiles(build_worktree.qibuild_xml)
    for profile_name in profile_names:
        match = profiles.get(profile_name)
        if not match:
            raise NoSuchProfile(build_worktree, profile_name)
        else:
            cmake_flags.extend(match.cmake_flags)
    return cmake_flags


class NoSuchProfile(Exception):
    """ The profile specified by the user cannot be found """
    def __init__(self, build_worktree, profile_name):
        self.profile_name = profile_name
        self.build_worktree = build_worktree

    def __str__(self):
        qibuild_xml = self.build_worktree.qibuild_xml
        profiles = qibuild.profile.parse_profiles(qibuild_xml)
        return """ Could not find profile {name}.
Known profiles are: {profiles}
Please check your worktree configuration in:
{qibuild_xml} \
""".format(name=self.profile_name, qibuild_xml=qibuild_xml,
           profiles=', '.join(sorted(profiles.keys())))
