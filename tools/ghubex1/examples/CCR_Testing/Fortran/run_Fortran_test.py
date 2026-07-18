#######################################################
# For module testing on CCR.
# Run as python run_Fortran_test.py username
#
# Requires input file f.a,
# bin/Fortran/receive_lunch_items.f90,
# bin/Fortran/consume_lunch_items.f90,
# remotebin/Fortran/Fortran_Build.sh (mode 755) and
# remotebin/Fortran/Fortran_Launch.sh (mode 755) files.
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
            
        # Build
        
        exitStatus = subprocess.call(['./Fortran_Build.sh'])
        print ('Build exitStatus: %d' %exitStatus)
        
        # Launch
        
        exitStatus = subprocess.call(['./Fortran_Launch.sh','./receive_lunch_items',username])
        print ('receive_lunch_items exitStatus: %d' %exitStatus)
        
        exitStatus = subprocess.call(['./Fortran_Launch.sh','./consume_lunch_items'])
        print ('consume_lunch_items exitStatus: %d' %exitStatus)
        
    else:
    
        print ('Wrong number of arguments')
        
#######################################################

if __name__ == "__main__":

    main(sys.argv)
