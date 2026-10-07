# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Which dashboard insights survive a statistics test?
#
# The course capstone, `StudentPerformanceDashboard_Sanjana_Maini.xlsx`, summarises 70 students with KPI
# cards, pivot charts and five written insights. A dashboard turns small differences into confident
# sentences, so this notebook checks each sentence: is the difference larger than chance alone would
# produce among 70 students?
#
# Method: each claim's number is recomputed from the `Data` sheet, then compared with a permutation test
# (shuffle the group labels 10,000 times and count how often a gap at least as large appears by chance),
# with confidence intervals where they help. Student names are never printed.

# %%
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint

warnings.filterwarnings("ignore")
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
rng = np.random.default_rng(20261007)
R = {}
d = pd.read_excel(ROOT / "StudentPerformanceDashboard_Sanjana_Maini.xlsx", sheet_name="Data ")
d = d.drop(columns=["Student Name"])
R["students"] = len(d)
R["academic_years"] = sorted(d["Academic Year"].unique().tolist())
print(f"{len(d)} students; academic year {R['academic_years']}; departments {d['Department'].value_counts().to_dict()}; "
      f"courses {d['Course Name'].nunique()}")


def perm_spread(values, groups, n=10000):
    """p-value for the spread (max minus min) of group means under random relabelling."""
    v, g = np.asarray(values, float), np.asarray(groups)
    labels = np.unique(g)

    def spread(gg):
        m = [v[gg == lab].mean() for lab in labels]
        return max(m) - min(m)
    obs = spread(g)
    null = np.array([spread(rng.permutation(g)) for _ in range(n)])
    return obs, float((null >= obs).mean())


# %% [markdown]
# ## Insight 1: "MBA Department has the highest average marks"

# %%
dep = d.groupby("Department")["Total Marks"].agg(["size", "mean", "std"]).round(2)
obs, p = perm_spread(d["Total Marks"], d["Department"])
R["insight1"] = {"means": dep["mean"].to_dict(), "spread": obs, "perm_p": p}
print(dep.to_string())
print(f"gap between highest and lowest department mean: {obs:.2f} marks; permutation p = {p:.3f}")

# %% [markdown]
# True as arithmetic (MBA 81.3 against 78.4 for BCOM), but a gap of 2.9 marks between three groups of
# 21 to 26 students appears by chance 43% of the time: no evidence that MBA students perform better.

# %% [markdown]
# ## Insight 2: "Mr. Nair gave the highest average internship score"

# %%
men = d.groupby("Mentor Name")["Internship Score"].agg(["size", "mean"]).round(2)
obs, p = perm_spread(d["Internship Score"], d["Mentor Name"])
R["insight2"] = {"means": men["mean"].to_dict(), "spread": obs, "perm_p": p}
print(men.to_string())
print(f"gap between highest and lowest mentor mean: {obs:.2f} points (scale 6 to 10); permutation p = {p:.3f}")

# %% [markdown]
# Mr. Nair's 8.7 is the highest mean, from 10 students; random assignment of the same scores to mentors
# produces a gap this wide 14% of the time. Suggestive at most.

# %% [markdown]
# ## Insight 3: "Equal number of male and female students have scored A+"

# %%
g = d.groupby("Gender")["Grade"].agg(n="size", a_plus=lambda s: int((s == "A+").sum()))
g["rate"] = g["a_plus"] / g["n"]
g["ci"] = [tuple(np.round(proportion_confint(k, n, method="wilson"), 3)) for k, n in zip(g["a_plus"], g["n"])]
tab = [[g.loc["F", "a_plus"], g.loc["F", "n"] - g.loc["F", "a_plus"]], [g.loc["M", "a_plus"], g.loc["M", "n"] - g.loc["M", "a_plus"]]]
fisher_p = float(stats.fisher_exact(tab)[1])
R["insight3"] = {"counts": g["a_plus"].to_dict(), "n": g["n"].to_dict(), "rates": g["rate"].round(4).to_dict(), "fisher_p": fisher_p}
print(g.to_string())
print(f"Fisher exact test on the rates: p = {fisher_p:.3f}")

