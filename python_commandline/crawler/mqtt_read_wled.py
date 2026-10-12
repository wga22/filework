#!/usr/bin/env python3
import sys
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
CLIENT_ID = "WLED-e3ed7e"

# Topics requested
TOPICS = [
    "wled/e3ed7e",  # Device topic
    "wled/wttjb",   # Group topic
]


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[+] Connected to HiveMQ Broker as {CLIENT_ID}")
        # Subscribe to all requested topics
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"[+] Subscribed to topic: {topic}")
        print("[*] Waiting for messages... Press Ctrl+C to exit.\n")
    else:
        print(f"[-] Connection failed with code {rc}")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode('utf-8', errors='ignore')}")


def main():
    # Use callback_api_version to ensure compatibility with paho-mqtt 2.x+
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
    )

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[!] Disconnecting...")
        client.disconnect()
        sys.exit(0)
    except Exception as e:
        print(f"[-] Error: {e}")


if __name__ == "__main__":
    main()