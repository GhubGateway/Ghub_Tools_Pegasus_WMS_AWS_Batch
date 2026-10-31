#!/bin/bash

#--------------------------------------------------------------------------------
# Fortran_Build.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Called from: a SLURM script
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------
set -e
start=$(date +%s)

# Echo to stdout:
echo "Fortran_Build.sh: $@"

# gfortran creates Fortran executables to run on a platform corresponding to the platform on which they are generated.

gfortran=$(which gfortran)
echo 'gfortran: '${gfortran}

# -v: verbose
# -o: output file

${gfortran} -v ./$1 -o ./$2

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

# Success status (exit code 0)
:
