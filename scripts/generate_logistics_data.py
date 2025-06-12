import json
import random
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional, Tuple
import os
from faker import Faker
from tqdm import tqdm
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Initialize Faker with specific providers
fake = Faker()
fake.add_provider('address')
fake.add_provider('company')
fake.add_provider('date_time')
fake.add_provider('person')

class PackageStatus(Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    IN_TRANSIT = "In Transit"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    EXCEPTION = "Exception"
    RETURNED = "Returned to Sender"
    CUSTOMS_HOLD = "Customs Hold"
    DAMAGED = "Damaged"
    LOST = "Lost"

class PackageType(Enum):
    STANDARD = "Standard"
    EXPRESS = "Express"
    PRIORITY = "Priority"
    OVERNIGHT = "Overnight"
    INTERNATIONAL = "International"
    FRAGILE = "Fragile"
    REFRIGERATED = "Refrigerated"
    HAZMAT = "Hazardous Materials"

class ShippingCarrier(Enum):
    UPS = "UPS"
    FEDEX = "FedEx"
    DHL = "DHL"
    USPS = "USPS"
    AMAZON = "Amazon Logistics"

@dataclass
class Location:
    city: str
    state: str
    zip_code: str
    country: str
    latitude: float
    longitude: float
    facility_name: str
    facility_type: str

@dataclass
class PackageDimensions:
    length: float
    width: float
    height: float
    weight: float
    volume: float

@dataclass
class TrackingEvent:
    event_id: str
    timestamp: str
    status: PackageStatus
    location: Location
    description: str
    carrier: ShippingCarrier
    scan_type: str
    operator_id: str

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (Location, PackageDimensions, TrackingEvent)):
            return asdict(obj)
        return super().default(obj)

