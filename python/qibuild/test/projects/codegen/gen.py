import sys
import shutil

input = sys.argv[1]
output = sys.argv[2]

shutil.copy(input, output)

if len(sys.argv) > 3:
    sys.exit("gen.py failed")
