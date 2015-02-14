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


DEC_PRECISION = 5
PERCENT_DIGITS = 2
EOL = '\n'


subdir = './'
crsfile = "instance1.crs"                   # CHANGE BEFORE TURN-IN
stufile = "instance1.stu"
solfile = "instance1.sol"

TIMESLOTS_PER_DAY = 5


class ExamWeek:

    def __init__(self, rmcap, num_exams):
        self.room_cap = rmcap
        self.timeslots = num_exams

class Student:

    def __init__(self, name):
        self.stu_id = name
        self.courses = ()
        
    def add_course(crs):
        self.courses = tuple(list(self.courses).append(crs))

class Course:

    def __init__(self, name, enrollment):
        self.crs_id = name
        self.students = ()
        self.enrolled = enrollment
        self.timeslot = 0

    
def read_crs_file(filename):
    courses = []
    
    f = open(filename, 'r')
    if f == None:
        print "TT Error: read_crs_file could not open file:", filename 
    else:
        data = f.readline()
        print data
        data = data.split()
        
        room_cap = int(data[0])
        timeslots = int(data[1])
        
        print 'Room Capacity:', room_cap
        print 'Timeslots:', timeslots
        
        print ''
        
        for line in f:
            print line
            courses.append(Course(line.split('\t')[0], line.split('\t')[1]))
            
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

def print_solution(sol):
    printable = ''
    
    printable = printable + '7\t133.75'

    for crs in sol:
        exam_day = crs.timeslot // TIMESLOTS_PER_DAY
        exam_timeslot = crs.timeslot % TIMESLOTS_PER_DAY
        printable += '\n' + crs.crs_id + '\t' + str(exam_day) + '\t' + str(exam_timeslot)
    
    return printable
        
def test_instance(crsfn, stufn):
    
    if VERBOSE_TESTING:
        print 'Testing...', crsfn, 'and', stufn, "@", time.asctime()

    read_crs_file(crsfn)
    read_stu_file(stufn)
    
    sol = [Course('001', 10) for x in range(0,10)]
    print print_solution(sol)
        
    print ''

    return

if __name__ == "__main__":
    
    test_instance(crsfile, stufile)

    print "Testing complete!"

    