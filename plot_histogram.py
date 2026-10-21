# plot_histogram.py - runs on the PC
# Reads the trial times in log.txt (one value per line, written by lab5.py)
# and draws a histogram of them in histogram.png.
from collections import Counter

import matplotlib.pyplot as plt

TRUE_S = 15  # the true elapsed time the trials are compared against

# Read one counted time per line, skipping blank lines
with open("log.txt") as f:
    values = [int(line) for line in f if line.strip()]

# Count how many trials gave each counted time
counts = Counter(values)
keys = sorted(counts)
n = len(values)  # total number of trials

# Bar chart of the counts, with a dashed line at the true 15 s
plt.figure(figsize=(8, 5))
plt.bar(keys, [counts[k] for k in keys], width=0.8)
plt.axvline(TRUE_S, color="tab:red", linestyle="--", label=f"true {TRUE_S} s")
plt.xlabel("Time counted for 15 seconds (s, from DS3231 RTC)")
plt.ylabel("Number of trials")
plt.title(f"Time counted for 15 s (n = {n})")
plt.xticks(keys)
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.savefig("histogram.png", dpi=150, bbox_inches="tight")
