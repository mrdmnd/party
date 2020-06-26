import sys
import csv
import cvxpy as cp

class Student:
    def __init__(self, record_id, first, last, gender, grade):
        self.record_id = record_id
        self.first = first
        self.last = last
        self.gender = gender
        self.grade = grade
        self.color_variable = cp.Variable(boolean=True)
    def __repr__(self):
        color_string = "GOLD" if self.color_variable.value == 1.0 else "BLUE"
        return "{self.record_id}\t{self.first}\t{self.last}\t{self.gender}\t{self.grade}\t{color_string}".format(self=self, color_string=color_string)

class Course:
    def __init__(self, course_id, course_name):
        self.course_id = course_id
        self.course_name = course_name
        self.students = []

    def __repr__(self):
        return "Course({self.course_id}\t{self.course_name})".format(self=self)

    # Returns a CVXPY expression tree.
    def color_variance(self):
        color_variables = [student.color_variable for student in self.students]
        optimal_people_in_gold = len(self.students) / 2.0
        num_gold_people = sum(color_variables)
        return (optimal_people_in_gold - num_gold_people)**2
   
    # For each group, compute the gender variance inside of that group.
    def gender_variance(self):
        color_variables = [student.color_variable for student in self.students]
        num_blue = len(self.students) - sum(color_variables)
        num_gold = sum(color_variables)
        optimal_females_in_blue_split = num_blue / 2.0
        optimal_females_in_gold_split = num_gold / 2.0
        females = [student for student in self.students if student.gender == 'Female']
        female_color_variables = [female.color_variable for female in females]
        num_blue_females = len(female_color_variables) - sum(female_color_variables)
        num_gold_females = sum(female_color_variables)
        # Optimal split expression is thus
        return (optimal_females_in_blue_split - num_blue_females)**2 + (optimal_females_in_gold_split - num_gold_females)**2

    def print_stats(self):
        blue_male = len([s for s in self.students if s.gender == "Male" and s.color_variable.value != 1])
        gold_male = len([s for s in self.students if s.gender == "Male" and s.color_variable.value == 1])
        blue_female = len([s for s in self.students if s.gender == "Female" and s.color_variable.value != 1])
        gold_female = len([s for s in self.students if s.gender == "Female" and s.color_variable.value == 1])
        print(self.course_name)
        print("_|Blue\t|Gold\t|")
        print("M|{0}\t|{1}\t|".format(blue_male, gold_male))
        print("F|{0}\t|{1}\t|".format(blue_female, gold_female))
        return (blue_male, gold_male, blue_female, gold_female)

# Returns a newly-constructed dictionary of Student objects, keyed by record_id field.
def LoadStudents(students_filepath):
    students = {}
    with open(students_filepath) as students_file:
        student_reader = csv.reader(students_file, delimiter=",")
        next(student_reader) # Skip header
        for line in student_reader:
            record_id = line[0]
            first = line[1]
            last = line[2]
            gender = line[3]
            grade = line[4]
            if grade in ("09", "10", "11", "12"):
                students[record_id] = Student(record_id, first, last, gender, grade)
    return students

# Returns a set of frozenset()s of record_ids corresponding to sibling groups.
# Only include siblings who are ALSO in the student set (so we don't include alumni or middle schoolers "in families" here).
def LoadSiblings(siblings_filepath, students):
    # Sibling file is kind of awkwardly formatted. Not denormalized at all.
    # Data comes in groups of THREE. RecordID, first, last.
    # We check index 0, 3, 6, 9, 12, 15, 18 for non-empty record IDs and do the student lookup from there.
    sibling_sets = set()
    with open(siblings_filepath) as siblings_file:
        sibling_reader = csv.reader(siblings_file, delimiter=",")
        next(sibling_reader) # Skip header
        for line in sibling_reader:
            record_id = line[0]
            if record_id in students.keys():
                siblings = {record_id}
                sib_ids = [line[3], line[6], line[9], line[12], line[15], line[18]]
                for sib_id in sib_ids:
                    if sib_id is not "" and sib_id in students.keys(): # Here's the check for "is already considered a student we care about"
                        siblings.add(sib_id)
            if len(siblings) > 1:
                frozen = frozenset(siblings)
                sibling_sets.add(frozen) # cleverly prevents having situations like {1, 2, 3} and {1, 3, 2} added.
    return sibling_sets

