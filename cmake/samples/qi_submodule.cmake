##
## Sample submodule
##

project(QiSubModule)

# create a submodule with your lib, with one publicheader and a Qt dependencies
qi_submodule_create(mysubmodule SRC mylib.cpp myprivateheader.hpp
                                PUBLIC_HEADER mypublicheader.hpp
                                DEPENDENCIES Qt)

# append files related to boost to the submodule, this will occur only if
# WITH_BOOST is defined.
qi_submodule_add(mysubmodule SRC mylibboostfeature.cpp myprivateboostheader.hpp
                          PUBLIC_HEADER mypublicboostheader.hpp
                          DEPENDENCIES boost
                          IF WITH_BOOST)

# this create a binary that have a dependencies on Qt and boost (if WITH_BOOST is set)
# source and public_header are taken from the submodule
qi_create_bin(mybin SUBMODULE mysubmodule)
