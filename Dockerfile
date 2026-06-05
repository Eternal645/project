FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY packages packages
COPY data data
COPY sql sql
COPY main.py .
COPY tests tests

CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-t", "."]
