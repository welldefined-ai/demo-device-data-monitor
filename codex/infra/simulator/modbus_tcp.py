from __future__ import annotations

import asyncio
import logging
import os
from typing import Final

from pymodbus.datastore import (  # type: ignore[import-not-found]
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server import StartAsyncTcpServer  # type: ignore[import-not-found]


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modbus-sim")

HOST: Final[str] = os.getenv("SIM_HOST", "0.0.0.0")
PORT: Final[int] = int(os.getenv("SIM_PORT", "1502"))


async def main() -> None:
    # 100 holding registers initialized to 0
    hr_block = ModbusSequentialDataBlock(0, [0] * 100)
    # Create a full slave context (we primarily use holding registers)
    store = ModbusSlaveContext(di=None, co=None, hr=hr_block, ir=None, zero_mode=True)
    context = ModbusServerContext(slaves=store, single=True)

    async def updater() -> None:
        value = 0
        while True:
            # Write an incrementing counter to register 0
            context[0x00].setValues(3, 0, [value])  # 3 = holding registers function code
            value = (value + 1) % 10000
            await asyncio.sleep(1.0)

    logger.info("Starting Modbus TCP simulator at %s:%s", HOST, PORT)
    await asyncio.gather(
        StartAsyncTcpServer(context=context, address=(HOST, PORT)),
        updater(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

