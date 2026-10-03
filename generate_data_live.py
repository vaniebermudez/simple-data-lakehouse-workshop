from pathlib import Path
from datetime import datetime
import json
import random

from faker import Faker

VALID_EVENT_NAME = 'user.signup'

VALID_PLANS = ['free', 'pro', 'enterprise']
INVALID_PLANS = ['premium']

fake = Faker()


def generate_events(num_records: int = 50, error_rate: float = 0.05 -> None):
    events = []
 
    for _ in range(num_records):
        is_error = random.random() < error_rate

        event = {
            "event_id": fake.uuid4(),
            "event_name": VALID_EVENT_NAME,
            "timestamp": fake.date_time_between(start_date="-30d", end_date="now").isoformat() + "Z",

            # Type Validation Error
            "user_id": fake.user_name() if is_error and random.random() < 0.5 else fake.random_int(min=1000, max=99999),

            # Schema Validation Error
            "plan_type": random.choice(INVALID_PLANS) if is_error and random.random() < 0.5 else random.choice(VALID_PLANS),

            # Sparse Data Simulation
            "referral_source":  None if random.random() < 0.3 else fake.url()
            }
        events.append(event)

        return events

    data_dir = Path("data_live")
    data_dir.mkdir(exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = data_dir / f"raw_events_{current_time}.json"

    with output_path.open("w") as f:
        json.dump(events, f, indent=2)




