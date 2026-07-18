#!/bin/bash

#--------------------------------------------------------------------------------
# Python_Launch.sh
#--------------------------------------------------------------------------------

# Echo to stdout:
echo "Python_Launch.sh: $@"

start=$(date +%s)

python "$@"

end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"

# Success status (exit code 0)
:
