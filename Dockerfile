FROM python:3.10-slim

# Install system dependencies needed for SSL and MongoDB
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
