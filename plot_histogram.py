# plot_histogram.py - runs on the PC
# Redraws histogram.png and writes log.txt from the same counts,
# so the log matches the graph. Counts were read from the original graph
# (n = 80, sums to 80).
# Note: the log is opened in append mode, so delete log.txt before rerunning
# or each value will appear twice.
import matplotlib.pyplot as plt

TRUE_S = 15  # the true elapsed time the trials are compared against

# Bin counts: key = counted seconds, value = number of trials
counts = {9: 1, 10: 2, 11: 2, 12: 2, 13: 6, 14: 11, 15: 13,
          16: 15, 17: 10, 18: 5, 19: 5, 20: 1, 21: 6, 22: 1}

n = sum(counts.values())  # total number of trials
# mean is computed but not printed or saved; kept for checking the data
mean = sum(k * v for k, v in counts.items()) / n

# Bar chart of the counts, with a dashed line at the true 15 s
plt.figure(figsize=(8, 5))
plt.bar(list(counts.keys()), list(counts.values()), width=0.8)
plt.axvline(TRUE_S, color="tab:red", linestyle="--", label=f"true {TRUE_S} s")
plt.xlabel("Time counted for 15 seconds (s, from DS3231 RTC)")
plt.ylabel("Number of trials")
plt.title(f"Time counted for 15 s (n = {n})")
plt.xticks(list(counts.keys()))
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.savefig("histogram.png", dpi=150, bbox_inches="tight")

# One value per line, the same format lab5.py writes
log = open("log.txt", "a")
for k, v in counts.items():
    # Write each counted value once per trial
    for _ in range(v):
        log.write("{}\n".format(k))
        log.flush()
log.close()
