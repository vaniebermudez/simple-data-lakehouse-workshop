from pathlib import Path
from datetime import datetime
import json
import random
import time

import click
from faker import Faker

VALID_EVENT_NAME = 'user.signup'

VALID_PLANS = ['free', 'pro', 'enterprise']
INVALID_PLANS = ['premium']

fake = Faker()


def generate_events(num_records: int = 50, error_rate: float = 0.05)-> None:
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


    data_dir = Path("data_live")
    data_dir.mkdir(exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = data_dir / f"raw_events_{current_time}.json"

    with output_path.open("w") as f:
        json.dump(events, f, indent=2)

    approx_errors = int(num_records * error_rate)
    click.secho(f"Generated {num_records} events in {output_path} ", fg="green", nl=False)
    click.secho(f"(Approx. {approx_errors} intentional errors)", fg="yellow")


@click.command()
@click.option('--batch-size', default=50, help='Number of records to generate per batch.')
@click.option('--error-rate', default=0.05, help='Probability of generating a malformed record.')
@click.option('--interval', default=5, help='Seconds to wait between generating batches.')

def main(batch_size: int, error_rate: float, interval: int) -> None:

    click.secho(f"Starting data generation: batch size={batch_size}, error rate={error_rate}, interval={interval}s", fg="blue", bold=True)
    try:
        while True:
            generate_events(num_records=batch_size, error_rate=error_rate)
            time.sleep(interval)
    except KeyboardInterrupt:
        click.secho("\nData generation interrupted by user.", fg="red", bold=True)
    

if __name__ == "__main__":
    main()
