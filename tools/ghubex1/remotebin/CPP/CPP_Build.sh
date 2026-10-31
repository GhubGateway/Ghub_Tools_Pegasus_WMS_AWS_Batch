#!/bin/bash

#--------------------------------------------------------------------------------
# CPP_Build.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------
set -e
start=$(date +%s)

# Echo to stdout:
echo "CPP_Build.sh: $@"

# gcc creates C++ executables to run on a platform corresponding to the platform on which they are generated.

gcc=$(which gcc)
echo 'gcc: '${gcc}

# -v: verbose
# -o: output file

${gcc} -lstdc++ -v ./$1 -o ./$2

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

# Success status (exit code 0)
:
