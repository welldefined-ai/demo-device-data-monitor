FROM python:3.11-slim

WORKDIR /app

# Install pymodbus
RUN pip install --no-cache-dir pymodbus==3.7.4

# Copy simulator script
COPY scripts/modbus_simulator.py /app/simulator.py

# Expose Modbus TCP port
EXPOSE 5020

# Run simulator
CMD ["python", "simulator.py"]