# Returns a dictionary of courses, keyed by record_id
def LoadSchedules(schedules_filepath, students):
    # File format is also denormalized. 
    # Setup like (student_id, first, last) and then pairs of (class_id, coursename) - up to 13 courses.
    courses = {}
    with open(schedules_filepath) as schedule_file:
        schedule_reader = csv.reader(schedule_file, delimiter=",")
        next(schedule_reader) # Skip header
        for line in schedule_reader:
            student_id = line[0]
            course_ids = line[3:28:2]
            course_names = line[4:29:2]
            for course_id, course_name in zip(course_ids, course_names):
                if course_id is not "":
                    if course_id not in courses.keys():
                        # Course does not exist, create it and add this student to its roster.
                        courses[course_id] = Course(course_id, course_name)
                    # Now we're sure it exists. Look it up, look up our student, and insert them into the class.
                    courses[course_id].students.append(students[student_id])
    return courses

# Takes a dictionary of courses as input and returns the "objective function" for the optimization problem.
def BuildObjective(courses):
    color_weight = 1.0
    gender_weight = 0.5
    color_term = sum(course.color_variance() for course in courses.values())
    gender_term = sum(course.gender_variance() for course in courses.values())
    return cp.Minimize(color_weight*color_term + gender_weight*gender_term)

def BuildConstraints(siblings, students):
    constraints = []
    for sibling_set in siblings:
        sib_constraint = cp.Variable(boolean=True)
        for student_id in sibling_set:
            student = students[student_id]
            constraints.append( student.color_variable == sib_constraint)
    return constraints

def PrintCourseStatistics(courses):
    print("Class Statistics: ")
    accum = [0, 0, 0, 0]
    for course in courses.values():
        stats = course.print_stats()
        accum[0] += stats[0]
        accum[1] += stats[1]
        accum[2] += stats[2]
        accum[3] += stats[3]
    print("Overall (by assignments)")
    print("  _|Blue\t|Gold\t|Sum\t")
    print("  M|{0}\t|{1}\t|{2}\t".format(accum[0], accum[1], accum[0]+accum[1]))
    print("  F|{0}\t|{1}\t|{2}\t".format(accum[2], accum[3], accum[2]+accum[3]))
    print("Sum|{0}\t|{1}\t|{2}\t".format(accum[0]+accum[2], accum[1]+accum[3], sum(accum)))

def PrintStudentStatistics(students):
    accum = [0, 0, 0, 0]
    for student in students.values():
        if student.gender == "Male" and student.color_variable.value == 0.0:
            accum[0] += 1
        if student.gender == "Male" and student.color_variable.value == 1.0:
            accum[1] += 1
        if student.gender == "Female" and student.color_variable.value == 0.0:
            accum[2] += 1
        if student.gender == "Female" and student.color_variable.value == 1.0:
            accum[3] += 1
    print("Overall (by student count)")
    print("  _|Blue\t|Gold\t|Sum\t")
    print("  M|{0}\t|{1}\t|{2}\t".format(accum[0], accum[1], accum[0]+accum[1]))
    print("  F|{0}\t|{1}\t|{2}\t".format(accum[2], accum[3], accum[2]+accum[3]))
    print("Sum|{0}\t|{1}\t|{2}\t".format(accum[0]+accum[2], accum[1]+accum[3], sum(accum)))




def main(students_filepath, siblings_filepath, schedules_filepath):
    students = LoadStudents(students_filepath)
    siblings = LoadSiblings(siblings_filepath, students)
    courses = LoadSchedules(schedules_filepath, students)

    objective = BuildObjective(courses)
    constraints = BuildConstraints(siblings, students)

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.GUROBI, verbose=True, Threads=4, TimeLimit=60)
    PrintCourseStatistics(courses)
    PrintStudentStatistics(students)
    print("Status: ", problem.status)
    print("Objective Value: ", problem.value)
    print("Assignments: ")
    for student in students.values():
        print(student)

if __name__ == "__main__":
    if len(sys.argv) is not 4:
        print("Needs three arguments, exiting.")
        exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

