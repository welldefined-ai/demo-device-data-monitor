FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /simulator

RUN pip install --no-cache-dir pymodbus==3.6.9

COPY infra/simulator/modbus_tcp.py /simulator/modbus_tcp.py

EXPOSE 1502

CMD ["python", "/simulator/modbus_tcp.py"]

