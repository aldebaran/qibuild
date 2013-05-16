cmake_minimum_required(VERSION 2.8)
project(translateme-qt)
find_package(qibuild)

qi_create_bin(translateme main.cpp)
qi_use_lib(translateme QT_QTCORE QT_QTGUI)