# %% [markdown]
# The counts are equal (5 and 5) but the groups are not (39 women, 31 men), so the rates differ, 12.8%
# against 16.1%; and that difference is itself well within chance (p = 0.74). The right sentence is
# "A+ rates are similar for men and women", not that the counts are equal.

# %% [markdown]
# ## Insight 4: "BCOM Department has highest number of placed students"

# %%
pl = d.groupby("Department")["Placement Status"].agg(n="size", placed=lambda s: int((s == "Placed").sum()))
pl["rate"] = pl["placed"] / pl["n"]
pl["ci"] = [tuple(np.round(proportion_confint(k, n, method="wilson"), 3)) for k, n in zip(pl["placed"], pl["n"])]
chi = stats.chi2_contingency(np.column_stack([pl["placed"], pl["n"] - pl["placed"]]))
R["insight4"] = {"placed": pl["placed"].to_dict(), "n": pl["n"].to_dict(), "rate": pl["rate"].round(4).to_dict(), "chi2_p": float(chi[1])}
print(pl.to_string())
print(f"chi-squared test of equal placement rates: p = {chi[1]:.3f}")

# %% [markdown]
# BCOM has the most placed students partly because it is the largest department. Its placement rate
# (57.7%) is the highest too, but the three rates are not distinguishable at this size (p = 0.22).

# %% [markdown]
# ## Insight 5: "Accounting has the least average total marks but the highest attendance %"

# %%
cr = d.groupby("Course Name").agg(n=("Total Marks", "size"), marks=("Total Marks", "mean"), attendance=("Attendance (%)", "mean")).round(2)
print(cr.sort_values("marks").to_string())
acc = d[d["Course Name"] == "Accounting"]
R["insight5"] = {"accounting_n": len(acc), "courses": int(len(cr)), "median_course_size": float(cr["n"].median())}
r_, p_ = stats.pearsonr(d["Attendance (%)"], d["Total Marks"])
R["attendance_marks_r"], R["attendance_marks_p"] = float(r_), float(p_)
print(f"Accounting has {len(acc)} students; courses have a median of {cr['n'].median():.0f} students each")
print(f"across all 70 students, attendance and total marks correlate at r = {r_:.2f} (p = {p_:.2f})")

# %% [markdown]
# The Accounting insight rests on three students. Course-level averages from groups of 2 to 13 cannot
# support a sentence; and across all 70 students, attendance has no relation to marks at all (r = -0.02),
# so a course combining high attendance with low marks is exactly what chance produces.

# %% [markdown]
# ## How many students would the dashboard need?
#
# To detect a 3-mark difference between two groups (marks have a standard deviation of about 8), with the
# usual 5% false-alarm rate and 80% power, each group needs about
# $2 (z_{0.975} + z_{0.8})^2 \sigma^2 / \delta^2$ students.

# %%
sd = float(d["Total Marks"].std())
need = 2 * (stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) ** 2 * sd ** 2 / 3 ** 2
R["sd_total_marks"], R["n_per_group_for_3_marks"] = sd, float(need)
print(f"standard deviation of total marks {sd:.1f}; students needed per group to detect 3 marks: {need:.0f}")

# %% [markdown]
# ## Conclusions
#
# | Dashboard insight | Verdict |
# |---|---|
# | MBA has the highest average marks | Arithmetic, not evidence: 2.9 marks, p = 0.43 |
# | Mr. Nair gives the highest internship scores | Suggestive at most: p = 0.14, 10 students |
# | Equal numbers of men and women scored A+ | Counts equal, groups not; rates 12.8% vs 16.1%, no real difference |
# | BCOM has the most placed students | Partly size; rates not distinguishable (p = 0.22) |
# | Accounting: lowest marks, highest attendance | Three students; attendance and marks are unrelated (r = -0.02) |
#
# With 70 students, detecting even a 3-mark difference between two groups would need about 112 students
# per group. The dashboard's KPI cards are fine; its written insights should either carry sample sizes
# and uncertainty or describe the data without ranking groups. (The dashboard title also says 2023-24;
# every row is 2024-2025.)

# %%
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "insights_tested.json").write_text(json.dumps(R, indent=1, default=float))
print(json.dumps({k: v for k, v in R.items() if not isinstance(v, dict)}, indent=1, default=float))
