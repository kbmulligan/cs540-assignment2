"""
timetableA2.py - optimizing timetabling with local search algorithms
K. Brett Mulligan
5 Feb 2015
CSU CS540
Dr. Adele Howe
"""

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
crsfile = "instance1.crs"
stufile = "instance1.stu"
solfile = "instance1.sol"

TIMESLOTS_PER_DAY = 5

CAP_MULTIPLIER = 10


class ExamWeek:

    def __init__(self, rmcap, num_exams):
        self.room_cap = rmcap
        self.timeslots = num_exams
        
    def display(self, courses):
        data = '--- Exam Week ---\n' + 'Room capacity: ' + str(self.room_cap) + '\nTotal Exams: ' + str(self.timeslots) + '\n'
        
        for x in range(1, self.timeslots + 1):
            data += '\n' + str(x) + ': '
            data += str(get_courses_with_timeslot(courses, x))
        data += '\n'
        return data

class Student:

    def __init__(self, name):
        self.stu_id = name
        self.courses = []
    
    def add_course(self, crs_id):
        self.courses.append(crs_id)
    
    def has_course(self, crs_id):
        has = crs_id in self.courses
        """
        if has:
            print self.stu_id, 'has', crs
        else:
            print self.stu_id, 'does not have', crs
        """
        return has
        
    def display(self):
        data = 'Student: ' + str(self.stu_id)
        data += '\n  Courses: ' + str(self.courses)
        return data

class Course:

    def __init__(self, name, enrollment):
        self.crs_id = name
        self.students = ()
        self.enrolled = int(enrollment)
        self.timeslot = 0
        
    def display(self):
        data = 'Course: ' + self.crs_id
        data += '\n  Students: ' + str(self.students)
        return data
        
    def enroll(self, new_students):
        self.students = new_students


### UTILITY ###
def show_items(items):
    for item in items:
        print item.display()
        
def enroll_students(courses, students):
    for course in courses:
        course.enroll([student.stu_id for student in students if student.has_course(course.crs_id)])
        
def get_courses_with_timeslot(courses, slot):
    return [course.crs_id for course in courses if course.timeslot == slot]
    
def get_course_by_id(course_id, courses):
    for course in courses:
        if course.crs_id == course_id:
            return course
    return None

