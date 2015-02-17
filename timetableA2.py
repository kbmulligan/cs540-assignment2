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

MINIMIZE_TIMESLOTS = 0
MINIMIZE_STUDENTCOST = 1

TIME_LIMIT = 590                # time limit for running
WRITE_EVERY = 1                 # write best solution every x seconds

VERBOSE_LOADING = False
VERBOSE_TESTING = True
VERBOSE_ALERTS = False


DEC_PRECISION = 5
PERCENT_DIGITS = 2
EOL = '\n'


subdir = './'
crsfile = "instance1.crs"
stufile = "instance1.stu"
solfile = "instance1.sol"

TIMESLOTS_PER_DAY = 5

CAP_MULTIPLIER = 10

TABU_LIST_LENGTH = 10


class ExamWeek:

    def __init__(self, rmcap, num_exams):
        self.room_cap = rmcap
        self.timeslots = num_exams
        
    def display(self, courses):
        data = '--- Exam Week ---\n' + 'Room capacity:       ' + str(self.room_cap) + '\nAvailable timeslots: ' + str(self.timeslots) + '\n'
        
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

### TIMESLOT ASSIGNMENT ###  
def assign_timeslot(course, slot):
    course.timeslot = slot
    
def assign_random_timeslot(courses, maximum):
    for course in courses:
        assign_timeslot(course, random.randint(1,maximum))

def assign_blanket_timeslot(courses, slot):
    for course in courses:
        assign_timeslot(course, slot)

def assign_timeslots(courses, timeslots):
    """ Assign timeslots to all courses given lists of timeslots and courses of equal length. """
    if len(courses) != len(timeslots):
        print 'ERROR: assign_timeslots given list inputs of differing lengths.'
    else:
        for x in range(len(courses)):
            assign_timeslot(courses[x], timeslots[x])
    
def assign_canned_timeslots(courses):
    """ Assign timeslots to all courses of instance1 based on given example. """
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

### TIMETABLE GENERATION ###
def generate_timetable(courses, exam_week):
    """ Generates initial timetable randomly. """
    maximum = exam_week.timeslots
    return [random.randint(1, maximum) for course in courses]

def generate_sparse_timetable(courses, exam_week):
    """ Generates initial timetable sequentially stepping through available timeslots. """
    timetable = []
    counter = 0
    maximum = exam_week.timeslots
    for course in courses:
        timetable.append((counter % maximum) + 1)
        counter += 1
    return timetable
    
def generate_dense_timetable(courses, exam_week):
    """ Generates initial timetable jamming everything in earliest timeslots. """
    timetable = []
    for course in courses:
        timetable.append(1)
    return timetable
    
def ensure_valid(slot, exam_week):
    slot = min(exam_week.timeslots, slot)
    slot = max(1, slot)
    return slot
    
def perturb_timetable(timetable, exam_week, perturbations=1):
    """ Selects random course(crs) from timetable and moves it STEPS timeslots in the timetable. """
    STEPS = 1
    delta = random.choice([-STEPS, STEPS])
    for x in range(perturbations):
        crs = random.randint(0, len(timetable) - 1)
        timetable[crs] += delta
        timetable[crs] = ensure_valid(timetable[crs], exam_week)
    return timetable
    
def neighboring_timetables(timetable, exam_week, k=1):
    """ Returns list of all timetables 1 step from given timetable (includes given timetable). """
    neighbors = [timetable]
    delta = 1
    steps = k
    for crs in range(len(timetable)):
        new_timetable_up = list(timetable)
        new_timetable_down = list(timetable)
        new_timetable_up[crs] += delta
        new_timetable_down[crs] -= delta
        new_timetable_up[crs] = ensure_valid(new_timetable_up[crs], exam_week)
        new_timetable_down[crs] = ensure_valid(new_timetable_down[crs], exam_week)
        neighbors.append(new_timetable_up)
        neighbors.append(new_timetable_down)
    return neighbors

def find_best(timetables, measure, courses, students):
    """ Returns best timetable in terms of min measure, given courses and students. Returns None if none are better than current score. """
    best = timetables[0]
    lowest_score = measure(courses, students)                       # get current measure
    for table in timetables:
        dummy_courses = list(courses)
        assign_timeslots(dummy_courses, table)
        score = measure(dummy_courses, students)
        # print score
        if (score < lowest_score):
            best = table
            lowest_score = score
    return best

