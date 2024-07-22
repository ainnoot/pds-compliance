import sys
from pathlib import Path
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])

    table_df = (
        df.groupby("size")
        .agg(avg_runtime=("runtime", "mean"), std_runtime=("runtime", "std"))
        .reset_index()
    )

    for _, row in table_df.iterrows():
        size, avg_runtime, std_runtime = row
        size = int(size)
        avg_runtime = round(avg_runtime, 5)
        std_runtime = round(std_runtime, 5)
        print(f"{size} & {avg_runtime:.5f} & {std_runtime:.5f} \\\\")
