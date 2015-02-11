"""
timetableA2.py - optimizing timetabling with local search algorithms
K. Brett Mulligan
5 Feb 2015
CSU CS540
Dr. Adele Howe
"""

import search 
import time
import re
import random
import math
import sys
import os
import copy

VERBOSE_LOADING = False
VERBOSE_TESTING = True

subdir = './'
crsfile = "instance1.crs"
stufile = "instance1.stu"
solfile = "instance1.sol"

DEC_PRECISION = 5
PERCENT_DIGITS = 2
EOL = '\n'


class Student:

    def __init__(name):
        self.stu_id = name
        self.courses = ()

class Course:

    def __init__(name):
        self.crs_id = name
        self.students = ()
        self.enrolled = len(self.students)
    

def test_instance(crsfn, stufn):
    
    if VERBOSE_TESTING:
        print 'Testing...', crsfn, 'and', stufn, "@", time.asctime()

    read_crs_file(crsfn)
    read_stu_file(stufn)
        
    print ''

    return

    
def read_crs_file(filename):
    f = open(filename, 'r')
    if f == None:
        print "TT Error: read_crs_file could not open file:", filename 
    
        
    
    else:
        data = f.readline()
        print data
        data = data.split()
        
        room_cap = int(data[0])
        timeslots = int(data[1])
        
        print 'Room cap:', room_cap
        print 'Timeslots:', timeslots
        
        for line in f:
            print line
            
        print ''
        
        """
        line = line.strip()                                         # strip whitespace

        if len(line) > 1 and line[0] not in IGNORE:                 # ignore comment lines and lines of only 1 char, process everything else                    
            # print line

            if line[0] == 'p':                                      # first line, grab data
                data = line.split()
                self.num_variables = int(data[2])
                self.num_clauses = int(data[3])

            else:                                                   # clauses
                temp_clauses.append(self.transform_clause(line.split()))
        """
        
def read_stu_file(filename):
    f = open(filename, 'r')
    if f == None:
        print "TT Error: read_stu_file could not open file:", filename 
    
    else:
        for line in f:
            print line
            
        print ''



if __name__ == "__main__":
    
    test_instance(crsfile, stufile)

    print "Testing complete!"

    