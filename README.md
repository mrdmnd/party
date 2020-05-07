# party
A library to assist registrars in partitioning students into groups for socially-distanced learning.

## Problem Motivation
Exploration: what happens if we go back to school in the fall, but we are required to have fewer students in
our classrooms at any given time?

One potential model for implementing this policy choice is the "partitioned" schedule - assign each student a label or color ("1, 2, 3" or "blue, grey, gold" - whatever) - and on each given day or week, students with a subset of the labels are allowed to visit school in person. For instance, suppose you chose two labels (RED and BLUE) and declared alternating weeks as RED or BLUE weeks. This would (on average) reduce the effective class size by a factor of two. However, it has some rawbacks - namely, students in different labels would never get a chance to interact in person.

Consider a slightly modified approach that allows students some cross-interaction between groups: we label students into one of THREE labels (RED, BLUE, GREEN) and then rotate through our weeks as (RED+BLUE, BLUE+GREEN, GREEN+RED) - this means that every group would get to interact with members of the other groups at some point, and our "student density" is on average 2/3rds (2 groups per period, 3 total groups).

In general, if we partition students into K groups and allow N of those groups to be physically present in an given period, our density should average N / K.

In practice, it will be problematic for students and parents to remember schedules with more than say, three labels. I suggest that if we move to this model, a reasonably good choice is K = 3 or 4 and N = 2, as described above.

## Analysis
Although the "average" argument above is a good one under the assumptions of the central limit theorem and random label assignment, I think we can do better. Because we're striving for socially distanced learning, it is our goal to ensure that no class accidentally has a large amount of students from one label present on any given day. That is, we're trying to minimize the "imbalance" in a classroom across different labels - this is minimized perfectly when the counts of students for each label is equal, or when the sample variance of the label counts is zero. Consider a classroom of 24 students. A "perfect" balance across three label classes would be [8, 8, 8]. A very imbalanced partition would look like [4, 14, 6].

 Instead of relying on random labelings to get good partitions, we can use extra information: a mapping from students-to-classes. I wrote some code to scrape this mapping from the Knightbook (see knightbook.py), but ultimately, as long as you can provide a mapping from a string (class name) to lists of strings (students in the class), you can use the tools in partitioner.py.

This script produces a labelling for each student starting from a random seed, then iteratively attempts to improve it by identifying the class with the largest variance (most imbalanced class) and swapping an arbitrary student from the majority label in that class to a minority label. This isn't guaranteed to be globally optimal, because it will likely modify some other class, but as a greedy algorithm it's pretty good.

After convergence or hitting an iteration limit, the script terminates and publishes the labelling for each student.

## Usage
### partitioner.py
`partitioner` expects to be called from the command line with a single argument - a path to a json file containing a dictionary mapping strings (class names) to lists of strings (students in that class).

I have not included such a file in this repository for privacy reasons. Such a file can be generated for Menlo School by using the included KnightBook scraper, though.

Partitioner implements the above-described algorithm and publishes the mapping as a graphviz file.

To compile the graph from the outputted dot file, you can run
    
    sfdp -v -Tpng output.dot > output.png

### knightbook.py
This script uses Selenium to automate a headless chrome browser, and click through each class on knightbook one-by-one to identify which students are present in that class. It stores this information to a dictionary, and then writes the dictionary out to a .json file. It's incredibly kludgy and was written in two hours after a couple of beers. Please no judgerino. 
