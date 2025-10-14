#!/usr/bin/env python3
"""Simple Modbus TCP simulator for testing."""

import random
import time
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartTcpServer

# Create a datastore with initial values
# ModbusSequentialDataBlock(starting_address, values)
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 1000),  # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0] * 1000),  # Coils
    hr=ModbusSequentialDataBlock(0, [0] * 10000),  # Holding Registers 0-9999
    ir=ModbusSequentialDataBlock(0, [0] * 1000),  # Input Registers
)

context = ModbusServerContext(slaves=store, single=True)


def update_values(context):
    """Update register values to simulate changing sensor data."""
    while True:
        # Simulate 4 different sensors
        # Register 0 (40001): Temperature 20-30°C
        temp_value = int((20 + random.random() * 10) * 10)
        context[0].setValues(3, 0, [temp_value])

        # Register 1 (40002): Pressure 0-100 bar
        pressure_value = int(random.random() * 100 * 10)
        context[0].setValues(3, 1, [pressure_value])

        # Register 2 (40003): RPM 1000-3000
        rpm_value = int(1000 + random.random() * 2000)
        context[0].setValues(3, 2, [rpm_value])

        # Register 3 (40004): Humidity 30-70%
        humidity_value = int((30 + random.random() * 40) * 10)
        context[0].setValues(3, 3, [humidity_value])

        time.sleep(5)  # Update every 5 seconds


if __name__ == "__main__":
    print("Starting Modbus TCP simulator on port 5020...")
    print("Available registers:")
    print("  40001 (address 0): Temperature 20-30°C")
    print("  40002 (address 1): Pressure 0-100 bar")
    print("  40003 (address 2): RPM 1000-3000")
    print("  40004 (address 3): Humidity 30-70%")

    # Start value updater in background
    import threading
    updater = threading.Thread(target=update_values, args=(context,), daemon=True)
    updater.start()

    # Start Modbus TCP server
    StartTcpServer(context=context, address=("0.0.0.0", 5020))
