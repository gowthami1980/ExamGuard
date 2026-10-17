from faker import Faker
import csv
import random

fake = Faker()

event_types = [
    "face_absent",
    "face_detected",
    "tab_switched",
    "focus_loss",
    "question_answered"
]

with open("log_generator.csv", "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    # Header
    writer.writerow([
        "session_id",
        "candidate_name",
        "event_type",
        "timestamp"
    ])

    # Generate data for 10 candidates
    for i in range(10):

        session_id = f"S{i + 1:03d}"
        candidate_name = fake.name()

        # Generate multiple events for each candidate
        for j in range(10):

            event_type = random.choice(event_types)
            timestamp = fake.date_time_between(
                start_date="-1d",
                end_date="now"
            )

            writer.writerow([
                session_id,
                candidate_name,
                event_type,
                timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ])

print("Fake ExamGuard data generated successfully!")
print("Saved as: log_generator.csv")