import json
import uuid
from datetime import datetime, timezone

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from sqlmodel import Field, Session, SQLModel, create_engine

# Initialize SQLite database
DB_PATH = 'parking_data.db'
engine = create_engine(f"sqlite:///{DB_PATH}")


class ParkingData(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    timestamp: str
    lot_name: str
    is_full: bool
    url: str
    image_src: str


def initialize_db():
    """
    Create the SQLite database and table if they don't exist.
    """
    SQLModel.metadata.create_all(engine)


# Constants
TARGET_URLS = [
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=123",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=3",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=122",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=45",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=94",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=10",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=4",
    "https://www.ahuzot.co.il/Parking/ParkingDetails/?ID=42"
]
REQUEST_TIMEOUT = 5  # seconds


def put_parking_data(data: ParkingData):
    """
    Store parking data in SQLite database.
    """
    try:
        with Session(engine) as session:
            session.add(data)
            session.commit()
    except Exception as e:
        print(f"Error putting item in SQLite: {str(e)}")


def query_lots():
    """
    AWS Lambda handler function
    """
    all_data = []
    try:
        for url in TARGET_URLS:
            # Add timeout to request
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, features="html.parser")

            # Extract parking data - optimize selectors
            img_tag = soup.select_one(".ParkingDetailsTable td img")
            img_src = img_tag.get('src', '') if img_tag else ''
            is_full = 'male.png' in img_src
            lot_name = soup.select_one(".ParkingTableHeader").text.strip()

            # Prepare data entry
            data = ParkingData(
                uuid=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat().replace(
                    '+00:00', 'Z'),
                lot_name=lot_name,
                is_full=is_full,
                url=url,
                image_src=img_src,
            )
            # Append data to the list
            all_data.append(data.model_dump_json())

            # Store in SQLite
            put_parking_data(data)

        return {
            'statusCode':
            200,
            'body':
            json.dumps({
                'success': True,
                'message': 'Query completed successfully',
                'data': all_data
            })
        }

    except requests.Timeout:
        print("Request timed out while fetching parking data")
        return {
            'statusCode': 504,
            'body': json.dumps({
                'success': False,
                'error': 'Request timed out'
            })
        }
    except Exception as e:
        print(f"Error processing parking data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


if __name__ == "__main__":
    # Initialize the database
    initialize_db()

    query_lots()
    # Schedule the lambda_handler function every 10 minutes
    scheduler = BlockingScheduler()
    scheduler.add_job(query_lots, 'interval', minutes=10)

    try:
        print("Scheduler started. Running lambda_handler every 10 minutes.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
        scheduler.shutdown()