def find_most_feasible(timetables, courses, students, exam_week):
    """ Returns best timetable in terms of feasibility, given courses and students. Returns None if none are better than current score. """
    best = None
    lowest_score = constraint_violations(courses, students, exam_week)
    for table in timetables:
        dummy_courses = list(courses)
        assign_timeslots(dummy_courses, table)
        score = constraint_violations(dummy_courses, students, exam_week)
        # print score
        if (score < lowest_score):
            best = table
            lowest_score = score
    return best
    
def only_feasible(timetables, courses, students, exam_week):
    """ Returns only feasible timetables, given courses and students. """
    feasible = []
    for table in timetables:
        dummy_courses = list(courses)
        assign_timeslots(dummy_courses, table)
        score = constraint_violations(dummy_courses, students, exam_week)
        if (score == 0):
            feasible.append(table)
    return feasible

### CONSTRAINTS ###
def constraint_violations(courses, students, exam_week):
    """ Counts number of constraint violations. """
    violations = 0
    violations += exam_gaps(courses)
    violations += student_conflicts(courses, students, exam_week)
    violations += exceeds_room_cap(courses, exam_week)
    violations += exceeds_available_timeslots(courses, exam_week)
    return violations

### HARD CONSTRAINTS ###    
def exam_gaps(courses):
    """ Returns number of exam gaps given list of courses. """
    gaps = 0
    timeslots = []
    for course in courses:
        timeslots.append(course.timeslot)
    for x in range(1, max(timeslots)):
        if x not in timeslots:
            if VERBOSE_ALERTS: print 'CONFLICT: Exam timetable contains EXAM GAP. Timeslot:', x
            gaps += 1
    return gaps
    
def student_conflicts(courses, students, exam_week):                 # loop through students and make sure each students courses have different timeslots
    """ Returns number of student conflicts given exam week info, courses, and students. """
    conflicts = 0
    for stud in students:
        student_courses = [get_course_by_id(course, courses) for course in stud.courses]

        timeslots = [course.timeslot for course in student_courses]
        if len(timeslots) != len(set(timeslots)):
            if VERBOSE_ALERTS: print 'CONFLICT: Exam timetable contains STUDENT CONFLICT. \n  Student:', stud.stu_id, '\n  Timeslots:', timeslots, '\n'
            conflicts += 1 

    return conflicts
    
def exceeds_room_cap(courses, exam_week):
    """ Checks each timeslot for exceeding room capacity. """
    violations = 0
    occupancy = {}
    for x in range(1, exam_week.timeslots + 1):
        occupancy[x] = 0
    for course in courses:
        occupancy[course.timeslot] += course.enrolled
    for x in range(1, exam_week.timeslots + 1):
        if (occupancy[x] > exam_week.room_cap):
            if VERBOSE_ALERTS: print 'CONFLICT: Exam timetable exceeds room capacity. Timeslot:', x 
            violations += 1
    return violations
    
def exceeds_available_timeslots(courses, exam_week):
    """ Checks exam week for exceeding available timeslots. """
    violations = 0
    for course in courses:
        if course.timeslot > exam_week.timeslots:
            if VERBOSE_ALERTS: print 'CONFLICT: Exam timetable exceeds available timeslots.'
            violations += 1
    return violations
    
### SOFT CONSTRAINTS ###
def total_timeslots(courses, students):
    timeslots = []
    for course in courses:
        timeslots.append(course.timeslot)
    return len(set(timeslots))
    
def total_student_cost(courses, students):
    total_cost = 0
    for stud in students:
        total_cost += CAP_MULTIPLIER*cap(courses, stud) + oap(courses, stud)
    return total_cost

# PENALTY FOR SAME DAY EXAMS (CONSECUTIVE)
def cap(courses, stud):
    combos = get_all_sameday_course_combos(courses, stud)               # filter for applicable combinations
    
    penalty = 0
    for combo in combos:                                                # loop through applicable combinations
        pair = list(combo)
        t1 = get_day_and_timeslot_from_timeslot(pair[0].timeslot)[1]    # extract day's timeslot
        t2 = get_day_and_timeslot_from_timeslot(pair[1].timeslot)[1]    
        penalty += 2**(-abs(t1 - t2))
    return penalty
    
# PENALTY FOR SEPARATE DAY EXAMS (OVERNIGHT)
def oap(courses, stud):
    combos = get_all_overnight_course_combos(courses, stud)             # filter for applicable combinations
    
    penalty = 0
    for combo in combos:                                                # loop through applicable combinations
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
    """ Return all pairs of courses that a given student is taking. """
    combos = []
    
    # loop through all course combos and determine if they belong to the student, use set() to avoid adding duplicates
    for course1 in courses:
        for course2 in courses:
            #print course1.crs_id, course2.crs_id
            if (course1.crs_id != course2.crs_id) and stud.has_course(course1.crs_id) and stud.has_course(course2.crs_id) and ([course1, course2] not in combos):
                combos.append([course1, course2])
                
    return combos

