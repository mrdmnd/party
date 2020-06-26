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
Call `party.py` with the three input files (students.csv, siblings.csv, schedules.csv)
TODO(mrdmnd): make this more flexible - for now this is completely useless to other educators because our data format is weird.

## Sample:
```
python miqp.py data/students.csv data/siblings.csv data/schedules.csv
(env) mredmond@jontron68419 party $ python miqp.py data/students.csv data/siblings.csv data/schedules.csv
Using license file /Users/mredmond/gurobi.lic
Academic license - for non-commercial use only
Parameter OutputFlag unchanged
   Value: 1  Min: 0  Max: 1  Default: 1
Changed value of parameter QCPDual to 1
   Prev: 0  Min: 0  Max: 1  Default: 0
Changed value of parameter Threads to 4
   Prev: 0  Min: 0  Max: 1024  Default: 0
Changed value of parameter TimeLimit to 30.0
   Prev: inf  Min: 0.0  Max: inf  Default: inf
Gurobi Optimizer version 9.0.2 build v9.0.2rc0 (mac64)
Optimize a model with 1015 rows, 1518 columns and 13808 nonzeros
Model fingerprint: 0x99d5f330
Model has 855 quadratic objective terms
Variable types: 855 continuous, 663 integer (663 binary)
Coefficient statistics:
  Matrix range     [5e-01, 1e+00]
  Objective range  [0e+00, 0e+00]
  QObjective range [1e+00, 2e+00]
  Bounds range     [1e+00, 1e+00]
  RHS range        [5e-01, 4e+01]
Found heuristic solution: objective 19940.125000
Presolve removed 172 rows and 172 columns
Presolve time: 0.04s
Presolved: 843 rows, 1346 columns, 9305 nonzeros
Presolved model has 843 quadratic objective terms
Variable types: 693 continuous, 653 integer (503 binary)

Root relaxation: objective 3.679375e+02, 7747 iterations, 2.51 seconds

    Nodes    |    Current Node    |     Objective Bounds      |     Work
 Expl Unexpl |  Obj  Depth IntInf | Incumbent    BestBd   Gap | It/Node Time

H    0     0                    17151.125000    1.50000   100%     -    2s
     0     0  367.93750    0  503 17151.1250  367.93750  97.9%     -    2s
H    0     0                    1010.1250000  367.93750  63.6%     -    3s
H    0     0                     967.3750000  367.93750  62.0%     -    3s
H    0     0                     798.3750000  367.93750  53.9%     -    3s
     0     0  368.20342    0  503  798.37500  368.20342  53.9%     -    7s
     0     2  368.20342    0  503  798.37500  368.20342  53.9%     -    7s
     3     8  368.20342    2  638  798.37500  368.20342  53.9%  10.3   10s
H   58    62                     792.3750000  368.20342  53.5%  17.7   12s
H   60    62                     781.3750000  368.20342  52.9%  17.5   12s
   127   136  371.60234   19  574  781.37500  368.20342  52.9%  21.1   15s
H  154   160                     740.3750000  368.20342  50.3%  22.2   16s
   289   309  377.54403   40  532  740.37500  368.20342  50.3%  24.6   20s
   551   599  389.84431   76  485  740.37500  368.20342  50.3%  22.8   25s
H  734   765                     731.1250000  368.20342  49.6%  21.7   29s
   764   815  405.44411  111  435  731.12500  368.20342  49.6%  21.7   30s

Explored 814 nodes (25028 simplex iterations) in 30.02 seconds
Thread count was 4 (of 4 available processors)

Solution count 9: 731.125 740.375 781.375 ... 19940.1

Time limit reached
Best objective 7.311250000000e+02, best bound 3.682034228706e+02, gap 49.6388%
Status:  user_limit
Objective Value:  731.1250000000002
Class Statistics:
AP Calculus AB
_|Blue	|Gold	|
M|6	|3	|
F|6	|4	|
AP Latin Vergil
_|Blue	|Gold	|
M|3	|3	|
F|2	|2	|
Adv. Jazz Dance
_|Blue	|Gold	|
M|0	|0	|
F|4	|3	|
AP Microeconomics
_|Blue	|Gold	|
M|5	|5	|
F|4	|5	|
AP Macroeconomics
_|Blue	|Gold	|
M|6	|5	|
F|4	|5	|
AP Government and Politics United States
_|Blue	|Gold	|
M|2	|2	|
F|7	|7	|
US Government and Political Science
_|Blue	|Gold	|
M|2	|2	|
F|7	|7	|
Cont. Global Lit (H)/1S
_|Blue	|Gold	|
M|5	|2	|
F|4	|4	|
Fairy Tales/ 2S
_|Blue	|Gold	|
M|5	|6	|
F|6	|3	|
AP Calculus BC
_|Blue	|Gold	|
M|7	|6	|
F|6	|3	|
AP Computer Science A
_|Blue	|Gold	|
M|3	|3	|
F|4	|4	|
Topics in Fine Arts
_|Blue	|Gold	|
M|1	|1	|
F|2	|2	|
Ralph Waldo Emerson/ S1
_|Blue	|Gold	|
M|2	|4	|
F|4	|5	|
Lyric and Lifeline/ 2S
_|Blue	|Gold	|
M|5	|3	|
F|4	|3	|
Honors Probability and Statistics
_|Blue	|Gold	|
M|4	|5	|
F|6	|3	|
Statistics
_|Blue	|Gold	|
M|4	|4	|
F|6	|4	|
Jazz Dance
_|Blue	|Gold	|
M|0	|0	|
F|4	|4	|
AP Microeconomics
_|Blue	|Gold	|
M|6	|5	|
F|2	|2	|
AP Macroeconomics
_|Blue	|Gold	|
M|5	|5	|
F|3	|2	|
Applied Sci. Research (H)
_|Blue	|Gold	|
M|7	|4	|
F|2	|1	|
Ralph Waldo Emerson/ S1
_|Blue	|Gold	|
M|3	|2	|
F|5	|3	|
Sizzling Scribes
_|Blue	|Gold	|
M|1	|0	|
F|1	|2	|
Statistics
_|Blue	|Gold	|
M|3	|2	|
F|2	|3	|
AP Japanese
_|Blue	|Gold	|
M|3	|2	|
F|0	|0	|
Sustainable Engineering
_|Blue	|Gold	|
M|7	|5	|
F|4	|2	|
Calculus
_|Blue	|Gold	|
M|8	|4	|
F|5	|4	|
Statistics
_|Blue	|Gold	|
M|4	|6	|
F|6	|5	|
Advanced Photo
_|Blue	|Gold	|
M|6	|5	|
F|2	|1	|
Mechanical/ Electrical Engineering
_|Blue	|Gold	|
M|5	|3	|
F|4	|4	|
Investigations/ 1S
_|Blue	|Gold	|
M|8	|4	|
F|4	|4	|
Experimental Archaeology 1S
_|Blue	|Gold	|
M|6	|3	|
F|3	|2	|
Lyric and Lifeline/ 2S
_|Blue	|Gold	|
M|4	|4	|
F|5	|5	|
Environmental Science
_|Blue	|Gold	|
M|2	|3	|
F|7	|6	|
Adv. Seminar Topics Spanish
_|Blue	|Gold	|
M|1	|1	|
F|4	|1	|
Philosophy/ 1S
_|Blue	|Gold	|
M|3	|2	|
F|3	|3	|
Philosophy/ 2S
_|Blue	|Gold	|
M|2	|1	|
F|0	|0	|
Dystopian Fiction & Film/ 2S
_|Blue	|Gold	|
M|8	|3	|
F|6	|2	|
Investigations/ 1S
_|Blue	|Gold	|
M|8	|5	|
F|2	|2	|
Intro to Computer Science
_|Blue	|Gold	|
M|7	|6	|
F|1	|1	|
Adv Topics in Biology (H)
_|Blue	|Gold	|
M|4	|3	|
F|3	|5	|
Upper Intermediate Spanish
_|Blue	|Gold	|
M|5	|3	|
F|8	|6	|
Foundations 1 French
_|Blue	|Gold	|
M|4	|2	|
F|5	|2	|
Cafe Society/ S1
_|Blue	|Gold	|
M|6	|3	|
F|4	|3	|
Multicultural London/ 2S
_|Blue	|Gold	|
M|6	|2	|
F|2	|3	|
AP Spanish Language
_|Blue	|Gold	|
M|2	|2	|
F|5	|6	|
Engineering Entrepreneurship
_|Blue	|Gold	|
M|3	|5	|
F|3	|1	|
Modern Political Rhetoric 1S
_|Blue	|Gold	|
M|4	|0	|
F|5	|6	|
AP European History
_|Blue	|Gold	|
M|3	|3	|
F|7	|7	|
AP French Language
_|Blue	|Gold	|
M|0	|1	|
F|6	|5	|
AP Spanish Literature
_|Blue	|Gold	|
M|2	|1	|
F|4	|2	|
Neuroscience
_|Blue	|Gold	|
M|1	|2	|
F|6	|5	|
Calculus
_|Blue	|Gold	|
M|4	|4	|
F|5	|2	|
AP Calculus AB
_|Blue	|Gold	|
M|5	|4	|
F|7	|4	|
Adv Topics in Biology (H)
_|Blue	|Gold	|
M|5	|2	|
F|8	|3	|
Post AP CS w/ Data Structures (H)
_|Blue	|Gold	|
M|2	|3	|
F|2	|2	|
The Art of the Essay 2S
_|Blue	|Gold	|
M|4	|3	|
F|6	|5	|
Gothic South 1S
_|Blue	|Gold	|
M|1	|3	|
F|5	|3	|
AP Calculus AB
_|Blue	|Gold	|
M|1	|1	|
F|2	|2	|
Adv. Jazz Dance
_|Blue	|Gold	|
M|0	|0	|
F|4	|2	|
Dystopian Fiction & Film/ 2S
_|Blue	|Gold	|
M|7	|4	|
F|4	|4	|
Post AP CS w/ Data Structures (H)
_|Blue	|Gold	|
M|4	|7	|
F|3	|3	|
Adv Topics in Math (H)
_|Blue	|Gold	|
M|7	|7	|
F|2	|3	|
AdvTopics in CompSci (H)
_|Blue	|Gold	|
M|9	|6	|
F|2	|3	|
Global Issues for Global Citizens/1S
_|Blue	|Gold	|
M|0	|2	|
F|4	|2	|
Adv. Economic Theory (H)
_|Blue	|Gold	|
M|10	|5	|
F|2	|2	|
Honors Probability and Statistics
_|Blue	|Gold	|
M|3	|3	|
F|4	|4	|
Post AP CS w/ Data Structures (H)
_|Blue	|Gold	|
M|5	|5	|
F|6	|5	|
AP Government and Politics United States
_|Blue	|Gold	|
M|6	|4	|
F|8	|3	|
US Government and Political Science
_|Blue	|Gold	|
M|6	|4	|
F|8	|3	|
Adv. Seminar Topics French
_|Blue	|Gold	|
M|1	|1	|
F|2	|1	|
BioTech/Research (H)
_|Blue	|Gold	|
M|1	|1	|
F|4	|4	|
Ethnic Studies 1S
_|Blue	|Gold	|
M|1	|1	|
F|4	|5	|
Dangerous Ideas (H) 1S
_|Blue	|Gold	|
M|5	|2	|
F|7	|4	|
Experimental Archaeology 2S
_|Blue	|Gold	|
M|3	|0	|
F|3	|1	|
Post AP Latin (H)
_|Blue	|Gold	|
M|1	|0	|
F|0	|1	|
Art
_|Blue	|Gold	|
M|7	|3	|
F|4	|6	|
AP Music Theory
_|Blue	|Gold	|
M|0	|0	|
F|3	|3	|
Modern Political Rhetoric 1S
_|Blue	|Gold	|
M|6	|5	|
F|3	|4	|
Leadership Case Studies 2S
_|Blue	|Gold	|
M|5	|1	|
F|6	|4	|
AP Calculus BC
_|Blue	|Gold	|
M|7	|4	|
F|6	|4	|
Photography
_|Blue	|Gold	|
M|6	|2	|
F|2	|4	|
Quantum Mechics (H)  1S
_|Blue	|Gold	|
M|8	|3	|
F|3	|4	|
Electromagnetism & Relativity (H)  2S
_|Blue	|Gold	|
M|8	|3	|
F|3	|4	|
Applied Sci. Research (H)
_|Blue	|Gold	|
M|7	|2	|
F|2	|2	|
Modernist Poetry Workshop 2S
_|Blue	|Gold	|
M|0	|1	|
F|5	|4	|
Global Mythologies 1S
_|Blue	|Gold	|
M|2	|2	|
F|4	|3	|
Art
_|Blue	|Gold	|
M|6	|5	|
F|5	|4	|
Intro to Law 2S
_|Blue	|Gold	|
M|2	|2	|
F|1	|1	|
AdvTopics in CompSci (H)
_|Blue	|Gold	|
M|6	|6	|
F|3	|1	|
War & Peace: Middle East 1S
_|Blue	|Gold	|
M|7	|2	|
F|8	|2	|
Anatomy & Physiology
_|Blue	|Gold	|
M|1	|0	|
F|6	|1	|
Global ScholarsRsrch H 2S
_|Blue	|Gold	|
M|0	|0	|
F|2	|2	|
Upper Intermediate Spanish
_|Blue	|Gold	|
M|4	|3	|
F|7	|6	|
US Economic History 1S
_|Blue	|Gold	|
M|7	|7	|
F|2	|3	|
Anatomy & Physiology
_|Blue	|Gold	|
M|1	|1	|
F|3	|5	|
Design and Architecture
_|Blue	|Gold	|
M|5	|1	|
F|5	|3	|
Swords & Ploughshares 2S
_|Blue	|Gold	|
M|1	|2	|
F|3	|2	|
Pre-Calculus
_|Blue	|Gold	|
M|2	|2	|
F|3	|4	|
Intro to Law 1S
_|Blue	|Gold	|
M|5	|4	|
F|6	|4	|
AP English Literature
_|Blue	|Gold	|
M|4	|4	|
F|5	|5	|
Biology
_|Blue	|Gold	|
M|3	|5	|
F|4	|2	|
Student Life
_|Blue	|Gold	|
M|0	|0	|
F|0	|1	|
Upper Intermediate Mandarin
_|Blue	|Gold	|
M|4	|3	|
F|2	|3	|
AP Computer Science A
_|Blue	|Gold	|
M|4	|3	|
F|2	|3	|
Advanced Journalism
_|Blue	|Gold	|
M|2	|3	|
F|8	|6	|
IP Capstone Seminar H 1S
_|Blue	|Gold	|
M|0	|2	|
F|5	|3	|
AP European History
_|Blue	|Gold	|
M|5	|3	|
F|6	|4	|
Contemp American Issues/2S
_|Blue	|Gold	|
M|3	|2	|
F|7	|3	|
Journalism Leadership
_|Blue	|Gold	|
M|0	|0	|
F|4	|3	|
US Foreign Policy 2S
_|Blue	|Gold	|
M|2	|3	|
F|3	|5	|
Advanced Moviemaking
_|Blue	|Gold	|
M|1	|1	|
F|3	|0	|
Jazz Dance
_|Blue	|Gold	|
M|1	|0	|
F|5	|5	|
Biology
_|Blue	|Gold	|
M|5	|4	|
F|4	|4	|
AP Chemistry
_|Blue	|Gold	|
M|5	|3	|
F|5	|5	|
Global Issues for Global Citizens/1S
_|Blue	|Gold	|
M|1	|1	|
F|1	|1	|
AP English Language
_|Blue	|Gold	|
M|2	|3	|
F|5	|4	|
Adv  Seminar Topics in Mandarin
_|Blue	|Gold	|
M|1	|2	|
F|3	|2	|
Advanced Pre-Calculus
_|Blue	|Gold	|
M|4	|4	|
F|8	|5	|
Post AP CS w/ Data Structures (H)
_|Blue	|Gold	|
M|3	|3	|
F|5	|3	|
AdvTopics in CompSci (H)
_|Blue	|Gold	|
M|5	|6	|
F|1	|1	|
Neuroscience
_|Blue	|Gold	|
M|3	|3	|
F|4	|4	|
AP English Language
_|Blue	|Gold	|
M|5	|4	|
F|6	|3	|
Biology
_|Blue	|Gold	|
M|4	|5	|
F|4	|2	|
Pre-Calculus H
_|Blue	|Gold	|
M|10	|3	|
F|4	|3	|
AP English Language
_|Blue	|Gold	|
M|5	|5	|
F|4	|4	|
Intro to Law 2S
_|Blue	|Gold	|
M|3	|7	|
F|5	|2	|
Biology
_|Blue	|Gold	|
M|3	|5	|
F|3	|4	|
Advanced Pre-Calculus
_|Blue	|Gold	|
M|4	|4	|
F|2	|3	|
Design and Architecture
_|Blue	|Gold	|
M|5	|4	|
F|6	|2	|
AP English Language
_|Blue	|Gold	|
M|5	|4	|
F|5	|4	|
US Foreign Policy 2S
_|Blue	|Gold	|
M|7	|7	|
F|0	|2	|
US Economic History 1S
_|Blue	|Gold	|
M|5	|6	|
F|1	|1	|
Pre-Calculus
_|Blue	|Gold	|
M|4	|3	|
F|5	|6	|
Latin 4
_|Blue	|Gold	|
M|1	|1	|
F|0	|0	|
English 3
_|Blue	|Gold	|
M|7	|5	|
F|4	|2	|
Biology
_|Blue	|Gold	|
M|4	|5	|
F|3	|3	|
Swords & Ploughshares 2S
_|Blue	|Gold	|
M|4	|1	|
F|6	|7	|
Biology
_|Blue	|Gold	|
M|4	|1	|
F|7	|5	|
Biology
_|Blue	|Gold	|
M|3	|0	|
F|9	|5	|
AP Chemistry
_|Blue	|Gold	|
M|4	|3	|
F|3	|2	|
English 3
_|Blue	|Gold	|
M|7	|6	|
F|2	|3	|
Upper Intermediate French
_|Blue	|Gold	|
M|2	|4	|
F|8	|6	|
Advanced Pre-Calculus
_|Blue	|Gold	|
M|5	|5	|
F|3	|6	|
Contemp American Issues/2S
_|Blue	|Gold	|
M|4	|4	|
F|3	|3	|
Upper Intermediate Spanish
_|Blue	|Gold	|
M|4	|4	|
F|7	|4	|
Biology
_|Blue	|Gold	|
M|6	|4	|
F|3	|5	|
AP Spanish Language
_|Blue	|Gold	|
M|1	|0	|
F|3	|4	|
Biology
_|Blue	|Gold	|
M|4	|5	|
F|4	|4	|
Pre-Calculus
_|Blue	|Gold	|
M|2	|4	|
F|5	|2	|
Advanced Art
_|Blue	|Gold	|
M|2	|0	|
F|3	|4	|
Moviemaking
_|Blue	|Gold	|
M|7	|7	|
F|1	|1	|
Journalism Leadership (H)
_|Blue	|Gold	|
M|0	|1	|
F|0	|0	|
Pre-Calculus H
_|Blue	|Gold	|
M|6	|2	|
F|6	|8	|
Ethnic Studies 2S
_|Blue	|Gold	|
M|4	|2	|
F|1	|2	|
Intermediate French
_|Blue	|Gold	|
M|2	|1	|
F|2	|4	|
AP Physics 2
_|Blue	|Gold	|
M|7	|4	|
F|3	|2	|
AP English Literature
_|Blue	|Gold	|
M|0	|1	|
F|7	|5	|
AP English Language
_|Blue	|Gold	|
M|4	|1	|
F|3	|5	|
AP Physics 2
_|Blue	|Gold	|
M|6	|4	|
F|2	|3	|
Chamber Choir
_|Blue	|Gold	|
M|1	|2	|
F|2	|2	|
Intermediate Spanish
_|Blue	|Gold	|
M|5	|4	|
F|6	|7	|
Jazz Band
_|Blue	|Gold	|
M|4	|5	|
F|0	|1	|
Intro to Law 1S
_|Blue	|Gold	|
M|3	|3	|
F|4	|4	|
English 2
_|Blue	|Gold	|
M|3	|3	|
F|6	|6	|
Conceptual Chemistry
_|Blue	|Gold	|
M|5	|4	|
F|6	|3	|
Intermediate Spanish
_|Blue	|Gold	|
M|6	|6	|
F|5	|5	|
AP US History
_|Blue	|Gold	|
M|2	|2	|
F|7	|5	|
Algebra 2 W/ Trig.
_|Blue	|Gold	|
M|5	|2	|
F|5	|4	|
English 2
_|Blue	|Gold	|
M|5	|3	|
F|5	|5	|
Conceptual Chemistry
_|Blue	|Gold	|
M|3	|5	|
F|5	|2	|
AP US History
_|Blue	|Gold	|
M|5	|4	|
F|5	|6	|
Algebra 2 Foundations
_|Blue	|Gold	|
M|5	|4	|
F|3	|2	|
English 2
_|Blue	|Gold	|
M|3	|7	|
F|6	|2	|
Latin 3 H
_|Blue	|Gold	|
M|1	|3	|
F|2	|1	|
Accelerated Chemistry (H)
_|Blue	|Gold	|
M|4	|3	|
F|5	|5	|
US History
_|Blue	|Gold	|
M|6	|4	|
F|4	|4	|
Algebra 2 W/ Trig. (H)
_|Blue	|Gold	|
M|5	|6	|
F|6	|5	|
English 2
_|Blue	|Gold	|
M|3	|7	|
F|5	|2	|
Intermediate French
_|Blue	|Gold	|
M|1	|1	|
F|3	|3	|
Algebra 2 W/ Trig.
_|Blue	|Gold	|
M|0	|1	|
F|7	|3	|
English 2
_|Blue	|Gold	|
M|5	|4	|
F|3	|3	|
Accelerated Chemistry (H)
_|Blue	|Gold	|
M|2	|6	|
F|5	|4	|
Mechanical/ Electrical Engineering
_|Blue	|Gold	|
M|5	|5	|
F|3	|3	|
US History
_|Blue	|Gold	|
M|5	|5	|
F|5	|4	|
Algebra 2 W/ Trig. (H)
_|Blue	|Gold	|
M|7	|9	|
F|2	|3	|
English 2
_|Blue	|Gold	|
M|5	|5	|
F|3	|3	|
Conceptual Chemistry
_|Blue	|Gold	|
M|4	|5	|
F|5	|4	|
AP US History
_|Blue	|Gold	|
M|4	|3	|
F|6	|6	|
Algebra 2 W/ Trig.
_|Blue	|Gold	|
M|1	|6	|
F|4	|3	|
Accelerated Chemistry (H)
_|Blue	|Gold	|
M|4	|4	|
F|5	|5	|
AP US History
_|Blue	|Gold	|
M|2	|6	|
F|7	|3	|
Intermediate Mandarin
_|Blue	|Gold	|
M|5	|5	|
F|6	|6	|
Intro to Computer Science
_|Blue	|Gold	|
M|7	|4	|
F|3	|2	|
Foundations 2 Spanish
_|Blue	|Gold	|
M|5	|5	|
F|6	|5	|
English 2
_|Blue	|Gold	|
M|3	|4	|
F|6	|5	|
Accelerated Chemistry (H)
_|Blue	|Gold	|
M|4	|4	|
F|4	|3	|
Foundations 2 Spanish
_|Blue	|Gold	|
M|2	|4	|
F|3	|4	|
Conceptual Chemistry
_|Blue	|Gold	|
M|3	|4	|
F|3	|3	|
Algebra 2 W/ Trig.
_|Blue	|Gold	|
M|2	|3	|
F|7	|3	|
US History
_|Blue	|Gold	|
M|4	|6	|
F|3	|2	|
Algebra 2 W/ Trig.
_|Blue	|Gold	|
M|3	|2	|
F|3	|4	|
AP Computer Science A
_|Blue	|Gold	|
M|3	|6	|
F|3	|3	|
US History
_|Blue	|Gold	|
M|4	|4	|
F|2	|3	|
Algebra 2 W/ Trig.
_|Blue	|Gold	|
M|5	|5	|
F|7	|5	|
Introduction to Journalism
_|Blue	|Gold	|
M|5	|2	|
F|6	|5	|
English 2
_|Blue	|Gold	|
M|4	|3	|
F|3	|4	|
Conceptual Chemistry
_|Blue	|Gold	|
M|6	|2	|
F|4	|4	|
US History
_|Blue	|Gold	|
M|4	|4	|
F|2	|2	|
Intermediate Spanish
_|Blue	|Gold	|
M|6	|5	|
F|7	|3	|
Photography
_|Blue	|Gold	|
M|3	|3	|
F|3	|4	|
Analytic Geometry and Algebra
_|Blue	|Gold	|
M|3	|5	|
F|2	|5	|
Latin 2
_|Blue	|Gold	|
M|5	|4	|
F|1	|2	|
Yearbook: Publication Design I
_|Blue	|Gold	|
M|0	|1	|
F|7	|3	|
Latin 3
_|Blue	|Gold	|
M|1	|1	|
F|1	|1	|
Intermediate Spanish
_|Blue	|Gold	|
M|5	|5	|
F|6	|6	|
Foundations 2 Spanish
_|Blue	|Gold	|
M|2	|2	|
F|2	|2	|
Intermediate Spanish
_|Blue	|Gold	|
M|8	|5	|
F|4	|6	|
Analytic Geometry and Algebra
_|Blue	|Gold	|
M|6	|1	|
F|3	|7	|
Analytic Geometry and Algebra
_|Blue	|Gold	|
M|5	|5	|
F|4	|4	|
Photography
_|Blue	|Gold	|
M|1	|4	|
F|3	|2	|
Analytic Geometry and Algebra
_|Blue	|Gold	|
M|4	|3	|
F|5	|3	|
Chamber Orchestra
_|Blue	|Gold	|
M|1	|2	|
F|3	|3	|
Foundations 1 Mandarin
_|Blue	|Gold	|
M|0	|1	|
F|4	|3	|
English 2
_|Blue	|Gold	|
M|4	|3	|
F|5	|3	|
English 1
_|Blue	|Gold	|
M|7	|4	|
F|4	|2	|
Modern World History
_|Blue	|Gold	|
M|4	|4	|
F|2	|2	|
Physics 1
_|Blue	|Gold	|
M|3	|5	|
F|6	|5	|
Freshman Seminar A Fall
_|Blue	|Gold	|
M|21	|20	|
F|16	|18	|
How Music Works 2S
_|Blue	|Gold	|
M|5	|2	|
F|3	|6	|
English 1
_|Blue	|Gold	|
M|5	|6	|
F|2	|5	|
Modern World History
_|Blue	|Gold	|
M|4	|5	|
F|6	|4	|
Physics 1
_|Blue	|Gold	|
M|5	|4	|
F|3	|4	|
Select Mixed Chorus
_|Blue	|Gold	|
M|0	|1	|
F|3	|2	|
Analytic Geometry and Algebra (H)
_|Blue	|Gold	|
M|5	|5	|
F|4	|4	|
Freshman Seminar A Spring
_|Blue	|Gold	|
M|20	|15	|
F|18	|22	|
Women's Chorus 1S
_|Blue	|Gold	|
M|0	|1	|
F|6	|5	|
English 1
_|Blue	|Gold	|
M|3	|6	|
F|5	|4	|
Modern World History
_|Blue	|Gold	|
M|3	|3	|
F|5	|6	|
Physics 1
_|Blue	|Gold	|
M|3	|6	|
F|6	|3	|
English 1
_|Blue	|Gold	|
M|3	|4	|
F|5	|4	|
Modern World History
_|Blue	|Gold	|
M|1	|5	|
F|6	|4	|
Body Maintenance 2S
_|Blue	|Gold	|
M|4	|1	|
F|5	|8	|
Modern World History
_|Blue	|Gold	|
M|6	|4	|
F|4	|5	|
Physics 1
_|Blue	|Gold	|
M|5	|3	|
F|5	|5	|
Modern World History
_|Blue	|Gold	|
M|7	|4	|
F|1	|5	|
Analytic Geometry and Algebra (H)
_|Blue	|Gold	|
M|7	|5	|
F|4	|5	|
English 1
_|Blue	|Gold	|
M|6	|5	|
F|4	|4	|
Modern World History
_|Blue	|Gold	|
M|6	|3	|
F|5	|5	|
Beyond Words 2S
_|Blue	|Gold	|
M|4	|6	|
F|4	|3	|
English 1
_|Blue	|Gold	|
M|6	|3	|
F|4	|6	|
Physics 1
_|Blue	|Gold	|
M|6	|2	|
F|4	|6	|
Foundations 2 Mandarin
_|Blue	|Gold	|
M|7	|3	|
F|1	|2	|
Modern World History
_|Blue	|Gold	|
M|6	|4	|
F|4	|6	|
English 1
_|Blue	|Gold	|
M|5	|3	|
F|4	|6	|
Men's Chorus 2S
_|Blue	|Gold	|
M|4	|4	|
F|0	|0	|
Physics 1
_|Blue	|Gold	|
M|5	|5	|
F|4	|4	|
Foundations 2 Spanish
_|Blue	|Gold	|
M|4	|4	|
F|5	|6	|
Foundations 2 Spanish
_|Blue	|Gold	|
M|2	|3	|
F|0	|0	|
Latin 2
_|Blue	|Gold	|
M|3	|3	|
F|0	|0	|
English 1
_|Blue	|Gold	|
M|3	|3	|
F|4	|5	|
Physics 1
_|Blue	|Gold	|
M|6	|3	|
F|3	|6	|
Foundations 2 French
_|Blue	|Gold	|
M|3	|1	|
F|2	|3	|
Art of Visual Design 2S
_|Blue	|Gold	|
M|4	|6	|
F|4	|1	|
Integrated Geometry & Algebra
_|Blue	|Gold	|
M|3	|3	|
F|2	|3	|
Conceptual Physics
_|Blue	|Gold	|
M|3	|3	|
F|2	|3	|
Foundations 1 Spanish
_|Blue	|Gold	|
M|3	|2	|
F|3	|2	|
Modern World History
_|Blue	|Gold	|
M|4	|3	|
F|2	|3	|
Analytic Geometry and Algebra (H)
_|Blue	|Gold	|
M|4	|4	|
F|2	|3	|
Body Maintenance 1S
_|Blue	|Gold	|
M|3	|3	|
F|4	|5	|
Foundations 2 French
_|Blue	|Gold	|
M|2	|1	|
F|2	|2	|
English 1
_|Blue	|Gold	|
M|3	|1	|
F|3	|4	|
Art of Visual Design 1S
_|Blue	|Gold	|
M|3	|4	|
F|5	|5	|
Beyond Words 1S
_|Blue	|Gold	|
M|8	|5	|
F|2	|2	|
Integrated Geometry & Algebra
_|Blue	|Gold	|
M|5	|3	|
F|2	|4	|
Conceptual Physics
_|Blue	|Gold	|
M|5	|3	|
F|2	|4	|
How Music Works 1S
_|Blue	|Gold	|
M|6	|2	|
F|2	|5	|
Analytic Geometry and Algebra
_|Blue	|Gold	|
M|0	|2	|
F|6	|4	|
Push Play 2S
_|Blue	|Gold	|
M|0	|0	|
F|1	|1	|
Yearbook: Publication Design Leadership
_|Blue	|Gold	|
M|0	|1	|
F|1	|0	|
Push Play 1S
_|Blue	|Gold	|
M|0	|1	|
F|1	|1	|
Yearbook: Publication Design II
_|Blue	|Gold	|
M|0	|0	|
F|0	|1	|
Improv: Whose Line is It Anyway 2S
_|Blue	|Gold	|
M|0	|1	|
F|0	|0	|
Latin 1
_|Blue	|Gold	|
M|1	|1	|
F|1	|0	|
Drama
_|Blue	|Gold	|
M|1	|0	|
F|3	|1	|
Foundations 1 Spanish
_|Blue	|Gold	|
M|2	|1	|
F|0	|0	|
Assignments:

(elided for privacy reasons)
```
