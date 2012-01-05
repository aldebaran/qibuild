##
## Sample submodule
##

project(QiSubModule)

# creates a submodule named 'mysubmodule'. It have 3 sources files and brings a dependencies on qt_core
qi_submodule_create(mysubmodule SRC mylib.cpp myprivateheader.hpp mypublicheader.hpp
                                DEPENDS qt_core)

# appends files related to boost to the submodule, this will occur only if
# WITH_BOOST is defined.
qi_submodule_add(mysubmodule SRC mylibboostfeature.cpp myprivateboostheader.hpp mypublicboostheader.hpp
                          DEPENDS boost
                          IF WITH_BOOST)

# this creates a binary that have a dependencies on Qt and boost (if WITH_BOOST is set)
# sources are taken from the submodule
qi_create_bin(mybin SUBMODULE mysubmodule)