class SmartLogisticsTrackingModel:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data structures
        self.facility_types = [
            "Sorting Center", "Distribution Hub", "Local Facility",
            "International Gateway", "Customs Clearance Center"
        ]
        
        self.scan_types = [
            "Arrival Scan", "Departure Scan", "Out for Delivery Scan",
            "Delivery Scan", "Exception Scan", "Customs Scan"
        ]
        
        # Initialize status templates with more detailed scenarios
        self.status_templates = {
            PackageStatus.PENDING: [
                "Package received at origin facility",
                "Package awaiting pickup",
                "Package registered in system",
                "Package awaiting processing"
            ],
            PackageStatus.PROCESSING: [
                "Package being processed at {facility}",
                "Package undergoing customs clearance",
                "Package being prepared for shipping",
                "Package being sorted at {facility}"
            ],
            PackageStatus.IN_TRANSIT: [
                "Package in transit to next facility",
                "Package moving through network",
                "Package en route to destination",
                "Package transferred to {carrier} for delivery"
            ],
            PackageStatus.OUT_FOR_DELIVERY: [
                "Package out for delivery with {carrier}",
                "Package with delivery driver",
                "Package on final delivery route",
                "Package scheduled for delivery today"
            ],
            PackageStatus.DELIVERED: [
                "Package delivered to recipient",
                "Package successfully delivered",
                "Package delivered and signed for",
                "Package delivered to secure location"
            ],
            PackageStatus.EXCEPTION: [
                "Delivery exception - {reason}",
                "Package delayed due to {reason}",
                "Delivery attempt failed - {reason}",
                "Package requires special handling"
            ],
            PackageStatus.RETURNED: [
                "Package being returned to sender",
                "Package return process initiated",
                "Package in return transit",
                "Package returned to origin facility"
            ],
            PackageStatus.CUSTOMS_HOLD: [
                "Package held for customs inspection",
                "Package awaiting customs clearance",
                "Package requires additional documentation",
                "Package under customs review"
            ],
            PackageStatus.DAMAGED: [
                "Package damaged during transit",
                "Package condition check required",
                "Package damage reported",
                "Package requires repackaging"
            ],
            PackageStatus.LOST: [
                "Package location unknown",
                "Package tracking information unavailable",
                "Package search in progress",
                "Package investigation initiated"
            ]
        }
        
        # Exception reasons for more realistic scenarios
        self.exception_reasons = [
            "address issue", "recipient not available", "weather conditions",
            "vehicle breakdown", "traffic delay", "security check",
            "customs delay", "incorrect address", "access restricted",
            "delivery area restricted"
        ]

    def generate_location(self) -> Location:
        """Generate a realistic location with coordinates and facility information."""
        city = fake.city()
        state = fake.state()
        zip_code = fake.zipcode()
        facility_name = f"{fake.company()} {random.choice(self.facility_types)}"
        facility_type = random.choice(self.facility_types)
        
        # Generate realistic coordinates within the US
        latitude = random.uniform(24.396308, 49.384358)  # US latitude range
        longitude = random.uniform(-125.000000, -66.934570)  # US longitude range
        
        return Location(
            city=city,
            state=state,
            zip_code=zip_code,
            country="USA",
            latitude=latitude,
            longitude=longitude,
            facility_name=facility_name,
            facility_type=facility_type
        )

    def generate_dimensions(self) -> PackageDimensions:
        """Generate realistic package dimensions and calculate volume."""
        length = round(random.uniform(5, 100), 2)
        width = round(random.uniform(5, 100), 2)
        height = round(random.uniform(5, 100), 2)
        weight = round(random.uniform(0.5, 50.0), 2)
        volume = round(length * width * height, 2)
        
        return PackageDimensions(
            length=length,
            width=width,
            height=height,
            weight=weight,
            volume=volume
        )

    def generate_tracking_event(self, 
                              status: PackageStatus,
                              carrier: ShippingCarrier,
                              location: Location) -> TrackingEvent:
        """Generate a detailed tracking event."""
        event_id = str(uuid.uuid4())
        timestamp = fake.date_time_this_month()
        scan_type = random.choice(self.scan_types)
        operator_id = f"OP{fake.random_number(digits=6)}"
        
        # Generate description based on status
        template = random.choice(self.status_templates[status])
        description = template.format(
            facility=location.facility_name,
            carrier=carrier.value,
            reason=random.choice(self.exception_reasons) if status == PackageStatus.EXCEPTION else ""
        )
        
        return TrackingEvent(
            event_id=event_id,
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            status=status,
            location=location,
            description=description,
            carrier=carrier,
            scan_type=scan_type,
            operator_id=operator_id
        )

    def generate_tracking_history(self, 
                                package_type: PackageType,
                                carrier: ShippingCarrier) -> List[Dict]:
        """Generate a realistic tracking history based on package type."""
        history = []
        current_status = PackageStatus.PENDING
        current_location = self.generate_location()
        
        # Generate appropriate number of events based on package type
        num_events = {
            PackageType.STANDARD: random.randint(4, 6),
            PackageType.EXPRESS: random.randint(3, 5),
            PackageType.PRIORITY: random.randint(3, 4),
            PackageType.OVERNIGHT: random.randint(2, 3),
            PackageType.INTERNATIONAL: random.randint(6, 8),
            PackageType.FRAGILE: random.randint(4, 6),
            PackageType.REFRIGERATED: random.randint(3, 5),
            PackageType.HAZMAT: random.randint(5, 7)
        }[package_type]
        
        for _ in range(num_events):
            event = self.generate_tracking_event(current_status, carrier, current_location)
            history.append(asdict(event))
            
            # Update status and location for next event
            if current_status == PackageStatus.PENDING:
                current_status = PackageStatus.PROCESSING
            elif current_status == PackageStatus.PROCESSING:
                current_status = PackageStatus.IN_TRANSIT
            elif current_status == PackageStatus.IN_TRANSIT:
                if random.random() < 0.1:  # 10% chance of exception
                    current_status = PackageStatus.EXCEPTION
                else:
                    current_status = PackageStatus.OUT_FOR_DELIVERY
            elif current_status == PackageStatus.OUT_FOR_DELIVERY:
                if random.random() < 0.95:  # 95% chance of successful delivery
                    current_status = PackageStatus.DELIVERED
                else:
                    current_status = PackageStatus.EXCEPTION
            elif current_status == PackageStatus.EXCEPTION:
                if random.random() < 0.7:  # 70% chance of recovery
                    current_status = PackageStatus.IN_TRANSIT
                else:
                    current_status = PackageStatus.RETURNED
            
            current_location = self.generate_location()
        
        return history

    def generate_package_data(self, num_packages: int = 20000) -> List[Dict]:
        """Generate comprehensive package tracking data."""
        packages = []
        
        for _ in tqdm(range(num_packages), desc="Generating package data"):
            # Generate basic package information
            package_type = random.choice(list(PackageType))
            carrier = random.choice(list(ShippingCarrier))
            dimensions = self.generate_dimensions()
            
            # Generate tracking number based on carrier
            tracking_number = f"{carrier.value[:3]}{fake.random_number(digits=9)}"
            
            # Generate tracking history
            tracking_history = self.generate_tracking_history(package_type, carrier)
            
            # Get final status from tracking history
            final_status = tracking_history[-1]["status"]
            
            # Generate package description
            package_description = (
                f"{package_type.value} package weighing {dimensions.weight}kg, "
                f"dimensions: {dimensions.length}x{dimensions.width}x{dimensions.height}cm, "
                f"volume: {dimensions.volume}cm³"
            )
            
            package = {
                "tracking_number": tracking_number,
                "package_type": package_type.value,
                "carrier": carrier.value,
                "dimensions": asdict(dimensions),
                "origin": asdict(self.generate_location()),
                "destination": asdict(self.generate_location()),
                "tracking_history": tracking_history,
                "current_status": final_status,
                "estimated_delivery": fake.date_time_this_month().strftime("%Y-%m-%d %H:%M:%S"),
                "actual_delivery": (
                    tracking_history[-1]["timestamp"] 
                    if final_status == PackageStatus.DELIVERED.value 
                    else None
                ),
                "description": package_description,
                "special_handling": package_type in [PackageType.FRAGILE, PackageType.REFRIGERATED, PackageType.HAZMAT],
                "insurance_value": round(random.uniform(100, 5000), 2) if random.random() < 0.3 else None,
                "signature_required": random.random() < 0.4
            }
            
            packages.append(package)
        
        return packages

    def save_to_json(self, data: List[Dict], filename: str = "logistics_data.json"):
        """Save generated data to a JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        print(f"\nSaving data to {filepath}...")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, cls=EnumEncoder)
        print(f"Data saved successfully!")

    def save_to_csv(self, data: List[Dict], filename: str = "logistics_data.csv"):
        """Save generated data to a CSV file with flattened structure."""
        print(f"\nConverting data to CSV format...")
        flattened_data = []
        
        for package in tqdm(data, desc="Converting to CSV format"):
            flat_package = {
                "tracking_number": package["tracking_number"],
                "package_type": package["package_type"],
                "carrier": package["carrier"],
                "weight_kg": package["dimensions"]["weight"],
                "length_cm": package["dimensions"]["length"],
                "width_cm": package["dimensions"]["width"],
                "height_cm": package["dimensions"]["height"],
                "volume_cm3": package["dimensions"]["volume"],
                "origin_city": package["origin"]["city"],
                "origin_state": package["origin"]["state"],
                "origin_zip": package["origin"]["zip_code"],
                "destination_city": package["destination"]["city"],
                "destination_state": package["destination"]["state"],
                "destination_zip": package["destination"]["zip_code"],
                "current_status": package["current_status"],
                "estimated_delivery": package["estimated_delivery"],
                "actual_delivery": package["actual_delivery"],
                "special_handling": package["special_handling"],
                "insurance_value": package["insurance_value"],
                "signature_required": package["signature_required"],
                "description": package["description"]
            }
            flattened_data.append(flat_package)
        
        df = pd.DataFrame(flattened_data)
        filepath = os.path.join(self.data_dir, filename)
        print(f"Saving CSV data to {filepath}...")
        df.to_csv(filepath, index=False)
        print(f"CSV data saved successfully!")

def main():
    try:
        model = SmartLogisticsTrackingModel()
        num_packages = 2000
        
        print(f"Generating {num_packages} package records...")
        logistics_data = model.generate_package_data(num_packages)
        
        # Save data in both JSON and CSV formats
        model.save_to_json(logistics_data)
        model.save_to_csv(logistics_data)
        
        print("\nData generation completed successfully!")
        print(f"Generated {num_packages} package records")
        print("Files saved in the 'data' directory:")
        print("- logistics_data.json")
        print("- logistics_data.csv")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
