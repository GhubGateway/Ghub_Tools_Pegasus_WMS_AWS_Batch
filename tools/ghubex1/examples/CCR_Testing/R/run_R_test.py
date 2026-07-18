#######################################################
# For module testing on CCR.
# Run as python run_R_test.py username
#
# Requires input file f.a,
# bin/R/receive_lunch_items.r,
# bin/R/consume_lunch_items.r and
# remotebin/R/R_Launch.sh (mode 755) files.
#######################################################

import sys
import os
import subprocess

def main(argv):

    if (len(argv) == 2):
    
        scriptname = argv[0]
        print ('scriptname: %s' %scriptname)
        username = str(argv[1])
        print ('username: %s' %username)

        if os.path.exists('f.b'):
            os.remove ('f.b')
        if os.path.exists('f.c'):
            os.remove ('f.c')
        
        # Launch
        
        exitStatus = subprocess.call(['./R_Launch.sh','receive_lunch_items.r',username])
        print ('receive_lunch_items.sh exitStatus: %d' %exitStatus)
        
        exitStatus = subprocess.call(['./R_Launch.sh','consume_lunch_items.r'])
        print ('consume_lunch_items.sh exitStatus: %d' %exitStatus)
        
    else:
    
        print ('Wrong number of arguments')
        
#######################################################

if __name__ == "__main__":

    main(sys.argv)
