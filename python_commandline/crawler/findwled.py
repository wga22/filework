#!/usr/bin/env python3
import concurrent.futures
import requests

SUBNET = "192.168.86"
TIMEOUT = 1.5  # Seconds to wait per request
MAX_THREADS = 50


def check_wled(ip):
    url = f"http://{ip}/json/info"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            # Verify it's a WLED device via its JSON keys
            if "brand" in data and data["brand"] == "WLED":
                return ip, data.get("name", "Unknown WLED Device")
            elif "ver" in data:  # Fallback check for older/custom versions
                return ip, "WLED Device"
    except (requests.exceptions.RequestException, ValueError):
        pass
    return None


def main():
    print(f"Scanning subnet {SUBNET}.0/24 for WLED devices...")
    ips = [f"{SUBNET}.{i}" for i in range(1, 255)]

    found_devices = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_THREADS
    ) as executor:
        # Map the check_wled function to all generated IPs
        results = executor.map(check_wled, ips)

        for result in results:
            if result:
                found_devices.append(result)
                print(f"[+] Found WLED: {result[0]} ({result[1]})")

    print("\n--- Scan Complete ---")
    if not found_devices:
        print("No WLED devices discovered.")
    else:
        print(f"Total WLED devices found: {len(found_devices)}")


if __name__ == "__main__":
    main()