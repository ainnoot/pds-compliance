import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
        'font.weight': 'bold',
    'text.usetex': True,
    'pgf.rcfonts': False,
    'font.size': 20
})


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    print(df.head())

    # Create the line plot
    plt.figure(figsize=(6, 6))
    ax = sns.lineplot(
        data=df,
        x="size",
        y="runtime",
        estimator="mean",
        marker="o",
        errorbar=("ci", 95),
    )

    # Add titles and labels
    # plt.title('Line Plot of CSV Data')
    plt.xlabel("\# Effective Constraints")
    plt.ylabel("Time (s)")
    ax.set_yscale("log")
    plt.grid(True)

    # Show the plot
    plt.savefig('plot.pdf')

