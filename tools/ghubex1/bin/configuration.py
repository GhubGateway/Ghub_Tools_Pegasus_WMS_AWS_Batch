#----------------------------------------------------------------------------------------------------------------------
# Configuration parameters
#----------------------------------------------------------------------------------------------------------------------

TEMPLATE_LIST = ['Bash', 'C', 'CPP', 'Fortran', 'Octave', 'Python', 'R']

# Following lists are ordered by the TEMPLATE_LIST order.

# Scripts for the Bash, Octave, Python, and R templates, and source code and binary executables for the C, CPP and Fortran templates, are stored in the tool's bin directory.
NUM_LISTS = 2
SRC_TYPE_LIST = ['Script', 'Source Code', 'Source Code', 'Source Code', 'Script', 'Script', 'Script']
SRC_LISTS = [['receive_lunch_items.sh', 'receive_lunch_items.c', 'receive_lunch_items.cpp', 'receive_lunch_items.f90', 'receive_lunch_items.m', 'receive_lunch_items.py', 'receive_lunch_items.r'],
    ['consume_lunch_items.sh', 'consume_lunch_items.c', 'consume_lunch_items.cpp', 'consume_lunch_items.f90', 'consume_lunch_items.m', 'consume_lunch_items.py', 'consume_lunch_items.r']]
BIN_LISTS = [[None, 'receive_lunch_items', 'receive_lunch_items', 'receive_lunch_items', None, None, None],
    [None, 'consume_lunch_items', 'consume_lunch_items', 'consume_lunch_items', None, None, None]]

