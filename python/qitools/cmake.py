""" Some useful functions to communicate
information between the Python and the CMake
worlds

"""
import os

import qitools


def get_cmake_value(name, build_dir=None):
    """Get a the value of a CMake variable.
    (Using a cache or not)

    """
    cache = None
    if build_dir:
        cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cache):
            mess = "Could not find CMakeCache in the build dir: %s" % build_dir
            raise Exception(mess)


    # Create a temporary script:
    out = None
    with qitools.sh.TempDir() as temp_dir:
        temp_script = os.path.join(temp_dir, "get-value.cmake")
        with open(temp_script, "w") as fp:
            to_write = 'message(STATUS "{name} ${{{name}}}")\n'
            to_write = to_write.format(name=name)
            fp.write(to_write)
        cmake_args = ["-P", temp_script]
        if cache:
            cmake_args.append(build_dir)
        cmd = ["cmake"]
        cmd.extend(cmake_args)
        out = qitools.command.call_output(cmd)[0]
    res = out.split()[-1]
    return res


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        name, build_dir = sys.argv[1:]
    else:
        name = sys.argv[1]
        build_dir = None
    res = get_cmake_value(name, build_dir)
    print res








