# random_code

Probably the dumbest idea I've ever had in my life.

What if you told Python the answer you wanted and asked it to generate executable Python code that output the result?

What if you gave it no structure in the generation and just asked it to randomly combine characters until something worked?

That would be a stupid idea.

But here it is.


## Sample Output

```
+-------------+-----------------+-----------------+-------------+
| Target Func | Min Result Size | Max Result Size | Num Results |
+-------------+-----------------+-----------------+-------------+
| is_true     | 8               | 20              | 5           |
+-------------+-----------------+-----------------+-------------+
+------------------------+---------+------------+--------------+-------------+
| Metric                 |     Min |        Max |          Avg |       Total |
+------------------------+---------+------------+--------------+-------------+
| Duration (s)           |    7.35 |   1,798.59 |       680.87 |    3,404.34 |
| Code Samples Generated | 369,220 | 95,660,503 | 35,659,184.2 | 178,295,921 |
| Code Sample Length     |       8 |          9 |          8.2 |          41 |
+------------------------+---------+------------+--------------+-------------+
+--------------+
| Code Samples |
+--------------+
| '~+5/1<9\t'  |
| '\n663*9>6'  |
| '5<0| 466'   |
| '8-.2<940,'  |
| '~7<28&87'   |
+--------------+
```