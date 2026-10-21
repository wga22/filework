import json
import time
from pathlib import Path
import tinytuya

# Device configuration
CREDENTIALS_FILE = Path(__file__).with_name("inverter_credentials.json")
with CREDENTIALS_FILE.open(encoding="utf-8") as credentials_file:
    TUYA_CONFIG = json.load(credentials_file)["tuya_extract"]

DEVICE_ID = TUYA_CONFIG["device_id"]
DEVICE_IP = TUYA_CONFIG["device_ip"]
LOCAL_KEY = TUYA_CONFIG["local_key"]
PROTOCOL_VERSION = 3.4

# Factory baseline offset (raw Wh stored in EEPROM from burn-in)
STARTING_OFFSET_WH = 28083

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


def parse_telemetry(dps: dict) -> dict[str, int | float]:
    """Parses raw Tuya DPS integers into scaled engineering units."""
    # Voltage: DPS 20 is 0.1V per unit
    ac_volts = dps.get("20", 0) / 10.0
    
    # Current: DPS 22 is 0.001A (mA) per unit
    ac_amps = dps.get("22", 0) / 1000.0
    
    # Inverter reported power vs real calculated apparent power
    raw_power = dps.get("25", 0) / 100.0  # 2770 -> 27.7 W
    calc_watts = ac_volts * ac_amps
    
    # Lifetime energy: DPS 23 is in Wh
    raw_cumulative_wh = dps.get("23", 0)
    net_produced_wh = max(0, raw_cumulative_wh - STARTING_OFFSET_WH)
    net_produced_kwh = net_produced_wh / 1000.0
    
    temp_c = dps.get("18", 0) / 10.0
    freq_hz = dps.get("19", 0)
    dc_bus_v = dps.get("24", 0) / 1000.0 if dps.get("24", 0) > 1000 else dps.get("24", 0) / 10.0

    return {
        "ac_volts": ac_volts,
        "ac_amps": ac_amps,
        "raw_power": raw_power,
        "calc_watts": calc_watts,
        "raw_cumulative_wh": raw_cumulative_wh,
        "raw_cumulative_kwh": raw_cumulative_wh / 1000.0,
        "net_produced_wh": net_produced_wh,
        "net_produced_kwh": net_produced_kwh,
        "temp_c": temp_c,
        "freq_hz": freq_hz,
        "dc_bus_v": dc_bus_v,
    }


def print_telemetry(telemetry: dict[str, int | float]) -> None:
    print("\n================ Inverter Live Telemetry ================")
    print(f"AC Output Voltage : {telemetry['ac_volts']:.1f} V AC | Grid Freq: {telemetry['freq_hz']} Hz")
    print(f"AC Current Draw   : {telemetry['ac_amps']:.3f} A")
    print(f"Active Output     : {telemetry['calc_watts']:.1f} W (Calculated) | {telemetry['raw_power']:.1f} W (Reported)")
    print(f"DC Bus / PV Input : {telemetry['dc_bus_v']:.1f} V DC")
    print(f"Heatsink Temp     : {telemetry['temp_c']} °C")
    print("---------------------------------------------------------")
    print(f"Raw Device Total  : {telemetry['raw_cumulative_wh']} Wh ({telemetry['raw_cumulative_kwh']:.3f} kWh)")
    print(f"Net Actual Output : {telemetry['net_produced_wh']} Wh ({telemetry['net_produced_kwh']:.3f} kWh)")
    print("=========================================================\n")



def main():
    print("Fetching initial reading...")
    initial_status = device.status()
    if "dps" in initial_status:
        telemetry = parse_telemetry(initial_status["dps"])
    else:
        print(f"Error reading status: {initial_status}")
        return
    
    is_sleeping = (telemetry["freq_hz"] == 0) or (telemetry["dc_bus_v"] < 18.0)

    if is_sleeping:
        active_watts_real = 0.0
        active_watts_reported = 0.0
        display_temp = None  # Store as NULL/None in Postgres and ThingSpeak
        print("Inverter is in sleep mode (no AC output). Telemetry values will be zeroed.")
    else:
        active_watts_real = telemetry["calc_watts"]
        active_watts_reported = telemetry["raw_power"]
        display_temp = telemetry["temp_c"]
        print_telemetry(telemetry)


    # Try alternate write payloads
    #attempt_hardware_reset()



if __name__ == "__main__":
    main()