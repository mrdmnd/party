# party
A library to assist registrars in partitioning students into groups for socially-distanced learning.

## Problem Motivation
I am a computer science teacher at a private highschool in Northern California.
We are being asked to prepare our students for a "partiioned" schedule when we return to school in the fall.

We intend to assign to each student one of two possible labels or colors ("blue and gold" for reference here) - and on each given week, only the students from one group are allowed to visit school in person. We're looking for an assignment of these colors to each student in a way that minimizes an objective function - in our school's case, we care about minimizing two things: the color-variance inside a class, and the gender-variance within these color groups.

## Goals
Suppose you had a class of 15 students, and you randomly assign labels. You might end up with six students in one color, and nine in another. This is less optimal than a class with eight students in one color and seven in another. Because we're striving for socially distanced learning, it is our goal to ensure that no class accidentally has a large amount of students from one label present on any given day. That is, we're trying to minimize the "imbalance" in a classroom across different labels - this is minimized perfectly when the counts of students for each label is equal, or when the sample variance of the label counts is zero. 

Additionally, we'd like to ensure that our classes are as gender balanced as possible within these blue and gold labels. 

Finally, we'd like to constraints students who have siblings at the school such that all students in one family share the same color, to minimize logistics overhead for the family.

Instead of relying on random labelings to get good partitions, we can use some extra information: a mapping from students-to-classes, as well as a sibling collection.

## Model
### Objective Function
We model this problem as a mixed-integer quadratic program.

The objective function here is a weighted combination of two terms: a "color-variance" term and a "gender-variance" term.

By default, the weight on the color-variance term is 1.0 and the gender-variance term is 0.5.

The color-variance term is summed across all classes. For each class, we compute the "optimal split" as having half the students in the class be blue and half be gold. 

The gender-variance term is summsed across all class/color pairs. For each class/color pair we compute the "optimal split" as half the students in the blue section be male and half the students in the blue section be female - same for gold.

Specifically, our variance terms look like the following:

Color-variance: `(optimal_people_in_gold - num_gold)^2`

Gender-variance: `(optimal_females_in_gold_split - num_gold_females)^2 + (optimal_females_in_blue_split - num_blue_females)^2`

(note: the color-variance term is invariant on which color you choose, and the gender-variance term is invariant on which gender you choose - these were chosen arbitrarily).

### Constraints
The constraints in our problem are "sibling constraints" - we only require that siblings share the same color.
We encode this as a special "free variable" set for each family, `F_i`. For each student `S_n` in that family / set of siblings, we constrain

`S_n = F_i`

For instance, in a family with three siblings, we have three constraints:
`S_1 = F_1`
`S_2 = F_1`
`S_3 = F_1`

In practice, most students do not have siblings, and of the ones who do, their families are small (not more than three or four members) so this approach does not add a lot of constraints or variables.

We require all variables to be boolean-valued.

## Running the Partitioner
### Dependencies / Installation
`party` depends on a commercial solver known as Gurobi. Obtaining an academic license is fairly straight forward for qualifying teachers or educators.
`party` also depends on cvxpy, a nice interface to various LP/QP solvers.

To install our dependencies, download gurobi's installer and set your license up following their instructions (the grbkey thing...)
Then start a new virtual environment:

`python3 -m venv ./env`

Activate the virtual environment:

`. env/bin/activate`

Install our first dependency with pip:

`pip install cvxpy`

Install our second dependency manually, with setup.py file. On my machine, the install directory for Gurobi was `/Library/gurobi/mac64`.

You'll want to navigate there (still inside of the virtualenv!) and run `sudo python setup.py install`.

Test things out: open a python shell and check that `import cvxpy` and `import gurobipy` both work.

## Execution
Call `party.py` with the three input files (schedules.csv, siblings.csv, and students.csv)
TODO(mrdmnd): make this more flexible - for now this is completely useless to other educators because our data format is weird.
