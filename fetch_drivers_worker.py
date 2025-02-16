from database.db import get_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from services.token_manager import get_access_token
from models.drivers import Base, Driver
import time
import requests
from datetime import datetime
# import pytz

COMPANY_ID = 129914

FLEET_DRIVERS_URL = "https://node.bolt.eu/fleet-integration-gateway/fleetIntegration/v1/getDrivers"

def create_drivers_table_if_not_exists():
    engine = get_engine()
    inspector = inspect(engine)
    if not inspector.has_table("drivers"):
        Base.metadata.create_all(engine)
        print("Table 'drivers' created successfully.")
    else:
        print("Table 'drivers' already exists.")

def fetch_and_store_drivers():
    token = get_access_token()
    url = FLEET_DRIVERS_URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "offset": 1,
        "limit": 100,
        "company_id": COMPANY_ID,
        "start_ts": int(time.time() - 5000),
        "end_ts": int(time.time())
    }

    response = requests.post(url, headers=headers, json=payload)
    drivers = response.json().get("data", {}).get("drivers", [])
    
    if not drivers:
        print("No drivers found.")
        return
    
    engine = get_engine()
    with engine.connect() as connection:
        for driver in drivers:
            stmt = text("""
                INSERT INTO drivers (
                    driver_uuid, partner_uuid, first_name, last_name, 
                    email, phone, state, has_cash_payment, inactivity_reason
                ) 
                VALUES (
                    :driver_uuid, :partner_uuid, :first_name, :last_name,
                    :email, :phone, :state, :has_cash_payment, :inactivity_reason
                )
                ON DUPLICATE KEY UPDATE
                    partner_uuid = VALUES(partner_uuid),
                    first_name = VALUES(first_name),
                    last_name = VALUES(last_name),
                    email = VALUES(email),
                    phone = VALUES(phone),
                    state = VALUES(state),
                    has_cash_payment = VALUES(has_cash_payment),
                    inactivity_reason = VALUES(inactivity_reason)
            """)
            
            connection.execute(stmt, {
                'driver_uuid': driver.get('driver_uuid'),
                'partner_uuid': driver.get('partner_uuid'),
                'first_name': driver.get('first_name'),
                'last_name': driver.get('last_name'),
                'email': driver.get('email'),
                'phone': driver.get('phone'),
                'state': driver.get('state'),
                'has_cash_payment': driver.get('has_cash_payment', False),
                'inactivity_reason': driver.get('inactivity_reason')
            })
        connection.commit()

    

if __name__ == "__main__":
    create_drivers_table_if_not_exists()
    fetch_and_store_drivers()