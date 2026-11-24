**A2. Overfull boxes — a float or line runs past its box.** `grep -nE 'Overfull \\[hv]box' <compile log>`.
A large `Overfull \hbox` (over ~5pt) on a figure/table page is the top signal that a float or a
tabular is wider than its column. Fix the float (A6/A7), do not ignore it.
