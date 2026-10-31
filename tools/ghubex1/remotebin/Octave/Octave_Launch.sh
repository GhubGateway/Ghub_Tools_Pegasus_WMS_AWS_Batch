#!/bin/bash

#--------------------------------------------------------------------------------
# Octave_Launch.sh
# Component of:
#     https://github.com/GhubGateway/Ghub_Pegasus_WMS_Tutorial_and_Templates and
#     https://theghub.org/tools/ghubex1
# Also see Ghub, https://theghub.org/about
#--------------------------------------------------------------------------------
set -e
start=$(date +%s)

# Echo to stdout:
echo "Octave_Launch.sh: $@"

octave --no-gui --silent "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

# Success status (exit code 0)
:
