# Use Python base image
FROM python:3.12-slim

# Set working dir
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Run your script
CMD ["python", "run_notifier.py"]
