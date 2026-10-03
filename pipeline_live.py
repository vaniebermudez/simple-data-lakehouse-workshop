import glob
import json
import logging
from typing import List, Dict, Any

import duckdb
import pandas as pd
from pydantic import ValidationError

from models.events_live import UserSignupEvent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_raw_data(file_path) -> List[Dict[str, Any]]:
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Could not find {file_path}. Please check the path.")
        return []


def validate_events(raw_events: List[Dict[str, Any]])-> List[UserSignupEvent]:
    valid_events = []
    for event in raw_events:
        try:        
            validated_event = UserSignupEvent(**event)
            valid_events.append(validated_event)
        except ValidationError as e:
            logging.warning(f"Validation failed for event {event.get('event_id', 'UNKNOWN')}: {e.errors()[0]['msg']}")

    return valid_events

def load_to_duckdb(events: List[UserSignupEvent], db_path: str = ":memory:") -> duckdb.DuckDBPyConnection:

    conn = duckdb.connect(db_path)

    raw_list = [event.model_dump() for event in events]
    
    if raw_list:
        validated_data = pd.DataFrame(raw_list) 

        conn.execute("COPY (SELECT * FROM validated_data) TO 'data_live/analytics.parquet' (FORMAT PARQUET)")
        logging.info(f"Successfully exported {len(validated_data)} records to data_live/analytics.parquet.")
    else:
        logging.warning("No valid data to load into DuckDB.")
        
    return conn


def main() -> None:
    # Get JSON files 
    file_paths = glob.glob("data_live/raw_events_*.json")

    if not file_paths:
        logging.error("No JSON Files found in the 'data_live' directory. Run generate_data.py first.")
        return 

    logging.info("Starting the data pipeline...")

    # Ingestion
    raw_data = []
    for file_path in file_paths:
        raw_data.extend(load_raw_data(file_path))

    logging.info(f"Loaded {len(raw_data)} raw events. Starting validation...")

    # Validation
    clean_events = validate_events(raw_data)
        
    logging.info("Exporting validated events to Parquet...")

    # Storage
    conn = load_to_duckdb(clean_events, db_path=":memory:")

    # Verification
    print("\n--- Analytics Sample: Signups by Plan Type ---")
    query_result = conn.execute(
        "SELECT plan_type, COUNT(*) as signup_count FROM read_parquet('data/analytics.parquet') GROUP BY plan_type ORDER BY signup_count DESC"
    ).fetchdf()
    
    print(query_result)


if __name__ == "__main__":
    main()