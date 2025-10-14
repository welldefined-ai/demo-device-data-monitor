#!/usr/bin/env python3
"""Simple Modbus TCP simulator for testing."""

import random
import time
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartTcpServer

# Create a datastore with initial values
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
    hr=ModbusSequentialDataBlock(0, [0] * 100),  # Holding Registers
    ir=ModbusSequentialDataBlock(0, [0] * 100),  # Input Registers
)

context = ModbusServerContext(slaves=store, single=True)


def update_values(context):
    """Update register values to simulate changing sensor data."""
    while True:
        # Generate random temperature value (20-30°C) for register 40001 (address 0)
        # Convert to 16-bit integer scaled by 10 (e.g., 25.3°C -> 253)
        temp_value = int((20 + random.random() * 10) * 10)

        # Write to holding register 0 (Modbus address 40001)
        context[0].setValues(3, 0, [temp_value])

        time.sleep(5)  # Update every 5 seconds


if __name__ == "__main__":
    print("Starting Modbus TCP simulator on port 5020...")
    print("Register 40001 (address 0): Simulated temperature (20-30°C)")

    # Start value updater in background
    import threading
    updater = threading.Thread(target=update_values, args=(context,), daemon=True)
    updater.start()

    # Start Modbus TCP server
    StartTcpServer(context=context, address=("0.0.0.0", 5020))
