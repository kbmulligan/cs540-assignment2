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

ARGS = 5

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
        
    def display(self, courses):
        data = '--- Exam Week ---\n' + 'Room capacity: ' + str(self.room_cap) + '\nTotal Exams: ' + str(self.timeslots) + '\n'
        
        for x in range(1, self.timeslots + 1):
            data += '\n' + str(x)                        # TODO: plus any courses in this timeslot
            data += str(get_course_with_timeslot(courses, x))
        data += '\n'
        return data

class Student:

    def __init__(self, name):
        self.stu_id = name
        self.courses = []
        
    def add_course(self, crs):
        self.courses.append(crs)

class Course:

    def __init__(self, name, enrollment):
        self.crs_id = name
        self.students = ()
        self.enrolled = enrollment
        self.timeslot = 0

def get_course_with_timeslot(courses, slot):
    return [course.crs_id for course in courses if course.timeslot == slot]

def assign_random_timeslot(courses, maximum):
    for course in courses:
        course.timeslot = random.randint(1,maximum)
    
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
        
    return courses, room_cap, timeslots

def total_timeslots():
    return 7
    
def total_student_cost():
    return 133.75
        
def read_stu_file(filename):
    students = []
    
    f = open(filename, 'r')
    if f == None:
        print "TT Error: read_stu_file could not open file:", filename 
    
    else:
        stud_count = 1
        for line in f:
            print line
            new_student = Student(stud_count)
            courses = line.split()
            for course in courses:
                new_student.add_course(course)
            students.append(new_student)
            stud_count += 1
            
        print ''
        
    return students

def print_solution(sol):
    printable = ''
    
    printable = printable + str(total_timeslots()) + '\t' + str(total_student_cost())

    for crs in sol:
        exam_day = (crs.timeslot // TIMESLOTS_PER_DAY) + 1
        exam_timeslot = (crs.timeslot % TIMESLOTS_PER_DAY)
        if (exam_timeslot == 0):
            exam_timeslot = TIMESLOTS_PER_DAY
            exam_day -= 1
        printable += '\n' + crs.crs_id + '\t' + str(exam_day) + '\t' + str(exam_timeslot) + '\t' + str(crs.timeslot)
    
    return printable
        
def test_instance(crsfn, stufn):
    
    if VERBOSE_TESTING:
        print 'Testing...', crsfn, 'and', stufn, "@", time.asctime()

    courses, room_cap, num_exams = read_crs_file(crsfn)
    students = read_stu_file(stufn)
    
    assign_random_timeslot(courses, num_exams)
    
    ### Check constraints
    
    
    print ExamWeek(room_cap, num_exams).display(courses)
    print print_solution(courses)
        
    print ''

    return

if __name__ == "__main__":

    if len(sys.argv) != ARGS:
        print 'Usage: ', sys.argv[0], '<coursefile> <studentfile> <solutionfile> <objectivefunction (0 or 1)>'
    else:
        crsfile = sys.argv[1]
        stufile = sys.argv[2]
        solfile = sys.argv[3]
        obj_function = sys.argv[4]
        test_instance(crsfile, stufile)

    print "Testing complete!"

    