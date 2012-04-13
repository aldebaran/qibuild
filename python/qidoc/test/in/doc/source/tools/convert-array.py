#!/usr/bin/env python2
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2011 Aldebaran Robotics
##

# .. important::
#   TODO: REFORMAT THIS TABLE
tagada = """\
  | Joint name  | Motion  | Range (degrees)  | Range (radian) |
  | RShoulderPitch  | Right shoulder joint front and back (Y)  | -119.5 to 119.5  | -2.0857 to 2.0857 |
  | RShoulderRoll  | Right shoulder joint right and left (Z)  | -76 to 18  | -1.3265 to 0.3142 |
  | RElbowYaw  | Right shoulder joint twist (X)  | -119.5 to 119.5  | -2.0857 to 2.0857 |
  | RElbowRoll  | Right elbow joint (Z)  | 2 to 88.5  | 0.0349 to 1.5446 |
  | RWristYaw  | Right wrist joint (X)  | -104.5 to 104.5  | -1.8238 to 1.8238 |
  | RHand  | Right hand  | Open And Close |
"""


tagada = """

Right Arm joints
----------------

.. image:: medias/hardware_rarmjoint_3.3.png

.. important::
  TODO: REFORMAT THIS TABLE
  | Joint name  | Motion  | Range (degrees)  | Range (radian) |
  | RShoulderPitch  | Right shoulder joint front and back (Y)  | -119.5 to 119.5  | -2.0857 to 2.0857 |
  | RShoulderRoll  | Right shoulder joint right and left (Z)  | -76 to 18  | -1.3265 to 0.3142 |
  | RElbowYaw  | Right shoulder joint twist (X)  | -119.5 to 119.5  | -2.0857 to 2.0857 |
  | RElbowRoll  | Right elbow joint (Z)  | 2 to 88.5  | 0.0349 to 1.5446 |
  | RWristYaw  | Right wrist joint (X)  | -104.5 to 104.5  | -1.8238 to 1.8238 |
  | RHand  | Right hand  | Open And Close |

Access value by using :ref:`ALMemory <None>` key name

Command(radian):

.. code-block:: guess

  Device/SubDeviceList/RShoulderPitch/Position/Actuator/Value
  Device/SubDeviceList/RShoulderRoll/Position/Actuator/Value
  Device/SubDeviceList/RElbowYaw/Position/Actuator/Value
  Device/SubDeviceList/RWristYaw/Position/Actuator/Value
  Device/SubDeviceList/RHand/Position/Actuator/Value
"""

def split_and_lean(line):
    line = line.strip()
    if len(line) < 2:
        print "line too short:", line
        raise "oups"
    if line[0] == "|":
        line = line[1:]
    if line[-1] == "|":
        line = line[:-1]
    words = line.split("|")
    result = list()
    for w in words:
        result.append(w.strip())
    return result

def print_sep(colsz, sep):
    ret = "+" + sep
    for i in range(len(colsz)):
        ret += sep * colsz[i]
        if len(colsz) - 1 == i:
            ret += sep + "+"
        else:
            ret += sep + "+" + sep
    return ret

def print_spaced(word, colsz):
    ret = "| "
    for i in range(len(word)):
        ret += word[i] + " " * (colsz[i] - len(word[i]))
        ret += " | "
    return ret

def fill_with_empty(row, sz):
    for i in range(len(row), sz):
        row.append("")
    return row

def branle(lines):
    """
    """
    headers = split_and_lean(lines[0])
    maxcol = len(headers)
    result = list()

    print "col size:", maxcol

    rows = list()
    for i in range(1, len(lines)):
        row = split_and_lean(lines[i])
        rows.append(row)
        if len(row) > maxcol:
            maxcol = len(row)

    fill_with_empty(headers, maxcol)
    for r in rows:
        r = fill_with_empty(r, maxcol)


    colslen = [ 0 for x in range(maxcol) ]
    for col in range(maxcol):
        cur = len(headers[col])
        for row in rows:
            if len(row[col]) > cur:
                cur = len(row[col])
        colslen[col] = cur

    print "cols", ",".join([ str(x) for x in colslen])
    result.append(print_sep(colslen, "-"))
    result.append(print_spaced(headers, colslen))
    result.append(print_sep(colslen, "="))

    for r in rows:
        result.append(print_spaced(r, colslen))
        result.append(print_sep(colslen, "-"))
    return result

def find_and_replace(lines):
    result = list()
    gettab = False
    tab = list()
    for l in lines:
        if l.startswith("  |"):
            tab.append(l)
            gettab = True
            continue
        if gettab:
            for t in tab:
                print "t:", t
            result.extend(branle(tab))
            tab = list()
            gettab = False
        result.append(l.rstrip())
    return result

import sys
if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
    ret = find_and_replace(lines)

    ret = find_and_replace(lines)
    print "\n".join(ret)

    with open(sys.argv[1], "w") as f:
        for l in ret:
            f.write(l + "\n")

