FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential gcc python3-dev libatlas-base-dev libblas-dev liblapack-dev libffi-dev libssl-dev git && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install --upgrade pip wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"
COPY . .
CMD ["python", "main.py"]
