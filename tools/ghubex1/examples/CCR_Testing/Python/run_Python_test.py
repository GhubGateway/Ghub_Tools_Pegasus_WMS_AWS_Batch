#######################################################
# For module testing on CCR.
# Run as python run_Python_test.py username
#
# Requires input file f.a,
# bin/Python/receive_lunch_items.py,
# bin/Python/consume_lunch_items.py and
# remotebin/Python/Python_Launch.sh (mode 755) files.
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
        
        exitStatus = subprocess.call(['./Python_Launch.sh','receive_lunch_items.py',username])
        print ('receive_lunch_items.py exitStatus: %d' %exitStatus)
        
        exitStatus = subprocess.call(['./Python_Launch.sh','consume_lunch_items.py'])
        print ('consume_lunch_items.py exitStatus: %d' %exitStatus)
        
    else:
    
        print ('Wrong number of arguments')
        
#######################################################

if __name__ == "__main__":

    main(sys.argv)
