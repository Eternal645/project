FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY packages packages
COPY data data
COPY sql sql
COPY main.py .
COPY tests tests

CMD ["python", "-m", "unittest", "discover", "-s", "tests"]
