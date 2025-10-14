"""Modbus client wrapper for reading device data."""

import logging
import struct
from typing import Any

from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger(__name__)


class ModbusClientWrapper:
    """Wrapper for Modbus TCP and RTU clients."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Modbus client based on configuration.

        Args:
            config: Modbus configuration dictionary with keys:
                - type: 'tcp' or 'rtu'
                - host: TCP host address (for TCP)
                - port: TCP port (for TCP)
                - serial_port: Serial port path (for RTU)
                - baudrate: Serial baudrate (for RTU)
                - register: Register address to read
                - data_type: Data type to parse ('int16', 'uint16', 'int32', 'uint32', 'float32')
        """
        self.config = config
        self.client: ModbusTcpClient | ModbusSerialClient | None = None
        self.register = config["register"]
        self.data_type = config["data_type"]

        if config["type"] == "tcp":
            self.client = ModbusTcpClient(
                host=config.get("host", "localhost"),
                port=config.get("port", 502),
                timeout=5,
            )
        elif config["type"] == "rtu":
            self.client = ModbusSerialClient(
                port=config.get("serial_port", "/dev/ttyUSB0"),
                baudrate=config.get("baudrate", 9600),
                timeout=5,
            )
        else:
            raise ValueError(f"Unsupported Modbus type: {config['type']}")

    def connect(self) -> bool:
        """
        Connect to the Modbus device.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            return False

        try:
            return self.client.connect()
        except Exception as e:
            logger.error(f"Modbus connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        if self.client:
            self.client.close()  # type: ignore[no-untyped-call]

    def read_value(self) -> float | None:
        """
        Read a value from the configured Modbus register.

        Returns:
            Parsed float value, or None if read failed

        Raises:
            ModbusException: If Modbus communication fails
        """
        if not self.client:
            raise ModbusException("Modbus client not initialized")  # type: ignore[no-untyped-call]

        try:
            # Read holding registers (function code 3)
            # Number of registers depends on data type
            register_count = self._get_register_count()

            result = self.client.read_holding_registers(
                address=self.register,
                count=register_count,
            )

            if result.isError():
                raise ModbusException(f"Modbus read error: {result}")  # type: ignore[no-untyped-call]

            # Parse the register values based on data type
            raw_value = self._parse_registers(result.registers)
            return raw_value

        except Exception as e:
            logger.error(f"Failed to read Modbus register {self.register}: {e}")
            raise ModbusException(str(e)) from e  # type: ignore[no-untyped-call]

    def _get_register_count(self) -> int:
        """Get number of registers to read based on data type."""
        if self.data_type in ["int16", "uint16"]:
            return 1
        elif self.data_type in ["int32", "uint32", "float32"]:
            return 2
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")

    def _parse_registers(self, registers: list[int]) -> float:
        """
        Parse register values based on configured data type.

        Args:
            registers: List of register values

        Returns:
            Parsed float value
        """
        if self.data_type == "int16":
            # Single register, signed 16-bit integer
            value = registers[0]
            if value > 32767:
                value -= 65536
            return float(value)

        elif self.data_type == "uint16":
            # Single register, unsigned 16-bit integer
            return float(registers[0])

        elif self.data_type == "int32":
            # Two registers, signed 32-bit integer (big-endian)
            bytes_data = struct.pack(">HH", registers[0], registers[1])
            value = struct.unpack(">i", bytes_data)[0]
            return float(value)

        elif self.data_type == "uint32":
            # Two registers, unsigned 32-bit integer (big-endian)
            bytes_data = struct.pack(">HH", registers[0], registers[1])
            value = struct.unpack(">I", bytes_data)[0]
            return float(value)

        elif self.data_type == "float32":
            # Two registers, 32-bit float (big-endian)
            bytes_data = struct.pack(">HH", registers[0], registers[1])
            value = struct.unpack(">f", bytes_data)[0]
            return float(value)

        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")

    def __enter__(self) -> "ModbusClientWrapper":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()
