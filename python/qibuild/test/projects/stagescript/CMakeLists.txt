cmake_minimum_required(VERSION 2.8)
project(test_stage_lib)

find_package(qibuild)
include_directories(".")


qi_create_lib(foo SHARED SRC src/foo.c)
qi_stage_lib(foo)

qi_create_lib(bar SHARED SRC src/bar.c DEPENDS FOO)
qi_stage_lib(bar)

qi_create_lib(worlduser SHARED SRC src/worlduser.cpp DEPENDS WORLD)
qi_stage_lib(worlduser)

qi_stage_script(src/nodep)
qi_stage_script(src/check_qipath TRAMPOLINE PYTHON DEPENDS FOO)
qi_stage_script(src/dlopenfoo TRAMPOLINE PYTHON DEPENDS FOO)
qi_stage_script(src/dlopenbar TRAMPOLINE PYTHON DEPENDS FOO BAR)
qi_stage_script(src/dlopenworlduser TRAMPOLINE PYTHON DEPENDS WORLDUSER)

qi_install_program(src/shlib.py)
qi_install_program(src/nodep)
qi_install_program(src/check_qipath) #will not work
qi_install_program(src/dlopenfoo)
qi_install_program(src/dlopenbar)
qi_install_program(src/dlopenworlduser)


add_custom_target(run_nodep ALL COMMAND ${python} ${NODEP_EXECUTABLE})
add_custom_target(run_dlopenworlduser ALL COMMAND ${python} ${DLOPENWORLDUSER_EXECUTABLE})
