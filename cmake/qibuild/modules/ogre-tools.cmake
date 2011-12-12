## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#! qiBuild ogre tools
# ===================
#
# This module contains useful functions helping writing
# code that use ogre libraries


#! Generate suitable configuration files, resources.cfg and plugins.cfg
#  and their install rules.
#
#  This allows you to configure ogre from CMake and plain text files
#  instead of doing it with the C++ Ogre API.
#
#
# \group APPLICATION_NAME Name of the application.
# \group SRC_RESOURCES_PATHS The list of absoluted paths to the directories
#                           where to find the meshes,
#                           the .material, and so on.
# \group INSTALLED_RESOURCES_PATHS The same list, but relative to the
#                                  install directory
# \param RENDER_PLUGIN   The name of the Render plugins, for instance
#                        RenderSystem_GL.
#
# Calling this function will make sure that:
#   - resources.cfg is available next to the executable,
#     and contains correct path to resources
#   - plugins.cfg is build correctly for windows (debug / release),
#     mac, and linux.
#     on windows, a plugins_d.cfg is created, containing path to
#     ${_render_plugin}_d.
#   - those files are installed at the correct place
# \example:ogre
function(configure_ogre)
  # FIXME: install rules
  # FIXME: put configuration files in etc/ rather that in bin/

  cmake_parse_arguments(ARG "" "APPLICATION_NAME;RENDER_PLUGIN"
    "SRC_RESOURCES_PATHS;INSTALLED_RESOURCES_PATHS" ${ARGN})

  # Set CMAKE_FIND_LIBRARY_PREFIXES so that RenderSystem_GL.so is found
  # (there is not libRendeSystem_GL.so)
  set(_backup ${CMAKE_FIND_LIBRARY_PREFIXES})
  set(CMAKE_FIND_LIBRARY_PREFIXES "")
  find_library(_ogre_plugin NAMES ${ARG_RENDER_PLUGIN}
                            PATH_SUFFIXES "OGRE")
  set(CMAKE_FIND_LIBRARY_PREFIXES ${_backup})

  if(NOT _ogre_plugin)
    qi_error("Could not find library for render plugin: '${ARG_RENDER_PLUGIN}'")
  endif()

  get_filename_component(_ogre_plugins_folder ${_ogre_plugin} PATH)

  set(_plugins_cfg "${QI_SDK_DIR}/${QI_SDK_CONF}/${ARG_APPLICATION_NAME}/ogre/plugins.cfg")
  file(WRITE  "${_plugins_cfg}" "# Defines Ogre plugins to load\n")
  file(APPEND "${_plugins_cfg}" "PluginFolder=${_ogre_plugins_folder}\n")
  file(APPEND "${_plugins_cfg}" "Plugin=${ARG_RENDER_PLUGIN}\n")

  if(WIN32)
    set(_plugins_d_cfg "${QI_SDK_DIR}/${QI_SDK_CONF}/${ARG_APPLICATION_NAME}/ogre/plugins_d.cfg")
    file(WRITE  "${_plugins_d_cfg}" "# Defines Ogre plugins to load\n")
    file(APPEND "${_plugins_d_cfg}" "PluginFolder=${_ogre_plugins_folder}\n")
    file(APPEND "${_plugins_d_cfg}" "Plugin=${ARG_RENDER_PLUGIN}_d\n")
  endif()

  set(_resources_cfg "${QI_SDK_DIR}/${QI_SDK_CONF}/${ARG_APPLICATION_NAME}/ogre/resources.cfg")
  file(WRITE  "${_resources_cfg}" "# Defines where to find Ogre resources\n")
  file(APPEND "${_resources_cfg}" "[General]\n")
  foreach(_resource_path ${ARG_SRC_RESOURCES_PATHS})
    file(APPEND "${_resources_cfg}" "FileSystem=${_resource_path}\n")
  endforeach()

  # Create files to be installed:
  # A custom plugins.cfg with no PluginFolder section
  set(_inst_plugins "${CMAKE_CURRENT_BINARY_DIR}/plugins.cfg")
  file(WRITE  "${_inst_plugins}" "#Defines ogre plugins to load\n")
  file(APPEND "${_inst_plugins}" "Plugin=${ARG_RENDER_PLUGIN}\n")
  file(APPEND "${_inst_plugins}" "PluginFolder=@sdk@/lib/OGRE\n")

  # A custon resource.cfg with the installed PATH
  set(_inst_resources "${CMAKE_CURRENT_BINARY_DIR}/resources.cfg")

  file(WRITE  "${_inst_resources}" "# Defines where to find Ogre resources\n")
  file(APPEND "${_inst_resources}" "[General]\n")
  foreach(_resource_path ${ARG_INSTALLED_RESOURCES_PATHS})
    file(APPEND "${_inst_resources}" "FileSystem=@sdk@/${_resource_path}\n")
  endforeach()

  qi_install_conf(${_inst_resources} SUBFOLDER ${ARG_APPLICATION_NAME}/ogre)
  qi_install_conf(${_inst_plugins}   SUBFOLDER ${ARG_APPLICATION_NAME}/ogre)


endfunction()
