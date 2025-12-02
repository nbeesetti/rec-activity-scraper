import gradio as gr
import matplotlib.pyplot as plt
from datetime import datetime
from model import model_predict_activity, model_predict_duration


def parse_time(t):
    return datetime.strptime(t, "%H:%M").time()


def predict_activity(day, start_time, end_time, is_same):
    print("app.py: Running predict_activity")
    try:
        s = parse_time(start_time)

        if is_same:
            e = s
        else:
            e = parse_time(end_time)

    except ValueError as e:
        return str(e), e

    res, p = model_predict_activity(day, s, e)

    if is_same:
        return f"Upper Exercise Room: {res["Upper"]["avg"]:.2f}%\nLower Exercise Room: {res["Lower"]["avg"]:.2f}%\nTrack Exercise Room: {res["Track"]["avg"]:.2f}%", None
    else:
        return None, p

################################################

PUSH = [
    ["Bench Press (Barbell)", 3],
    ["Lateral Raise (Dumbbell)", 3],
    ["Shoulder Press (Dumbbell)", 3],
    ["Triceps Extension (Dumbbell)", 3]
]

PULL = [
    ["Seated Cable Row - V Grip (Cable)", 4],
    ["Bicep Curl (Dumbbell)", 3],
    ["Lat Pulldown (Cable)", 3],
    ["Cross Body Hammer Curl", 3]
]

LEGS = [
    ["Hip Thrust (Smith Machine)", 4],
    ["Romanian Deadlift (Dumbbell)", 4],
    ["Leg Press Horizontal (Machine)", 4],
    ["Hip Abduction (Machine)", 3]
]

def add_exercise(exercise, sets, workout_display):
    if exercise and sets:
        workout_display.append([exercise, int(sets)])
    return workout_display


def clear_workout():
    return []

def load_workout(name):
    if name == "push":
        return PUSH
    elif name == "pull":
        return PULL
    elif name == "legs":
        return LEGS


def predict_duration(day, start, workout_display):
    workout = [tuple(row) for row in workout_display.to_numpy()]
    print(workout)
    st = parse_time(start)
    return model_predict_duration(day, st, workout)


with gr.Blocks() as demo:
    gr.Markdown("## Zappy Sets - Rec Center Activity + Workout Duration Prediction")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Rec Activity")
            day = gr.Dropdown(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                label="Day",
            )

            gr.Markdown("Enter Time (only from 06:00 to 23:59)")
            start_time = gr.Textbox(label="Start Time")
            end_time = gr.Textbox(label="End Time")
            is_same = gr.Checkbox(label="Same start and end time?")

            predict_activity_button = gr.Button("Predict Room Activity")
            activity_result_text = gr.Textbox(
                label="Activity Predictions at Timestep", lines=3
            )
            activity_result_plot = gr.Plot(label="Activity Predictions for Time Window")

            predict_activity_button.click(
                predict_activity,
                inputs=[day, start_time, end_time, is_same],
                outputs=[activity_result_text, activity_result_plot],
            )

        with gr.Column():
            gr.Markdown("### Workout Duration")

            day = gr.Dropdown(
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
                label="Day",
            )

            start = gr.Textbox(label="Start Time")

            exercise = gr.Dropdown(
                [
                    "Back Extension (Machine)",
                    "Front Raise (Cable)",
                    "Pull Up (Assisted)",
                    "Torso Rotation",
                    "Dumbbell Row",
                    "Rear Delt Reverse Fly (Machine)",
                    "Crunch (Machine)",
                ],
                label="Exercises",
            )

            sets = gr.Number(label="Number of Sets", precision=0)

            add_button = gr.Button("Add Exercise")
            clear_button = gr.Button("Clear List")

            gr.Markdown("#### Example Workouts")
            with gr.Row():
                push_btn = gr.Button("Push")
                pull_btn = gr.Button("Pull")
                legs_btn = gr.Button("Leg")

            workout_display = gr.Dataframe(
                headers=["Exercise", "Sets"],
                datatype=["str", "number"],
                row_count=(0, "dynamic"),
                col_count=2,
                label="Workout List (editable)"
            )

            add_button.click(
                add_exercise, inputs=[exercise, sets, workout_display], outputs=workout_display
            )
            clear_button.click(clear_workout, outputs=workout_display)
            push_btn.click(lambda: load_workout("push"), outputs=workout_display)
            pull_btn.click(lambda: load_workout("pull"), outputs=workout_display)
            legs_btn.click(lambda: load_workout("legs"), outputs=workout_display)

            predict_duration_button = gr.Button("Predict Workout Duration")

            workout_result_text = gr.Textbox(
                label="Predicted Workout Duration (minutes)", lines=3
            )

            predict_duration_button.click(
                predict_duration,
                inputs=[day, start, workout_display],
                outputs=workout_result_text,
            )

demo.launch()
