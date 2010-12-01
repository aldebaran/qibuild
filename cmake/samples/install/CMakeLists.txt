

#NONE because we dont want to check for a valid compiler
project(QiInstallSample NONE)

#include(qibuild)

#install foo.h    in include/qiinstallsample/foo.h
#install bar/*.h  in include/qiinstallsample/*.h
#install foobar/* in include/qiinstallsample/foobar/

qi_install_header(qiinstallsample foo.h bar/*.h foobar)



#to install to a subfolder you can do:
qi_install_header(qiinstallsample/subbar subbar/*.h)
