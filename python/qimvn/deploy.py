## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys

def deploy(groupId, version, artifactId, package, url, packaging="jar"):
    """ Call maven to deploy given file
    """
    return qisys.command.call(["mvn", "deploy:deploy-file" ,"-nsu", "-U",
                        "-Dpackaging="+packaging, "-DgroupId="+groupId,
                        "-Dversion="+version, "-DartifactId="+artifactId,
                        "-Dfile="+package, "-Durl="+url])
