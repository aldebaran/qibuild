#!/bin/sh
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2011-2018 SoftBank Robotics
##

PYTHONPATH=. python -m cProfile -stime $@


#how to get better profiling:
#python_profile.sh -o mysuperoutput.stats ../bin/qibuild
#python -mpstats mysuperoutput.stats
#sort time
#stats 10