def get_day_and_timeslot_from_timeslot(timeslot):
    exam_day = (timeslot // TIMESLOTS_PER_DAY) + 1
    exam_timeslot = (timeslot % TIMESLOTS_PER_DAY)
    if (exam_timeslot == 0):
        exam_timeslot = TIMESLOTS_PER_DAY
        exam_day -= 1
    return exam_day, exam_timeslot
    
def assign_random_timeslot(courses, maximum):
    for course in courses:
        assign_timeslot(course, random.randint(1,maximum))

def assign_blanket_timeslot(courses, slot):
    for course in courses:
        assign_timeslot(course, slot)
        
def assign_timeslot(course, slot):
    course.timeslot = slot
    
def check_constraints(courses, students, exam_week):
    satisfied = True
    satisfied = satisfied and not has_exam_gaps(courses)
    satisfied = satisfied and not has_student_conflict(courses, students, exam_week)
    satisfied = satisfied and not exceeds_room_cap(courses, exam_week)
    satisfied = satisfied and not exceeds_available_timeslots(courses, exam_week)
    return satisfied

### HARD CONSTRAINTS ###    
def has_exam_gaps(courses):
    timeslots = []
    for course in courses:
        timeslots.append(course.timeslot)
    for x in range(1, max(timeslots)):
        if x not in timeslots:
            print 'CONFLICT: Exam timetable contains EXAM GAP. Timeslot:', x
            return True
    return False
    
def has_student_conflict(courses, students, exam_week):                 # loop through students and make sure each students courses have different timeslots
    for stud in students:
        student_courses = [get_course_by_id(course, courses) for course in stud.courses]

        timeslots = [course.timeslot for course in student_courses]
        if len(timeslots) != len(set(timeslots)):
            print 'CONFLICT: Exam timetable contains STUDENT CONFLICT. Timeslots:', timeslots
            return True

    return False
    
def exceeds_room_cap(courses, exam_week):
    occupancy = {}
    for x in range(1, exam_week.timeslots + 1):
        occupancy[x] = 0
    for course in courses:
        occupancy[course.timeslot] += course.enrolled
    for x in range(1, exam_week.timeslots + 1):
        if (occupancy[x] > exam_week.room_cap):
            print 'CONFLICT: Exam timetable exceeds room capacity. Timeslot:', x 
            return True
    return False
    
def exceeds_available_timeslots(courses, exam_week):
    for course in courses:
        if course.timeslot > exam_week.timeslots:
            print 'CONFLICT: Exam timetable exceeds available timeslots.'
            return True
    return False
    
### SOFT CONSTRAINTS ###
def total_timeslots(courses):
    timeslots = []
    for course in courses:
        timeslots.append(course.timeslot)
    return len(set(timeslots))
    
def total_student_cost(courses, students):
    total_cost = 0
    for stud in students:
        total_cost += CAP_MULTIPLIER*cap(courses, stud) + oap(courses, stud)
    #return 133.75
    return total_cost

# PENALTY FOR SAME DAY EXAMS (CONSECUTIVE)
def cap(courses, stud):
    combos = get_all_sameday_course_combos(courses, stud)     # filter for applicable combinations
    
    penalty = 0
    for combo in combos:                                    # loop through applicable combinations
        pair = list(combo)
        t1 = get_day_and_timeslot_from_timeslot(pair[0].timeslot)[1]    # extract day's timeslot
        t2 = get_day_and_timeslot_from_timeslot(pair[1].timeslot)[1]    
        penalty += 2**(-abs(t1 - t2))
    return penalty
    
# PENALTY FOR SEPARATE DAY EXAMS (OVERNIGHT)
def oap(courses, stud):
    combos = get_all_overnight_course_combos(courses, stud)     # filter for applicable combinations
    
    penalty = 0
    for combo in combos:                                    # loop through applicable combinations
        pair = list(combo)
        d1 = get_day_and_timeslot_from_timeslot(pair[0].timeslot)[0]    # extract day
        d2 = get_day_and_timeslot_from_timeslot(pair[1].timeslot)[0]
        penalty += 2**(-abs(d1 - d2))
    return penalty

# Return combinations for given student
def get_all_sameday_course_combos(courses, stud):
    combos = [list(combo) for combo in get_all_course_combos(courses, stud)]
    filtered = [combo for combo in combos if get_day_and_timeslot_from_timeslot(combo[0].timeslot)[0] == get_day_and_timeslot_from_timeslot(combo[1].timeslot)[0]]
    return filtered
    
def get_all_overnight_course_combos(courses, stud):
    combos = [list(combo) for combo in get_all_course_combos(courses, stud)]
    filtered = [combo for combo in combos if get_day_and_timeslot_from_timeslot(combo[0].timeslot)[0] != get_day_and_timeslot_from_timeslot(combo[1].timeslot)[0]]
    return filtered    
    
def get_all_course_combos(courses, stud):
    combos = []
    
    # loop through all course combos and determine if they belong to the student, use set() to avoid adding duplicates
    for course1 in courses:
        for course2 in courses:
            #print course1.crs_id, course2.crs_id
            if (course1.crs_id != course2.crs_id) and stud.has_course(course1.crs_id) and stud.has_course(course2.crs_id) and ([course1, course2] not in combos):
                combos.append([course1, course2])
                
    return combos
    
    
def assign_canned_timeslots(courses):
    """ Assign timeslots to all courses. """
    for course in courses:
        if course.crs_id in ('001', '004', '006'):
            course.timeslot = 1
        elif course.crs_id == '002':
            course.timeslot = 2
        elif course.crs_id == '003':
            course.timeslot = 3
        elif course.crs_id in ('005', '007'):
            course.timeslot = 4
        elif course.crs_id == '008':
            course.timeslot = 5
        elif course.crs_id == '009':
            course.timeslot = 6
        elif course.crs_id == '010':
            course.timeslot = 7
            
            
        else:
            course.timeslot = 99
         
    
    
def read_crs_file(filename):
    """Read course file and return list of courses, room capacity, and total timeslots."""
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
            print line.strip()
            split_data = line.split()
            courses.append(Course(split_data[0], split_data[1]))
            
        print ''
        
    return courses, room_cap, timeslots
    
def read_stu_file(filename):
    """Read student file and return list of students."""
    students = []
    
    f = open(filename, 'r')
    if f == None:
        print "TT Error: read_stu_file could not open file:", filename 
    
    else:
        stud_count = 1
        for line in f:
            print line.strip()
            new_student = Student(stud_count)
            courses = line.split()
            for course in courses:
                new_student.add_course(course)
            students.append(new_student)
            stud_count += 1
            
        print ''
        
    return students

def print_solution(courses, students):
    printable = ''
    str_slots = str(total_timeslots(courses))
    str_cost = "{0:.2f}".format(total_student_cost(courses, students))
    printable = printable + str_slots + '\t' + str_cost

    for crs in courses:
        exam_day, exam_timeslot = get_day_and_timeslot_from_timeslot(crs.timeslot)
        printable += '\n' + crs.crs_id + '\t' + str(exam_day) + '\t' + str(exam_timeslot) #+ '\t' + str(crs.timeslot)
    
    return printable
    
def write_solution_file(filename, sol):
    """Write solution to file."""

    f = open(filename, 'w')
    if f == None:
        print "TT Error: write_solution_file could not open file:", filename 
    
    else:
        for line in sol:
            f.write(line)
    return
    
def test_combination_code(courses, students):
    print 'Testing combination code...'
    for stud in students:
        pairs = ''
        overnights = 'Overnights: '
        samedays = 'Samedays: '
        for combo in get_all_course_combos(courses, stud):
            pair = list(combo)
            pairs += str((pair[0].crs_id, pair[1].crs_id))
        for combo in get_all_overnight_course_combos(courses, stud):
            overnights += str((combo[0].crs_id, combo[1].crs_id))
        for combo in get_all_sameday_course_combos(courses, stud):
            samedays += str((combo[0].crs_id, combo[1].crs_id))
        print stud.stu_id, pairs, overnights, samedays
        
        
def test_instance(crsfn, stufn, solfn, obj):
    
    if VERBOSE_TESTING:
        print 'Testing...', crsfn, 'and', stufn, "@", time.asctime()

    courses, room_cap, num_exams = read_crs_file(crsfn)
    students = read_stu_file(stufn)
    
    #show_items(students)
    
    #show_items(courses)
    enroll_students(courses, students)
    #show_items(courses)
    
    exam_week = ExamWeek(room_cap, num_exams)
    
    """
    assign_random_timeslot(courses, num_exams)
    
    # Check constraints and loop until satisfied
    while (check_constraints(courses, students, exam_week) == False):
        assign_random_timeslot(courses, num_exams)
    """
    
    assign_canned_timeslots(courses)
    check_constraints(courses, students, exam_week)
    
    print exam_week.display(courses)
    sol = print_solution(courses, students)
    
    print sol
    write_solution_file(solfn, sol)
    
    # print ''
    # test_combination_code(courses, students)

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
        test_instance(crsfile, stufile, solfile, obj_function)


    print "Testing complete!"

    