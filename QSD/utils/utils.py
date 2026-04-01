from datetime import datetime, timedelta
import random
import string

# Utility functions for wafer metadata generation
def generate_batch_id() -> str:
    """7-character alphanumeric batch ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def build_facility_name(production_site: str, diameter: int) -> str:
    """Build facility name based on production site and diameter."""
    return f"{production_site} {diameter} mm"

def build_facility_id(location_id: str, diameter: int) -> str:
    """Build facility ID based on location ID and diameter."""
    return f"{location_id}-{diameter}"

def get_location_from_facility_name(facility_name: str) -> str:
    """Extract location from facility name."""
    return facility_name.split()[0]

def generate_workroute_id() -> str:
    """Generate a workroute ID."""
    letter1 = random.choice(string.ascii_uppercase)
    digit1 = random.randint(0, 9)
    letter2 = random.choice(string.ascii_uppercase)
    number = random.randint(1000, 9999)
    return f"{letter1}{digit1}{letter2}{number}"

def generate_operation_id() -> str:
    """Generate a random operation ID."""
    return str(random.randint(1000, 9999))

def generate_equip_id() -> str:
    """Generate a random equipment ID."""
    part1 = random.randint(100, 999)
    part2 = random.randint(0, 999)
    return f"{part1}-{part2:03d}"

def generate_last_update() -> datetime:
    """Generate a dateTime object for the last update.
    Represents the timestamp of the last transaction."""
    delta_days = random.randint(0, 5)
    delta_minutes = random.randint(0, 600)
    return datetime.now() - timedelta(days=delta_days, minutes=delta_minutes)

def generate_global_route_id() -> str:
    """Generate a global route ID."""
    part1 = random.choice(string.ascii_uppercase)
    part2 = ''.join(random.choices(string.ascii_uppercase, k = 2))
    part3 = random.randint(1, 9)
    part4 = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 3))
    return f"{part1} {part2} {part3} {part4}"

def generate_thickness_raw() -> float:
    """Generate a random raw thickness for the wafer."""
    return round(random.uniform(300, 800.0), 2)

def generate_thickness_finished(thickness_raw: float) -> float:
    """Generate a finished thickness based on raw thickness."""
    return round(random.uniform(10.0, min(thickness_raw * 0.1, 30.0)), 2)

def generate_resistivity_class(dopant: str, base_material: str) -> float:
    """Generate a resistivity class based on dopant and base material."""
    if base_material == "Si":
        if dopant.upper().startswith("B"):
            value = random.uniform(1.0, 10.0) # Boron -> P-type
        else:
            value = random.uniform(0.1, 1.0) # Phosphorus -> N-type
    else:
        value = random.uniform(0.01, 0.1)  # Wide-bandgap materials like SiC or GaN
    
    return round(value, 2)

def generate_product_number() -> str:
    """Generate a random product number."""
    return str(random.randint(10_000_000, 99_999_999))

def generate_basic_type() -> str:
    """Generate a random basic type."""
    prefix = random.choice(string.ascii_uppercase)
    digits = random.randint(1000, 9999)
    suffix = random.choice(string.ascii_uppercase)
    return f"{prefix}{digits}{suffix}"

# Utility functions for wafer electrical testing generation
LOCATION_IDS = ["BKK", "DRS", "HSC", "SGP"]

def generate_wafer_test_id() -> int:
    """Generate a random wafer test ID."""
    return random.randint(1, 999)

def generate_test_flow_id() -> str:
    """Generate a random test flow ID."""
    part1 = random.choice(string.ascii_uppercase)
    part2 = random.randint(0, 9)
    part3 = random.choice(string.ascii_uppercase)
    part4 = random.randint(1000, 9999)
    return f"{part1}{part2}{part3}{part4}"

def generate_test_timestamps() -> tuple[datetime, datetime]:
    """Generate random start and end timestamps for a test run."""
    start = datetime.now() - timedelta(
        days=random.randint(0, 5),
        hours=random.randint(0, 12),
        minutes=random.randint(0, 59)
    )
    end = start + timedelta(minutes=random.randint(10, 180))  # Test duration between 10 and 180 minutes
    return start, end

def generate_facility_and_location() -> tuple[str, str]:
    """Randomly select a facility and location ID."""
    location_id = random.choice(LOCATION_IDS)
    facility_id = f"WT{location_id}"
    return facility_id, location_id

def generate_test_run_info():
    """Generate data for TestRun."""

    test_run_id = ''.join(random.choices(string.ascii_lowercase, k=3)) + str(random.randint(10, 99))

    type_map = {
        "N": "Normal",
        "E": "Electrical",
        "Q": "Qualification"
    }

    code = random.choice(list(type_map.keys()))
    test_type_id = f"{code} - {type_map[code]}"
    
    start = datetime.now() - timedelta(hours=random.randint(1, 6))
    end = start + timedelta(minutes=random.randint(5, 30))
    
    return test_run_id, test_type_id, start, end

def generate_test_equipment():
    """Generate random test equipment details."""
    probe_card = f"pc{random.randint(10000000, 99999999)}"
    tester = f"t{random.randint(100000000, 999999999)}"
    test_program = f"tp{random.randint(100000, 999999)}"
    return probe_card, tester, test_program