### FILE IO ###
def read_crs_file(filename):
    """Read course file and return list of courses, room capacity, and total timeslots."""
    courses = []
    
    f = open(filename, 'r')
    if f == None:
        print "TT Error: read_crs_file could not open file:", filename 
    else:
        data = f.readline()
        if VERBOSE_LOADING: print data
        data = data.split()
        
        room_cap = int(data[0])
        timeslots = int(data[1])
        
        if VERBOSE_LOADING: print 'Room Capacity:', room_cap
        if VERBOSE_LOADING: print 'Timeslots:', timeslots
        
        if VERBOSE_LOADING: print ''
        
        for line in f:
            if VERBOSE_LOADING: print line.strip()
            split_data = line.split()
            courses.append(Course(split_data[0], split_data[1]))
            
        if VERBOSE_LOADING: print ''
        
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
            if VERBOSE_LOADING: print line.strip()
            new_student = Student(stud_count)
            courses = line.split()
            for course in courses:
                new_student.add_course(course)
            students.append(new_student)
            stud_count += 1
            
        if VERBOSE_LOADING: print ''
        
    return students

def print_solution(courses, students):
    printable = ''
    str_slots = str(total_timeslots(courses, students))
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
    
def write_out(courses, students, exam_week, solfn):
    """ Write to stdout and to file. """
    print exam_week.display(courses)
    sol = print_solution(courses, students)
    print '--- Solution ---'
    print 'Constraint violations: ', constraint_violations(courses, students, exam_week)
    print sol
    print ''
    write_solution_file(solfn, sol)

    
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
        print 'Timetabling...', crsfn, 'and', stufn, "@", time.asctime()

    t0 = t1 = time.time()
    
    courses, room_cap, num_exams = read_crs_file(crsfn)
    students = read_stu_file(stufn)
    enroll_students(courses, students)
    exam_week = ExamWeek(room_cap, num_exams)
    
    ### SETUP COMPLETE - BEGIN SLS ###
    
    ### INITIALIZATION
    if (obj == MINIMIZE_STUDENTCOST):
        measure = total_student_cost
        initial_timetable = generate_sparse_timetable(courses, exam_week)
        print 'SOFT CONSTRAINT: Minimizing student cost.\n'
    else:
        measure = total_timeslots
        initial_timetable = generate_dense_timetable(courses, exam_week)
        print 'SOFT CONSTRAINT: Minimizing timeslots used.\n'
        
    assign_timeslots(courses, initial_timetable)
    
    ### PERTURBATION
    # Check constraints and loop until satisfied
    current = list(initial_timetable)
    tabu_list = [list(current)]
    best_timetables = [list(current)]
    while True:
        neighbors = neighboring_timetables(current, exam_week)
         
        # Write to file at regular intervals
        t2 = time.time()
        if (t2 - t0 > TIME_LIMIT):
            write_out(courses, students, exam_week, solfn)
        elif (t2 - t1 > WRITE_EVERY):
            write_out(courses, students, exam_week, solfn)
            t1 = time.time()
        
        # always check for constraint violations and get away from them
        if (constraint_violations(courses, students, exam_week) > 0):
            best = find_most_feasible(neighbors, courses, students, exam_week)
            if best != None and best not in tabu_list:
                current = best
                assign_timeslots(courses, current)
                tabu_list.append(current)
                if len(tabu_list) > TABU_LIST_LENGTH:
                    tabu_list.pop(0)
            else:
                current = perturb_timetable(current, exam_week, constraint_violations(courses, students, exam_week))
            continue
        
        # begin to optimize when a valid solution has been found
        if (True):
            neighbors = only_feasible(neighboring_timetables(current, exam_week), courses, students, exam_week)
            best = find_best(neighbors, measure, courses, students)
            if best != None:
                current = best
                assign_timeslots(courses, current)
            else:
                current = perturb_timetable(current, exam_week, constraint_violations(courses, students, exam_week))

    ### TERMINATE ###
    write_out(courses, students, exam_week, solfn)

    print ''

    return

if __name__ == "__main__":

    if len(sys.argv) != ARGS:
        print 'Usage: ', sys.argv[0], '<coursefile> <studentfile> <solutionfile> <objectivefunction (0 or 1)>'
    else:
        crsfile = sys.argv[1]
        stufile = sys.argv[2]
        solfile = sys.argv[3]
        obj_function = int(sys.argv[4])
        test_instance(crsfile, stufile, solfile, obj_function)


    print "Testing complete!"

    