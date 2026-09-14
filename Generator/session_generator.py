import csv
import random
from datetime import datetime, timedelta

candidates = [
    "Arun",
    "Priya",
    "Rahul",
    "Anu",
    "Kiran",
    "Sneha",
    "Ravi",
    "Kavya",
    "Ajay",
    "Meena"
]

events = [
    "face_absent",
    "face_detected",
    "tab_switched",
    "focus_loss",
    "question_answered"
]

data = []

for i in range(10):

    session_id = "SESSION_" + str(i + 1)

    candidate = candidates[i]

    time = datetime.now()

    for j in range(20):

        event = random.choice(events)

        time = time + timedelta(seconds=random.randint(30, 180))

        data.append([
            session_id,
            candidate,
            event,
            time.strftime("%Y-%m-%d %H:%M:%S")
        ])


with open("log_generter.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "session_id",
        "candidate_name",
        "event_type",
        "timestamp"
    ])

    writer.writerows(data)

print("CSV file created successfully!")

