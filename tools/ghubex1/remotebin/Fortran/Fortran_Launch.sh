#!/bin/bash

#--------------------------------------------------------------------------------
# Fortran_Launch.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------
set -e
start=$(date +%s)

# Echo to stdout:
echo "Fortran_Launch.sh: $@"

# First word of the command line = the program to run
prog="${1%% *}"
prog="${prog#./}"
echo "prog: ":$prog

# If it's a file staged into the job's working dir, make it executable
if [ -f "./$prog" ]; then
    chmod +x "./$prog"
fi

eval "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

# Success status (exit code 0)
:
