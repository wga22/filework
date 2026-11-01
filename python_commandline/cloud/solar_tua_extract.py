import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import psycopg
import tinytuya

# Device configuration
CREDENTIALS_FILE = Path(__file__).with_name("inverter_credentials.json")
with CREDENTIALS_FILE.open(encoding="utf-8") as credentials_file:
    CREDENTIALS = json.load(credentials_file)

TUYA_CONFIG = CREDENTIALS["tuya_extract"]
POSTGRES_CONFIG = CREDENTIALS["postgres"]
THINGSPEAK_CONFIG = CREDENTIALS["thingspeak"]
THINGSPEAK_CHANNEL_ID = 3544921

DEVICE_ID = TUYA_CONFIG["device_id"]
DEVICE_IP = TUYA_CONFIG["device_ip"]
LOCAL_KEY = TUYA_CONFIG["local_key"]
PROTOCOL_VERSION = 3.4

device = tinytuya.OutletDevice(
    dev_id=DEVICE_ID, 
    address=DEVICE_IP, 
    local_key=LOCAL_KEY, 
    version=PROTOCOL_VERSION
)
device.set_socketPersistent(True)

def attempt_hardware_reset():
    """Attempts standard alternate Tuya reset formats for write-protected registers."""
    print("--- Testing Reset Command Formats ---")
    
    # Test 1: Boolean True
    res1 = device.set_value(17, True)
    print(f"Payload {{17: True}} -> {res1}")
    time.sleep(1)

    # Test 2: Integer 0
    res2 = device.set_value(17, 0)
    print(f"Payload {{17: 0}} -> {res2}")
    time.sleep(1)

    # Test 3: Direct zero-out of DPS 23
    res3 = device.set_value(23, 0)
    print(f"Payload {{23: 0}} -> {res3}")
    # Re-check status
    updated_status = device.status()
    if "dps" in updated_status:
        current_23 = updated_status["dps"].get("23")
        if current_23 == 0:
            print("[SUCCESS] Hardware counter reset to 0.")
        else:
            print(f"[INFO] Hardware counter retained {current_23}. Net calculation offset active.")
        print_telemetry(parse_telemetry(updated_status["dps"]))


def parse_telemetry(dps: dict) -> dict[str, int | float | bool | None]:
    """Parses raw Tuya DPS integers into scaled engineering units."""
    # DPS 1: Main inverter state switch
    is_switch_on = bool(dps.get("1", False))

    # DPS 20: AC Grid Voltage (0.1V per unit -> e.g., 1227 = 122.7 V)
    ac_volts = round(dps.get("20", 0) / 10.0, 1)

    # DPS 18: AC Output Current (1 mA per unit -> e.g., 582 = 0.582 A)
    ac_amps = round(dps.get("18", 0) / 1000.0, 3)

    # DPS 19: Active Grid-Injected Power (0.1W per unit -> e.g., 637 = 63.7 W)
    power_w = round(dps.get("19", 0) / 10.0, 1)

    # Apparent Power (VA = V * A)
    apparent_power_va = round(ac_volts * ac_amps, 1)

    # Power Factor calculation (Active Power / Apparent Power)
    power_factor = (
        round(min(1.0, power_w / apparent_power_va), 2)
        if apparent_power_va > 0
        else 0.0
    )

    # Operational status: active if switch is enabled and reporting current/power
    is_active = is_switch_on and (power_w > 0.0 or ac_amps > 0.05)

    return {
        "is_active": is_active,
        "ac_volts": ac_volts,
        "ac_amps": ac_amps,
        "power_w": power_w,
        "apparent_power_va": apparent_power_va,
        "power_factor": power_factor,
        "fault_code": int(dps.get("9", 0)),
        "dps": dps,  # Include raw DPS for reference
    }


def print_telemetry(telemetry: dict[str, int | float | bool]) -> None:
    print("\n================ Inverter Live Telemetry ================")
    print(f"Inverter Active   : {telemetry['is_active']}")
    print(f"AC Output Voltage : {telemetry['ac_volts']:.1f} V AC")
    print(f"AC Current Draw   : {telemetry['ac_amps']:.3f} A")
    print(f"Active Power      : {telemetry['power_w']:.1f} W")
    print(f"Apparent Power    : {telemetry['apparent_power_va']:.1f} VA")
    print(f"Power Factor      : {telemetry['power_factor']:.2f}")
    print("---------------------------------------------------------")
    if "raw_cumulative_wh" in telemetry and "net_produced_wh" in telemetry:
        print(f"Interval Energy   : {telemetry['raw_cumulative_wh'] / 1000.0:.3f} kWh")
        print(f"Net Actual Output : {telemetry['net_produced_wh'] / 1000.0:.3f} kWh")
    print(f"Fault Code        : {telemetry['fault_code']}")
    print("=========================================================\n")



def write_telemetry_toDB(telemetry: dict[str, int | float | bool]) -> int:
    """Insert one telemetry row and return its generated ID."""
    with psycopg.connect(
        host=POSTGRES_CONFIG["host"],
        port=POSTGRES_CONFIG["port"],
        dbname=POSTGRES_CONFIG["database"],
        user=POSTGRES_CONFIG["username"],
        password=POSTGRES_CONFIG["password"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT CURRENT_TIMESTAMP")
            recorded_at = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT recorded_at, power_reported_w
                FROM tesla.inverter_telemetry
                WHERE device_id = %s
                  AND recorded_at >= date_trunc('day', %s::timestamptz)
                  AND recorded_at < date_trunc('day', %s::timestamptz) + INTERVAL '1 day'
                ORDER BY recorded_at DESC, id DESC
                LIMIT 1
                """,
                (DEVICE_ID, recorded_at, recorded_at),
            )
            previous_reading = cursor.fetchone()
            if previous_reading is None:
                previous_power_w = 0.0
                elapsed_hours = 1.0
            else:
                previous_at, previous_power_w = previous_reading
                previous_power_w = float(previous_power_w)
                elapsed_hours = (recorded_at - previous_at).total_seconds() / 3600.0

            interval_wh = max(
                0,
                round(
                    ((previous_power_w + telemetry["power_w"]) / 2.0)
                    * elapsed_hours
                ),
            )
            cursor.execute(
                """
                SELECT COALESCE(SUM(raw_cumulative_wh), 0)
                FROM tesla.inverter_telemetry
                WHERE device_id = %s
                """,
                (DEVICE_ID,),
            )
            net_produced_wh = int(cursor.fetchone()[0]) + interval_wh
            telemetry["raw_cumulative_wh"] = interval_wh
            telemetry["net_produced_wh"] = net_produced_wh
            cursor.execute(
                """
                INSERT INTO tesla.inverter_telemetry (
                    recorded_at, device_id, is_active, fault_code, ac_voltage_v,
                    ac_current_a, power_reported_w, apparent_power_va,
                    power_factor, raw_cumulative_wh, raw_dps, net_produced_wh
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    recorded_at,
                    DEVICE_ID,
                    telemetry["is_active"],
                    telemetry["fault_code"],
                    telemetry["ac_volts"],
                    telemetry["ac_amps"],
                    telemetry["power_w"],
                    telemetry["apparent_power_va"],
                    telemetry["power_factor"],
                    interval_wh,
                    json.dumps(telemetry["dps"]),
                    net_produced_wh,
                ),
            )
            record_id = cursor.fetchone()[0]
    return record_id


def write_telemetry_to_thingspeak(telemetry: dict[str, int | float | bool]) -> int:
    """Send one telemetry update and return its ThingSpeak entry ID."""
    fields = {
        "api_key": THINGSPEAK_CONFIG["write_api_key"],
        "field1": int(telemetry["is_active"]),
        "field2": telemetry["ac_volts"],
        "field3": telemetry["ac_amps"],
        "field4": telemetry["power_w"],
        "field5": telemetry["power_factor"],
        "field6": telemetry["raw_cumulative_wh"],
        "field7": telemetry["net_produced_wh"],
        "field8": telemetry["fault_code"],
    }

    request = Request(
        "https://api.thingspeak.com/update.json",
        data=urlencode(fields).encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        result = json.load(response)

    if result.get("channel_id") != THINGSPEAK_CHANNEL_ID or not result.get("entry_id"):
        raise RuntimeError(
            f"ThingSpeak update failed or used the wrong channel: {result}"
        )
    return result["entry_id"]


def main():
    print("Fetching initial reading...")
    initial_status = device.status()
    if "dps" in initial_status:
        telemetry = parse_telemetry(initial_status["dps"])
    else:
        print(f"Error reading status: {initial_status}")
        return
    
    if not telemetry["is_active"]:
        print("Inverter is in sleep mode (no AC output). Telemetry values will be zeroed.")
    else:
        record_id = write_telemetry_toDB(telemetry)
        print_telemetry(telemetry)
        print(f"Saved telemetry row {record_id} to PostgreSQL.")
        entry_id = write_telemetry_to_thingspeak(telemetry)
        print(f"Saved telemetry entry {entry_id} to ThingSpeak channel {THINGSPEAK_CHANNEL_ID}.")

    # Try alternate write payloads
    #attempt_hardware_reset()



if __name__ == "__main__":
    main()