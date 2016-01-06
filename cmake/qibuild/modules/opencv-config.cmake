## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#This is the old OpenCV please prefer opencv2_* packages
clean(OPENCV)

fpath(OPENCV cv.h PATH_SUFFIXES opencv)
fpath(OPENCV opencv/cv.h)

flib(OPENCV OPTIMIZED NAMES cv      cv200      )
flib(OPENCV DEBUG     NAMES cv      cv200d     )
flib(OPENCV OPTIMIZED NAMES cvaux   cvaux200   )
flib(OPENCV DEBUG     NAMES cvaux   cvaux200d  )
flib(OPENCV OPTIMIZED NAMES cxcore  cxcore200  )
flib(OPENCV DEBUG     NAMES cxcore  cxcore200d )
flib(OPENCV OPTIMIZED NAMES highgui highgui200 )
flib(OPENCV DEBUG     NAMES highgui highgui200d)
flib(OPENCV OPTIMIZED NAMES ml      ml200d     )
flib(OPENCV DEBUG     NAMES ml      ml200      )

export_lib(OPENCV)
