import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_CSV_NAME = "rec_data.csv"
OUTPUT_CSV_NAME = "clean_rec_data.csv"


def main():
    df = pd.read_csv(INPUT_CSV_NAME)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce", utc=True
    ).dt.tz_convert("US/Pacific")

    df["date"] = df["timestamp"].dt.date
    df["time"] = df["timestamp"].dt.strftime("%H:%M")
    df["day"] = df["timestamp"].dt.day_name()

    df["minutes_of_day"] = df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
    df = df[(df["minutes_of_day"] >= 360) & (df["minutes_of_day"] <= 1440)]

    print(df.head())

    bins = np.arange(0, 1441, 10)  # [0,1440]
    df["time_bin"] = pd.cut(
        df["minutes_of_day"], bins=bins, include_lowest=True, right=False
    )

    plt.figure(figsize=(10, 5))
    plt.hist(df["minutes_of_day"], bins=bins, edgecolor="black")
    plt.title("Distribution by Time of Day")
    plt.xlabel("Minutes of Day")
    plt.ylabel("Count of Samples")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()
    # df.to_csv(OUTPUT_CSV_NAME, index=False)


if __name__ == "__main__":
    main()
