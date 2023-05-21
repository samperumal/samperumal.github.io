import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import json

brackets = []
with open("tax/tax-data.json", "r") as i:
    data = json.load(i)
    #print(data)
    brackets = data['brackets']

def tax(x, year):
    for row in data['thresholds']:
        if row['year'] == year:
            threshold = row['Under 65']
    for row in brackets:
        if year == row['year'] and x < row['high']:
            tax = row['fixed'] + (x - row['thresh']) * row['perc'] / 100
            if x >= threshold:
                return tax
            else:
                return 0
    return 0

def rebate(year):
    for row in data['rebates']:
        if row['year'] == year:
            return row['Under 65']

def year_tax(year):
    return lambda x: max(0, tax(x, year) - rebate(year))

x = [10000 * i for i in range(1, 1000)]
y = [year_tax(2024)(xi) / xi for xi in x]

print(year_tax(2024)(2e6) / 2e6)

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(x, y)  # Plot some data on the axes.

plt.savefig("fig.png")