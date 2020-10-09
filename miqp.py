import sys
import csv
import cvxpy as cp

class Student:
    def __init__(self, legacy_id, veracross_id, first, last, gender, grade):
        self.legacy_id = legacy_id
        self.veracross_id = veracross_id
        self.first = first
        self.last = last
        self.gender = gender
        self.grade = grade
        self.color_variable = cp.Variable(boolean=True)

    def __repr__(self):
        color_string = "GOLD" if self.color_variable.value == 1.0 else "BLUE"
        return "{self.legacy_id}\t{self.veracross_id}\t{self.first}\t{self.last}\t{self.gender}\t{self.grade}\t{color_string}\n".format(self=self, color_string=color_string)

class Course:
    def __init__(self, course_id, course_name, course_block):
        self.course_id = course_id
        self.course_name = course_name
        self.course_block = course_block
        self.students = [] # Mutable!

    def __repr__(self):
        return "Course({self.course_id}\t{self.course_name})".format(self=self)

    # Returns a CVXPY expression tree.
    # For each group, compute the color variance inside of that group.
    def color_variance(self):
        color_variables = [student.color_variable for student in self.students]
        optimal_split = len(self.students) / 2.0
        num_gold = sum(color_variables)
        return (optimal_split - num_gold)**2
   
    # Returns a CVXPY expression tree.
    # For each group, compute the gender variance inside of that group.
    def gender_variance(self):
        color_variables = [student.color_variable for student in self.students]
        num_students = len(self.students)
        num_gold = sum(color_variables)
        num_blue = num_students - num_gold

        optimal_females_in_blue_split = num_blue / 2.0
        optimal_females_in_gold_split = num_gold / 2.0

        females = [student for student in self.students if student.gender == 'Female']
        female_color_variables = [female.color_variable for female in females]

        num_females = len(females)
        num_gold_females = sum(female_color_variables)
        num_blue_females = num_females - num_gold_females
        
        return (optimal_females_in_blue_split - num_blue_females)**2 + \
               (optimal_females_in_gold_split - num_gold_females)**2

    def get_stats(self):
        blue_male = len([s for s in self.students if s.gender == "Male" and s.color_variable.value != 1])
        gold_male = len([s for s in self.students if s.gender == "Male" and s.color_variable.value == 1])
        blue_female = len([s for s in self.students if s.gender == "Female" and s.color_variable.value != 1])
        gold_female = len([s for s in self.students if s.gender == "Female" and s.color_variable.value == 1])
        return (blue_male, gold_male, blue_female, gold_female)

# Returns a newly-constructed dictionary of Student objects, keyed by legacy_id field.
def LoadStudents(students_filepath):
    students = {}
    with open(students_filepath) as students_file:
        student_reader = csv.reader(students_file, delimiter=",")
        next(student_reader) # Skip header
        for line in student_reader:
            (legacy_id, veracross_id, first, last, gender, grade) = line
            students[legacy_id] = Student(legacy_id, veracross_id, first, last, gender, grade)
    return students

# Returns a list of pairs of sibling relations [(legacy_id, related_legacy_id), ...]
def LoadSiblings(siblings_filepath):
    sibling_relations = []
    with open(siblings_filepath) as siblings_file:
        sibling_reader = csv.reader(siblings_file, delimiter=",")
        next(sibling_reader) # Skip header
        for line in sibling_reader:
            (legacy_id, first, last, related_legacy_id, related_first, related_last) = line
            sibling_relations.append((legacy_id, related_legacy_id))
    return sibling_relations

# Processes the list of sibling edges into a list of "connected component" tuples
# This is the equivalence-class finding code!
def ProcessSiblings(sibling_relationships):
    groups = {}
    for (x, y) in sibling_relationships:
        xset = groups.get(x, set([x]))
        yset = groups.get(y, set([y]))
        jset = xset | yset
        for z in jset:
            groups[z] = jset
    return set(map(tuple, groups.values()))

# Returns a dictionary of courses, keyed by record_id
# Schedule CSV is of the form veracross_id, legacy_id, first, last, course_id, course_name, course_block
def LoadSchedules(schedules_filepath, students):
    courses = {}
    with open(schedules_filepath) as schedule_file:
        schedule_reader = csv.reader(schedule_file, delimiter=",")
        next(schedule_reader) # Skip header
        for line in schedule_reader:
            (veracross_id, legacy_id, first, last, course_id, course_name, course_block) = line
            # For subpartitioning: if we're trying to process a course for a student that doens't exist, skip the line.
            if legacy_id not in students:
                continue
            if course_id not in courses.keys():
                # Course does not exist, so create it.
                courses[course_id] = Course(course_id, course_name, course_block)
            # Now we're sure it exists. Look it up, look up our student, and insert them into the class.
            courses[course_id].students.append(students[legacy_id])
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
    for sibling_tuple in siblings:
        sib_constraint = cp.Variable(boolean=True)
        for legacy_id in sibling_tuple:
            # If we see a legacy_id from a sibling tuple that's not in our students list,
            # we are considering poorly partitioned data, so skip this sibling tuple.
            if legacy_id not in students:
                break
            student = students[legacy_id]
            constraints.append( student.color_variable == sib_constraint)
    return constraints

def ExportStatistics(students, courses):
    with open('balance_stats.txt', 'w') as f:
        accum = [0, 0, 0, 0]
        for course in courses.values():
            stats = course.get_stats()
            accum[0] += stats[0]
            accum[1] += stats[1]
            accum[2] += stats[2]
            accum[3] += stats[3]
        f.write("Overall (assignments)\n")
        f.write("___|Blue\t|Gold\t|Sum\t\n")
        f.write("  M|{0}\t|{1}\t|{2}\t\n".format(accum[0], accum[1], accum[0]+accum[1]))
        f.write("  F|{0}\t|{1}\t|{2}\t\n".format(accum[2], accum[3], accum[2]+accum[3]))
        f.write("Sum|{0}\t|{1}\t|{2}\t\n".format(accum[0]+accum[2], accum[1]+accum[3], sum(accum)))

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
        f.write("Overall (students)\n")
        f.write("___|Blue\t|Gold\t|Sum\t\n")
        f.write("  M|{0}\t|{1}\t|{2}\t\n".format(accum[0], accum[1], accum[0]+accum[1]))
        f.write("  F|{0}\t|{1}\t|{2}\t\n".format(accum[2], accum[3], accum[2]+accum[3]))
        f.write("Sum|{0}\t|{1}\t|{2}\t\n".format(accum[0]+accum[2], accum[1]+accum[3], sum(accum)))


def ExportAssignments(students):
    with open('assignments.tsv', 'w') as f:
        f.write("Legacy ID\tVeracross Id\tFirst\tLast\tGender\tGrade\tAssignment\n")
        for student in students.values():
            f.write(repr(student))
    

def main(students_filepath, siblings_filepath, schedules_filepath):
    students = LoadStudents(students_filepath)
    siblings = ProcessSiblings(LoadSiblings(siblings_filepath))
    courses = LoadSchedules(schedules_filepath, students)

    objective = BuildObjective(courses)
    constraints = BuildConstraints(siblings, students)

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.GUROBI, verbose=True, Threads=4, TimeLimit=60)
    print("Status: ", problem.status)
    print("Objective Value: ", problem.value)
    ExportStatistics(students, courses)
    ExportAssignments(students)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Needs three arguments, exiting.")
        exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

