# Sorting_Assignment

## Student name(s)

Ziv Beck ID-206917809
Dor Sela ID-209342260


## Selected algorithms

| ID | Algorithm     |
|----|---------------|
| 1  | Bubble Sort   |
| 3  | Insertion Sort|
| 4  | Merge Sort    |

Commands used to generate the figures (mean time over 20 runs per size):

```
```Run this command to execute task 1
python run_experiments.py -a 1 3 4 -s 100 500 1000 3000 -e 0 -r 20

```Run this command to execute task 2
python run_experiments.py -a 1 3 4 -s 100 500 1000 3000 -e 1 -r 20
```

Arguments Explanation-
-a - Choosing the algorithems by their ID as mentioned above
-s - Array sizes
-e - Experiment type
-r - Number of repetitions

Let's dive into the results-

The following is the result of task1 with random arrays-
## result1.png

<img width="1500" height="900" alt="figure1" src="https://github.com/user-attachments/assets/ed90f1b7-00fa-4da5-ab00-eb01d5d05a1d" />


**Explanation:** On random integers, bubble sort and insertion sort show much faster growth of running time with *n* than merge sort, consistent with quadratic versus *n* log *n* behavior. Merge sort stays the lowest curve for larger sizes.

The following is the result of task2 with nearly sorted arrays and noise
## result2.png
<img width="1500" height="900" alt="figure2" src="https://github.com/user-attachments/assets/94f3c928-a770-4a08-8402-481bd1865f00" />



**Explanation:** With ~5% random swaps on an otherwise sorted array, **insertion sort** usually becomes faster relative to the random case, because it stops after few comparisons when each element is already close to its place. **Bubble sort** may improve somewhat but still does many passes. **Merge sort** changes less in shape than insertion, because it always does full divide-and-merge work. Compared to Figure 1, insertion typically drops the most; merge stays similar in ranking (fastest here at larger *n*).
