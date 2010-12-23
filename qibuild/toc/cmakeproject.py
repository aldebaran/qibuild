import os
import glob
import logging

from buildtool                 import toolchain
from buildtool.config          import CMAKE_GENERATOR, ON_WIN, SDK_ARCH
from buildtool.cmake           import configure
from buildtool.build           import build_unix, build_vc, build_nmake
from buildtool.install         import install_unix, install_vc, install_components
from buildtool.runtests        import run_tests

from qibuild.toc.exception   import TocException
from qibuild.toc.buildconfig import BuildConfig, get_arch
from qibuild.toc.path        import to_posix_path


LOGGER = logging.getLogger("cmakeproject")

class CMakeProject:
    """A class that represent a CMake based project.

    Used as an attribute of the Project class
    """
    def __init__(self, project):
        self.toc         = project.toc
        self.project     = project
        self.cross       = False
        self.release     = False
        self.build_config = BuildConfig()
        self.build_dir = None

    def get_build_dir(self):
        """Get the build directory of the project.

        You can use a bunch of options here, and we will also use
        the toc configuration.

        """
        build_dir_name = self.build_config.get_build_folder_name()
        src_dir = self.project.get_src_dir()
        LOGGER.debug("get_build_dir: %s", build_dir_name)
        return os.path.join(src_dir, build_dir_name)

    def get_extra_toolchain_text(self, arch=None):
        """ Look in .toc/ find
            a toolchain.cmake
            a toolchain-arch.cmake
        """
        ret = ""
        arch = get_arch(self.build_config.cross)
        tcpath = self.toc.path.get("toc", "toolchain.cmake")
        if os.path.exists(tcpath):
            LOGGER.info("Extra cmake toolchain file: %s", tcpath)
            ret += "include(\"%s\")\n" % to_posix_path(tcpath)
        tcpath = self.toc.path.get("toc", "toolchain-%s.cmake" % (arch))
        if os.path.exists(tcpath):
            LOGGER.info("Extra cmake toolchain file: %s", tcpath)
            ret += "include(\"%s\")\n" % to_posix_path(tcpath)
        return ret


    def configure(self, flags=None, toolchain_file=None, generator=None):
        """ Call cmake with correct options
        if toolchain_file is None a t001chain file is generated in the cmake binary directory.
        if toolchain_file is "", then CMAKE_TOOLCHAIN_FILE is not specified.
        """
        if generator is None and CMAKE_GENERATOR is None:
            raise TocException("Could not guess CMAKE_GENERATOR. Check configuration")
        if generator is None:
            generator = CMAKE_GENERATOR
        src_dir = self.project.get_src_dir()
        if not os.path.exists(src_dir):
            raise TocException("source dir: %s does not exist, aborting" % \
                src_dir)
        # There are still a few projects not managed by cmake ...
        if not os.path.exists(os.path.join(src_dir, "CMakeLists.txt")):
            LOGGER.info("Not calling cmake for %s", os.path.basename(src_dir))
            return

        # Create build dir if it does not exist:
        build_dir = self.get_build_dir()
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        # Set generator (mandatory on windows, because cmake does not
        # autodetect visual studio compilers very well)
        cmake_args = ["-G", generator]

        if flags:
            # Make a copy so that we do not modify
            # the list used by the called
            cmake_flags = flags[:]
        else:
            cmake_flags = list()
        cmake_flags.extend(self.build_config.flags)

        cross = self.build_config.cross
        ctc_path = self.build_config.ctc_path
        if cross:
            if not ctc_path:
                ctc_path = self.toc.config.get("general.toc.ctc", "")
                if not ctc_path:
                    mess  = "Using --cross without --ctc-path\n"
                    mess += "And could not find general.toc.ctc setting"
                    raise TocException(mess)

        if toolchain_file is None:
            extra_toolchain_text = self.get_extra_toolchain_text()
            (toolchain_dir, dep_sdk_dirs) = self.get_sdk_dirs()
            toolchain_file = toolchain.generate_toolchain_file(build_dir,
                toolchain_dir,
                dep_sdk_dirs,
                cross=cross, ctc_path=ctc_path, extra=extra_toolchain_text)
        if toolchain_file != "":
            cmake_flags.append("CMAKE_TOOLCHAIN_FILE=" + toolchain_file)

        cmake_args.extend(["-D" + x for x in cmake_flags])

        configure(src_dir, build_dir, cmake_args)


    def build(self, num_jobs=1, nmake=False, target=None):
        """Build the project"""
        build_dir = self.get_build_dir()
        release = self.build_config.release
        LOGGER.debug("[%s]: building in %s", self.project.name, build_dir)
        if ON_WIN and not nmake:
            sln_files = glob.glob(build_dir + "/*.sln")
            if len(sln_files) == 0:
                LOGGER.debug("Not calling msbuild for %s", os.path.basename(build_dir))
                return

            if len(sln_files) != 1:
                err_message = "Found several sln files: "
                err_message += ", ".join(sln_files)
                raise TocException(err_message)

            sln_file = sln_files[0]
            build_vc(sln_file, release=release, target=target)
        else:
            if not os.path.exists(os.path.join(build_dir, "Makefile")):
                LOGGER.debug("Not calling make for %s", os.path.basename(build_dir))
                return
            if ON_WIN:
                build_nmake(build_dir, target=target)
            else:
                build_unix(build_dir, num_jobs=num_jobs, target=target)

    def install(self, destdir, components=None, strip=False):
        """Install the project.

        If components is not none, it must be a list
        of components you want to install

        If strip is True, libraries will get stripped.
        Does not work on windows and mac, though.

        Note: for now, all our cmake projects will be configured with
        insall_prefix = "/", so foo.so will be installed on destdir/lib/libfoo.so,
        but we may use a different install prefix one day (say /usr/local), and
        libfoo.so would then be found in destdir/usr/local/lib/libfoo.so

        Of course, you can use toc cmake --install-prefix=/usr/local foo
        if you want.
        """
        no_install = self.project.config.get("no_install", False)
        if no_install:
            LOGGER.info("[%s] not to be installed, skipping", self.project.name)
            return

        build_dir = self.get_build_dir()
        release = self.build_config.release

        if not os.path.exists(build_dir):
            mess = "[%s] install: could not find build dir. Looked in %s" % \
                (self.project.name, build_dir)
            raise TocException(mess)
        if components is not None:
            install_components(build_dir, destdir, components,
                strip=strip,
                release=release)
        else:
            if ON_WIN:
                install_vc(build_dir, destdir, release=release)
            else:
                install_unix(build_dir, destdir, strip=strip)


    def run_tests(self):
        """Run tests """
        build_dir = self.get_build_dir()
        if not os.path.exists(build_dir):
            mess = "[%s] run_tests: could not find build dir. Looked in %s" % \
                (self.project.name, build_dir)
            raise TocException(mess)
        run_tests(self.project.get_src_dir(), build_dir)


    def get_sdk_dirs(self):
        """
        Transform the list of dependencies into a list of sdk dirs

        Returns (toolchain_dir, [sdk_dirs])

        """
        # 1. Look for t001chain dir:
        toolchain_dir = self.project.toc.get_project("toolchain").get_src_dir()
        if not os.path.exists(toolchain_dir):
            mess = "Could not find toolchain source dir!"
            raise TocException(mess)

        cross = self.build_config.cross
        deps_projs = self.project.toc.resolve_deps([self.project], get_arch(cross))

        # Remove self from the list of dependencies
        # unless self was explicitly specified in configuration
        # (otherwise we got a spurious warning the first time)
        config_deps_names  = self.project.get_depends(get_arch(cross))
        if self.project.name not in config_deps_names:
            deps_projs.remove(self.project)

        # 2. Start to fill sdk_dirs
        dep_sdk_dirs = []

        # Add toolchain-pc only if we are not cross compiling
        # TODO:
        # 1. split t001chain and toolchain-pc.
        # 2. simply add ctc/staging/usr as a binary sdk when cross compiling
        if not self.cross:
            toolchain_sdk_dir = os.path.join(toolchain_dir, "toolchain-pc")
            dep_sdk_dirs = [toolchain_sdk_dir]

        sdk_bin_proj_conf = self.toc.config.get("general.toc.bin_sdk_projects" , "")
        sdk_bin_proj_names = sdk_bin_proj_conf.split()
        sdk_bin_projs = [self.toc.get_project(n) for n in sdk_bin_proj_names]

        dep_src_projs = [p for p in deps_projs if p not in sdk_bin_projs]
        #   add dep_src/build/sdk if dep is not a bin sdk,
        #       dep_src otherwise
        for dep_proj in dep_src_projs:
            dep_src_dir = dep_proj.get_src_dir()
            if not os.path.exists(dep_src_dir):
                mess = "Could not find source dir for dependency: %s\n" % \
                    dep_proj.name
                mess += "Try calling toc load"
                dep_proj.name = "Pierre"
                raise TocException(mess)
            if dep_proj.config.get("is_bin_sdk", False):
                dep_sdk_dir = dep_src_dir
            else:
                dep_build_dir = dep_proj.cmake.get_build_dir()
                dep_sdk_dir = os.path.join(dep_build_dir, "sdk")

                if not os.path.exists(dep_sdk_dir):
                #TODO: remove doc from the build depends of choregraphe,
                # and throw a plain old exception here
                    mess = "Could not find build/sdk dir "
                    mess += "for dependency: %s\n" %  dep_proj.name
                    mess += "calling :"
                    mess += " toc cmake " + dep_proj.name
                    mess += " toc build " + dep_proj.name
                    LOGGER.warning(mess)

            dep_sdk_dirs.append(dep_sdk_dir)

        for dep_proj in sdk_bin_projs:
            dep_sdk_dirs.append(dep_proj.get_sdk_dir())

        LOGGER.debug("SDK_DIRS: %s" , ",".join(dep_sdk_dirs))
        return (toolchain_dir, dep_sdk_dirs)
