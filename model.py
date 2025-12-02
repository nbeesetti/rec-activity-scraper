from tensorflow.keras.models import load_model
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pickle
import pandas as pd


BIN_INTERVAL = 10
TIME_STEPS_WINDOW = 100

activity_model_path = "rec_lstm2_model.keras"
activity_model = load_model(activity_model_path)

mod_if = open("workout_time_rf_pipeline.pkl", "rb")
model2 = pickle.load(mod_if)

feature_cols = [
    "minutes_of_day",
    "room_name_Lower Exercise Room",
    "room_name_Track Exercise Room",
    "room_name_Upper Exercise Room",
    "day_Friday",
    "day_Monday",
    "day_Saturday",
    "day_Sunday",
    "day_Thursday",
    "day_Tuesday",
    "day_Wednesday",
]


def build_row(minutes_of_day, room, day_name):
    minutes_of_day = minutes_of_day / 1440.0

    room_map = {
        "Lower": {
            "room_name_Lower Exercise Room": 1,
            "room_name_Track Exercise Room": 0,
            "room_name_Upper Exercise Room": 0,
        },
        "Track": {
            "room_name_Lower Exercise Room": 0,
            "room_name_Track Exercise Room": 1,
            "room_name_Upper Exercise Room": 0,
        },
        "Upper": {
            "room_name_Lower Exercise Room": 0,
            "room_name_Track Exercise Room": 0,
            "room_name_Upper Exercise Room": 1,
        },
    }

    weekdays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_map = {f"day_{d}": (1 if d == day_name else 0) for d in weekdays}

    row_dict = {"minutes_of_day": minutes_of_day, **room_map[room], **day_map}  # unpack

    return np.array([row_dict[col] for col in feature_cols], dtype=np.float32)


def predict_occupancy(
    model,
    day_name,
    start_min,
    end_min,
    seq_len=TIME_STEPS_WINDOW,
    rooms=["Lower", "Track", "Upper"],
):
    print("Running predict_occupancy")
    minutes_bins = list(range(start_min, end_min + 1, BIN_INTERVAL))
    results = {}

    for room in rooms:
        seq = np.array([build_row(minutes_bins[0], room, day_name)] * seq_len)

        preds = []
        for b in minutes_bins:
            pred = model.predict(seq.reshape(1, seq_len, -1), verbose=0)[0][0]
            preds.append(pred)

            next_row = build_row(b, room, day_name)
            seq = np.vstack([seq[1:], next_row])

        preds_percent = [p * 100 for p in preds]
        avg = float(np.mean(preds_percent))

        results[room] = {"minutes_bins": minutes_bins, "predictions": preds, "avg": avg}

    return results


def date_to_day_name(date):
    return date.weekday()


def time_to_minutes(time):
    return time.hour * 60 + time.minute


def model_predict_activity(day: str, st: datetime, et: datetime):
    print("Running model_predict_activity")

    results = predict_occupancy(
        activity_model, day, time_to_minutes(st), time_to_minutes(et)
    )

    cmap = plt.get_cmap("GnBu", 5)
    plt.close("all")

    for i, room in enumerate(["Lower", "Track", "Upper"]):
        preds = results[room]["predictions"]
        bins = results[room]["minutes_bins"]

        preds_percent = [p * 100 for p in preds]
        avg = float(np.mean(preds_percent))
        print(f"\t{room} avg occupancy: {avg:.2f}%")

        plt.plot(
            bins,
            preds_percent,
            marker="o",
            linestyle="-",
            label=f"{room} (avg {avg:.1f}%)",
            color=cmap(i + 2),
        )

    plt.xlabel("Time")
    plt.ylabel("Activity (%)")
    plt.title("Predicted Activity All Rooms given Time Window")

    plt.xticks(bins, [f"{b//60:02d}:{b%60:02d}" for b in bins], rotation=45)

    plt.legend()
    plt.tight_layout()

    return results, plt


##############################################


def build_workout_row(day, start_time_m, workout, occupancy):
    print("Running build_workout_row")
    row = {f: 0 for f in model2.feature_names_in_}

    row[day] = 1
    row["start_time_m"] = start_time_m
    row["pred_occupancy"] = occupancy

    for exercise, sets in workout:
        if exercise in row:
            row[exercise] = sets
        else:
            print(f"Exercise {exercise} not in feature columns")

    return pd.DataFrame([row])


def model_predict_duration(day, start: datetime, workout):
    print("Running model_predict_duration")
    start_time_m = time_to_minutes(start)

    occ = predict_occupancy(activity_model, day, start_time_m, start_time_m)
    occ = occ["Upper"]["predictions"][0] * 100
    print("occ: ", occ)

    df_input = build_workout_row(day, start_time_m, workout, occ)
    print(df_input.dtypes)
    print(df_input.iloc[0])

    prediction = model2.predict(df_input)[0]
    print("Predicted workout time (minutes):", prediction)
    return prediction
