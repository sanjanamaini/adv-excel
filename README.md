# Advanced Excel Coursework

A structured Advanced Excel course (July to November 2025): weekly assignments, pivot tables, charts, slicers, text-to-columns, and a final comprehensive assignment covering 17 topics, culminating in a KPI dashboard capstone.

**At a glance**

| | |
|---|---|
| **Question** | Do the five written insights of a student-performance dashboard survive a statistics test? |
| **Data** | 70 students |
| **Result** | Built the dashboard as an Advanced Excel capstone, then tested its insights with permutation tests: none held at 70 students, and about 112 per group would be needed to detect a 3-mark gap |
| **Stack** | Excel (pivot tables, charts, slicers), Python for the tests |

## Capstone: Student Performance Dashboard

**`StudentPerformanceDashboard_Sanjana_Maini.xlsx`**: the flagship piece. Built from a 70-student dataset (`Data` sheet), with:

- 4 KPI cards (Average Attendance %, Overall Average Marks, Student Count, Placement %)
- 5 pivot-table-driven charts (department-wise marks, gender-wise grade distribution, department-wise placement %, average marks & attendance by department, internship score by mentor)
- Written insight callouts alongside the charts, e.g. "Accounting has the least average total marks but the highest attendance %"

## Do the dashboard's insights survive a statistics test?

[`notebooks/dashboard_insights_tested.ipynb`](notebooks/dashboard_insights_tested.ipynb) re-computes each of the dashboard's five written insights from the `Data` sheet and tests it with a permutation or exact test. None survives as evidence: the department gap in marks (2.9 marks) appears by chance 43% of the time; the "equal" A+ counts (5 and 5) come from groups of 39 and 31 students; BCOM's lead in placements is partly its size (rates not distinguishable, p = 0.22); and the Accounting insight rests on three students, while attendance and marks are unrelated across all 70 (r = -0.02). Detecting even a 3-mark difference would need about 112 students per group. The lesson: on 70 rows, a dashboard should show sample sizes and uncertainty next to every ranking.

## Everything else

Weekly graded assignments (`Saturday-Sanjana-Assignment *.xlsx`, `EXCEL SKRM/`), a pivot/chart/slicer exercise (`PiVot_chart_slicer_Assignment 10...xlsx`), a comprehensive 17-topic final assignment (`final asst_sanjana_saturday.xlsx`), and supporting sample datasets used across the course.

## Tools

Microsoft Excel: pivot tables, PivotCharts, slicers, VLOOKUP/formulas, text-to-columns, conditional formatting.
