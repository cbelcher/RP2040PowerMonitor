import machine

# 1. Initialize I2C
# For ESP32: SDA=21, SCL=22 is common
# For RP2040 (Pico): SDA=8, SCL=9 is common (I2C0)
# For RP2040-Zero: SDA=0 (Orange), SCL=1 (Blue) is common (I2C0)
# Usging pin numbers for RP2040-Zero: SDA=GP8 (Orange), SCL=GP9 (Blue)
i2c = machine.I2C(0, scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)

print("Scanning I2C bus...")

# 2. Perform the scan
devices = i2c.scan()

# 3. Output results
if len(devices) == 0:
    print("No I2C devices found.")
else:
    print(f"I2C devices found: {len(devices)}")
    for device in devices:
        # Devices are returned as decimal; hex is standard for I2C
        print(f"  - Decimal: {device} | Hex: {hex(device)}")