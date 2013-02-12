## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(qi_create_trad domain_name po_dir)
  qi_stage_dir(${po_dir})
  set(_locale_dir ${po_dir}/share/locale)
  file(MAKE_DIRECTORY ${_locale_dir})
  qi_install_data(${po_dir}/share/locale KEEP_RELATIVE_PATHS)
endfunction()
