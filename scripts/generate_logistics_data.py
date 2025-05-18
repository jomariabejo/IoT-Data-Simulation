import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

num_records = 100
data = []

for _ in range(num_records):
    # Generate timestamps
    timestamp = datetime.now() - timedelta(minutes=np.random.randint(0, 1440))
    pickup_datetime = timestamp - timedelta(hours=np.random.randint(1, 6))
    estimated_arrival = timestamp + timedelta(hours=np.random.randint(24, 49))
    actual_arrival = estimated_arrival + timedelta(minutes=np.random.randint(-60, 120))

    # Simulated IoT sensor readings
    temperature_c = round(np.random.uniform(2.0, 8.0), 2)
    humidity_percent = round(np.random.uniform(50.0, 80.0), 2)

    # Alert logic using native bool
    temperature_alert = bool(temperature_c < 2.5 or temperature_c > 7.5)
    humidity_alert = bool(humidity_percent < 55 or humidity_percent > 75)

    # Delay detection
    logistics_delay = actual_arrival > estimated_arrival
    logistics_delay_reason = (
        np.random.choice(["Heavy Traffic", "Flooded Roads", "Mechanical Issue", "Checkpoint Delay"])
        if logistics_delay else "None"
    )

    record = {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "estimated_arrival": estimated_arrival.strftime("%Y-%m-%d %H:%M:%S"),
        "actual_arrival": actual_arrival.strftime("%Y-%m-%d %H:%M:%S"),
        "shipment_id": f"SHIP{np.random.randint(1000, 9999)}",
        "order_id": f"ORD{np.random.randint(100000, 999999)}",
        "origin_hub": np.random.choice(["Cebu Hub", "QC Hub", "Laguna Warehouse", "Davao Center"]),
        "destination_city": np.random.choice(["Taguig", "Cebu City", "Baguio", "Davao", "Naga", "Iloilo"]),
        "status": np.random.choice(["In Transit", "Delivered", "Delayed", "Out for Delivery"]),
        "temperature_c": temperature_c,
        "humidity_percent": humidity_percent,
        "temperature_alert": temperature_alert,
        "humidity_alert": humidity_alert,
        "package_type": np.random.choice(["Pouch", "Small Box", "Medium Box", "Large Box", "Envelope", "Frozen Pack"]),
        "logistics_delay": bool(logistics_delay),
        "logistics_delay_reason": logistics_delay_reason,
        "delivery_rating": random.choice([None, 3, 4, 5]),
        "customer_notified": bool(np.random.choice([True, False]))
    }

    data.append(record)

# Convert to DataFrame
df = pd.DataFrame(data)

df.to_csv("../data/logistics_data.csv", index=False)

with open("../data/logistics_data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

df.head()