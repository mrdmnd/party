''' Expects input of the form FOO.json where '''
''' foo.json is formatted like {"class_name": ["student1", "student2", ...], "class_name": [ ]} '''
import sys
import json
from collections import defaultdict
import statistics
import random

NUM_GROUPS = 3

# Our goal is to minimize total "imbalance" across all classes in the dataset.
# Suppose a class has S students with labels [a_1, a_2, ... a_S].
# We'll define "imbalance" of a class as the sample variance of its label counts.
# We'll implement a simple greedy algorithm to attempt to minimize total summed variance:
    # 1. Identify the class with the highest variance.
    # 2. Select an arbitrary student from that class in the majority group.
    # 3. Relabel that student to the minority group
    # 4. Repeat 1-3 until local convergence or iteration limit.
# Steps 1-3 are guaranteed to reduce the sample variance of a single class. 
# However, because a student may be in multiple classes, it is very possible (likely!) that this procedure
# of "swapping" a student's label will increase the variance in another, different class. This algorithm therefore
# does not guarantee an optimal solution.

def argmax(it):
    f = lambda i: it[i]
    return max(range(len(it)), key=f)

def argmin(it):
    f = lambda i: it[i]
    return min(range(len(it)), key=f)

class State(object):
    def __init__(self, path):
        # Load immutable index of classname->[students] from `path`.
        with open(path, 'r') as f:
            self.class_to_student_map = json.load(f)
      
        # Build immutable inverted index of student->[classnames]
        # self.student_to_class_map = defaultdict(list)
        # for (class_name, student_list) in self.class_to_student_map.items():
        #     for student in student_list:
        #         self.student_to_class_map[student].append(class_name)

        # Distribute random initial student labels.
        # The self.student_labels member is MUTABLE. 
        # We'll be modifying it to find the lowest cumulative imbalance.
        distinct_students = set()
        for student_list in self.class_to_student_map.values():
            distinct_students.update(student_list)
        self.student_labels = {}
        for student in distinct_students:
            self.student_labels[student] = random.randint(0, NUM_GROUPS-1)

    def Relabel(self, student_name, new_label):
        self.student_labels[student_name] = new_label

    # Helper method.
    # Build a temporary dict mapping classname->[label1_count, label2_count, ... labelN_count]
    def class_label_count_map(self):
        class_label_count_map = {}
        for class_name, student_list in self.class_to_student_map.items():
            class_label_count_map[class_name] = [0]*NUM_GROUPS
            for student in student_list:
                class_label_count_map[class_name][self.student_labels[student]] += 1
        return class_label_count_map

    # Compute the total variance of our labelling.
    def CumulativeImbalance(self):
        return sum([statistics.variance(counts) for counts in self.class_label_count_map().values()])

    def MostImbalancedClass(self):
        biggest_variance = 0
        most_imbalanced_class = ''
        m = self.class_label_count_map()
        for class_name, counts in m.items():
            if statistics.variance(counts) > biggest_variance:
                biggest_variance = statistics.variance(counts) 
                most_imbalanced_class = class_name
        return (most_imbalanced_class, m[most_imbalanced_class])

    def IterationStep(self):
        # 1. Identify most imbalanced class.
        # 2. Identify majority and minority label.
        # 3. Swap a (random) member of this class from majority to minority label
        #    This ensure that *this class* is more balanced, but what about full dataset?
        #    Compute CumulativeImbalance. If improved, keep the new labelling. If not, use old labelling.
        # 4. Repeat.

        (most_imbalanced_class, counts) = self.MostImbalancedClass()
        print(most_imbalanced_class + "  "  + str(counts))

        majority_label = argmax(counts)
        minority_label = argmin(counts)

        majority_label_students = [student for student in self.class_to_student_map[most_imbalanced_class] if self.student_labels[student] == majority_label]
        self.Relabel(random.choice(majority_label_students), minority_label)

    def GenerateGraphviz(self):
        student_node_format_string = """"{0}" [shape=circle, style=filled, fillcolor="{1} 1.000 1.000"]\n"""
        node_colors = ""
        for (student, label) in self.student_labels.items():
            node_colors += student_node_format_string.format(student, 1.0*label/NUM_GROUPS)

        edge_connectivity_format_string = """"{0}" -- "{1}"\n"""
        edge_connectivity = ""
        for (class_name, student_list) in self.class_to_student_map.items():
            for student_name in student_list:
                edge_connectivity += edge_connectivity_format_string.format(student_name, class_name)

        output = """
graph test {{
  overlap=false
  edge [style="", weight=1, len=1]
{0}
{1}
}}
        """.format(node_colors, edge_connectivity)
        with open("output.dot", 'w') as f:
            f.write(output)
        return

def main(path):
    s = State(path)
    imbalance = s.CumulativeImbalance()
    for iterations in range(100):
        print(imbalance)
        s.IterationStep()
        imbalance = s.CumulativeImbalance()
    s.GenerateGraphviz()

if __name__ == '__main__':
    main(sys.argv[1])
