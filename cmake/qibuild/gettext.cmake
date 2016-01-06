## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Translation support
# ====================

#! Create install rules for dictionary
#
# Example of use: ::
#
#   qi_create_lib(my_application SHARED SRC main.cpp)
#   qi_create_trad(my_application "po")
#
# \arg:app_name Name of the application you want to translate
# \arg:po_dir Directory where you have the POTFILES.in and
#             where files will be generated
function(qi_create_trad app_name po_dir)
  qi_stage_dir(${po_dir})
  set(_locale_dir ${po_dir}/share/locale)
  file(MAKE_DIRECTORY ${_locale_dir})
  qi_install_data(${po_dir}/share/locale KEEP_RELATIVE_PATHS)
endfunction()
